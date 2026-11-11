"""Manually publish reviewed campaign text. Python 3.11+, no dependencies."""

import base64
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STATE_BRANCH = "publicity-state"
CHANNELS = ("bluesky", "slack")


class Failure(Exception):
    """Safe, credential-free diagnostic for the operator."""


def request(url, payload=None, token=None, method=None):
    headers = {"User-Agent": "SQLFluff-publicity", "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload).encode()
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    # Never retry a POST automatically: the server may have accepted it.
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


class Ledger:
    """Receipts live on a separate branch, not in deployable website content."""

    def __init__(self):
        self.base = "https://api.github.com/repos/" + os.environ["GITHUB_REPOSITORY"]
        self.token = os.environ["GITHUB_TOKEN"]

    def api(self, path, payload=None, method=None):
        return request(self.base + path, payload, self.token, method)

    def exists(self):
        try:
            self.api("/git/ref/heads/" + STATE_BRANCH)
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return False
            raise

    def ensure(self):
        if not self.exists():
            self.api(
                "/git/refs",
                {"ref": "refs/heads/" + STATE_BRANCH, "sha": os.environ["GITHUB_SHA"]},
            )

    def read(self, campaign, channel):
        if not self.exists():
            return None
        try:
            value = self.api(
                f"/contents/publicity/receipts/{campaign}/{channel}.json?ref={STATE_BRANCH}"
            )
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise
        record = json.loads(base64.b64decode(value["content"]))
        record["_sha"] = value["sha"]
        return record

    def write(self, campaign, channel, record, previous):
        data = {
            "branch": STATE_BRANCH,
            "message": f"publicity: {campaign} {channel} {record['status']}",
            "content": base64.b64encode(json.dumps(record, indent=2).encode()).decode(),
        }
        if previous:
            data["sha"] = previous["_sha"]
        self.api(f"/contents/publicity/receipts/{campaign}/{channel}.json", data, "PUT")
        return self.read(campaign, channel)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.noindex = False
        self.h1 = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name") == "robots":
            self.noindex |= "noindex" in attrs.get("content", "").lower()
        if tag == "h1":
            self.h1 = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.h1 = False

    def handle_data(self, data):
        if self.h1:
            self.title += data


def load_campaign(slug, channels):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise Failure("Use the campaign filename without .toml.")
    data = tomllib.loads(
        (ROOT / "publicity/campaigns" / (slug + ".toml")).read_text(encoding="utf-8")
    )
    if data.get("id") != slug or data.get("status") != "ready":
        raise Failure("Campaign must have a matching id and status = ready.")
    path = data.get("article", "")
    if not re.fullmatch(r"/updates/[a-z0-9-]+/", path):
        raise Failure("Article must be a local /updates/<slug>/ path.")
    source = ROOT / "content" / path.strip("/") / "index.md"
    front = source.read_text(encoding="utf-8").split("---", 2)[1]
    if re.search(r"^draft:\s*true\s*$", front, re.M | re.I):
        raise Failure("The article is still a draft.")
    date = re.search(r"^date:\s*(.+)$", front, re.M)
    if not date:
        raise Failure("Article needs a publication date.")
    date = dt.datetime.fromisoformat(date[1].strip(" '\"").replace("Z", "+00:00"))
    if date.tzinfo is None:
        date = date.replace(tzinfo=dt.timezone.utc)
    if date > dt.datetime.now(dt.timezone.utc):
        raise Failure("Article publication date is in the future.")
    title = re.search(r"^title:\s*(.+)$", front, re.M)[1].strip()
    if title.startswith('"'):
        title = json.loads(title)
    elif title.startswith("'"):
        title = title[1:-1].replace("''", "'")
    data["title"] = title
    data["url"] = "https://sqlfluff.com" + path
    for channel in channels:
        text = data.get("copy", {}).get(channel, "").strip()
        if not text or data["url"] not in text:
            raise Failure(f"{channel}: copy must include the article URL.")
        if channel == "bluesky" and (len(text) > 300 or len(text.encode()) > 3000):
            raise Failure("Bluesky copy exceeds the conservative 300-character limit.")
        if channel == "slack" and len(text) > 4000:
            raise Failure("Keep Slack copy below 4000 characters.")
        data["copy"][channel] = text
    return data


def check_live(campaign):
    req = urllib.request.Request(
        campaign["url"], headers={"User-Agent": "SQLFluff-publicity"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        url = urllib.parse.urlsplit(response.url)
        if url.scheme != "https" or url.netloc not in (
            "sqlfluff.com",
            "www.sqlfluff.com",
        ):
            raise Failure("Article redirected away from the production site.")
        if (
            url.path != campaign["article"]
            or response.headers.get_content_type() != "text/html"
        ):
            raise Failure("Article URL did not return the expected HTML page.")
        html = response.read(2_000_000).decode("utf-8")
    page = Page()
    page.feed(html)
    if (
        page.noindex
        or page.canonical != campaign["url"]
        or page.title.strip() != campaign["title"]
    ):
        raise Failure(
            "Live title/canonical/indexing check failed; wait for the production deploy."
        )


def credentials(channels):
    required = {
        "bluesky": ("BLUESKY_IDENTIFIER", "BLUESKY_APP_PASSWORD"),
        "slack": ("SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID"),
    }
    for channel in channels:
        for name in required[channel]:
            if not os.environ.get(name):
                raise Failure("Missing configuration: " + name)
    if "slack" in channels and not re.fullmatch(
        r"[CG][A-Z0-9]+", os.environ["SLACK_CHANNEL_ID"]
    ):
        raise Failure("Use Slack's channel ID, not a channel name.")


def post_bluesky(text):
    base = "https://bsky.social/xrpc/"
    session = request(
        base + "com.atproto.server.createSession",
        {
            "identifier": os.environ["BLUESKY_IDENTIFIER"],
            "password": os.environ["BLUESKY_APP_PASSWORD"],
        },
    )
    facets = []
    for match in re.finditer(r"https://[^\s]+", text):
        facets.append(
            {
                "index": {
                    "byteStart": len(text[: match.start()].encode()),
                    "byteEnd": len(text[: match.end()].encode()),
                },
                "features": [
                    {"$type": "app.bsky.richtext.facet#link", "uri": match[0]}
                ],
            }
        )
    result = request(
        base + "com.atproto.repo.createRecord",
        {
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,
                "facets": facets,
                "langs": ["en"],
                "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        },
        session["accessJwt"],
    )
    uri = result["uri"]
    return {
        "uri": uri,
        "url": "https://bsky.app/profile/"
        + session["did"]
        + "/post/"
        + uri.rsplit("/", 1)[1],
    }


def post_slack(text):
    result = request(
        "https://slack.com/api/chat.postMessage",
        {
            "channel": os.environ["SLACK_CHANNEL_ID"],
            "text": text,
            "mrkdwn": False,
            "parse": "none",
            "unfurl_links": False,
            "unfurl_media": False,
        },
        os.environ["SLACK_BOT_TOKEN"],
    )
    if not result.get("ok"):
        raise Failure(
            "Slack rejected the message; check bot permissions and channel membership."
        )
    return {"channel": result["channel"], "ts": result["ts"]}


def publish_channel(ledger, campaign, channel, send):
    slug = campaign["id"]
    previous = ledger.read(slug, channel)
    if previous:
        if previous["status"] == "published":
            return previous
        raise Failure(
            f"{channel}: unresolved attempt; reconcile the receipt before retrying."
        )
    destination = os.environ.get(
        "SLACK_CHANNEL_ID" if channel == "slack" else "BLUESKY_IDENTIFIER"
    )
    pending = {
        "status": "pending",
        "campaign": slug,
        "channel": channel,
        "destination": destination,
        "article": campaign["url"],
        "text_sha256": hashlib.sha256(campaign["copy"][channel].encode()).hexdigest(),
        "commit": os.environ["GITHUB_SHA"],
        "run": os.environ["GITHUB_SERVER_URL"]
        + "/"
        + os.environ["GITHUB_REPOSITORY"]
        + "/actions/runs/"
        + os.environ["GITHUB_RUN_ID"],
    }
    # A durable pending receipt must exist BEFORE any external post is attempted.
    saved = ledger.write(slug, channel, pending, None)
    if not saved or saved.get("status") != "pending":
        raise Failure("Could not verify the pending receipt. Nothing posted.")
    result = send(campaign["copy"][channel])
    done = dict(pending, status="published", result=result)
    ledger.write(slug, channel, done, saved)
    return done


def report(text):
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as output:
            output.write(text + "\n\n")


def main():
    selected = os.environ.get("CHANNELS", "bluesky")
    if selected not in (*CHANNELS, "both"):
        raise Failure("Choose bluesky, slack or both.")
    channels = CHANNELS if selected == "both" else (selected,)
    campaign = load_campaign(os.environ.get("CAMPAIGN", ""), channels)
    check_live(campaign)
    ledger = Ledger()
    publishing = os.environ.get("PUBLISH") == "true"
    if publishing:
        if os.environ.get("GITHUB_REF") != "refs/heads/" + os.environ["DEFAULT_BRANCH"]:
            raise Failure("Publish only from the default branch.")
        credentials(channels)
        ledger.ensure()
    errors = False
    for channel in channels:
        report(f"### {channel}: {campaign['id']}")
        if not publishing:
            previous = ledger.read(campaign["id"], channel)
            report("Receipt: " + (previous["status"] if previous else "not yet posted"))
            report("```text\n" + campaign["copy"][channel] + "\n```")
            continue
        try:
            result = publish_channel(
                ledger,
                campaign,
                channel,
                post_bluesky if channel == "bluesky" else post_slack,
            )
            report("Published (or already published): " + json.dumps(result["result"]))
        except Exception:
            # Never print HTTP bodies, headers or credential-bearing exceptions.
            report(
                "Publication incomplete. Check the receipt on publicity-state before retrying this channel. No automatic retry was attempted."
            )
            errors = True
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as error:
        report(str(error))
        sys.exit(1)
    except Exception:
        report(
            "Validation or network request failed. No automatic retry was attempted; check receipts before publishing again."
        )
        sys.exit(1)
