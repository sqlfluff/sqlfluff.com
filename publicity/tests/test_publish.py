import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location(
    "publisher", Path(__file__).resolve().parents[1] / "publish.py"
)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class MemoryLedger:
    def __init__(self):
        self.records = {}

    def read(self, slug, channel):
        return self.records.get((slug, channel))

    def write(self, slug, channel, record, previous):
        stored = dict(record, _sha="receipt-sha")
        self.records[slug, channel] = stored
        return stored


class PublishingTest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {
                "GITHUB_SHA": "abc",
                "GITHUB_SERVER_URL": "https://github.com",
                "GITHUB_REPOSITORY": "sqlfluff/sqlfluff.com",
                "GITHUB_RUN_ID": "123",
                "BLUESKY_IDENTIFIER": "sqlfluff.com",
                "SLACK_CHANNEL_ID": "C123",
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.campaign = {
            "id": "example",
            "url": "https://sqlfluff.com/updates/example/",
            "copy": {"bluesky": "Approved text", "slack": "Approved text"},
        }

    def test_published_receipt_prevents_duplicate_even_after_copy_edit(self):
        ledger = MemoryLedger()
        send = Mock(return_value={"url": "https://example.com/post"})
        publisher.publish_channel(ledger, self.campaign, "bluesky", send)
        self.campaign["copy"]["bluesky"] = "An edited announcement"
        publisher.publish_channel(ledger, self.campaign, "bluesky", send)
        send.assert_called_once()

    def test_pending_is_saved_before_send_and_ambiguous_failure_blocks_retry(self):
        ledger = MemoryLedger()

        def uncertain(text):
            self.assertEqual(ledger.read("example", "slack")["status"], "pending")
            raise TimeoutError()

        with self.assertRaises(TimeoutError):
            publisher.publish_channel(ledger, self.campaign, "slack", uncertain)
        send = Mock()
        with self.assertRaises(publisher.Failure):
            publisher.publish_channel(ledger, self.campaign, "slack", send)
        send.assert_not_called()

    def test_receipt_write_failure_prevents_post(self):
        ledger = MemoryLedger()
        ledger.write = Mock(side_effect=OSError())
        send = Mock()
        with self.assertRaises(OSError):
            publisher.publish_channel(ledger, self.campaign, "slack", send)
        send.assert_not_called()

    def test_receipt_failure_after_post_leaves_pending(self):
        ledger = MemoryLedger()
        original = ledger.write

        def write(slug, channel, record, previous):
            if record["status"] == "published":
                raise OSError()
            return original(slug, channel, record, previous)

        ledger.write = write
        with self.assertRaises(OSError):
            publisher.publish_channel(
                ledger, self.campaign, "slack", Mock(return_value={"ts": "1"})
            )
        self.assertEqual(ledger.read("example", "slack")["status"], "pending")

    def test_channel_receipts_are_independent(self):
        ledger = MemoryLedger()
        ledger.records["example", "slack"] = {"status": "pending"}
        send = Mock(return_value={"uri": "at://example"})
        publisher.publish_channel(ledger, self.campaign, "bluesky", send)
        send.assert_called_once()

    def test_dry_run_never_writes_or_posts(self):
        ledger = Mock()
        ledger.read.return_value = None
        with patch.dict(
            os.environ, {"CHANNELS": "both", "PUBLISH": "false"}
        ), patch.object(
            publisher, "load_campaign", return_value=self.campaign
        ), patch.object(
            publisher, "check_live"
        ), patch.object(
            publisher, "Ledger", return_value=ledger
        ), patch.object(
            publisher, "post_slack"
        ) as slack, patch.object(
            publisher, "post_bluesky"
        ) as bluesky:
            self.assertEqual(publisher.main(), 0)
        ledger.ensure.assert_not_called()
        ledger.write.assert_not_called()
        slack.assert_not_called()
        bluesky.assert_not_called()

    def test_bluesky_link_facets_use_utf8_offsets(self):
        text = "News: café https://sqlfluff.com/updates/example/"
        with patch.object(
            publisher,
            "request",
            side_effect=[
                {"did": "did:plc:test", "accessJwt": "private"},
                {"uri": "at://did:plc:test/app.bsky.feed.post/123"},
            ],
        ) as api:
            with patch.dict(os.environ, {"BLUESKY_APP_PASSWORD": "private"}):
                publisher.post_bluesky(text)
        record = api.call_args.args[1]["record"]
        index = record["facets"][0]["index"]
        self.assertEqual(
            text.encode()[index["byteStart"] : index["byteEnd"]].decode(),
            self.campaign["url"],
        )

    def test_campaign_requires_approval_and_published_article(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            campaign = root / "publicity/campaigns/example.toml"
            campaign.parent.mkdir(parents=True)
            source = root / "content/updates/example/index.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "---\ntitle: Example\ndate: 2020-01-01\ndraft: true\n---\n"
            )
            template = 'id="example"\narticle="/updates/example/"\nstatus="{status}"\n[copy]\nbluesky="https://sqlfluff.com/updates/example/"\n'
            with patch.object(publisher, "ROOT", root):
                campaign.write_text(template.format(status="draft"))
                with self.assertRaises(publisher.Failure):
                    publisher.load_campaign("example", ("bluesky",))
                campaign.write_text(template.format(status="ready"))
                with self.assertRaises(publisher.Failure):
                    publisher.load_campaign("example", ("bluesky",))
                source.write_text(
                    source.read_text().replace("draft: true", "draft: false")
                )
                self.assertEqual(
                    publisher.load_campaign("example", ("bluesky",))["title"], "Example"
                )
                with self.assertRaises(publisher.Failure):
                    publisher.load_campaign("../example", ("bluesky",))

    def test_live_page_requires_matching_title_canonical_and_indexing(self):
        campaign = dict(self.campaign, title="Example", article="/updates/example/")
        response = Mock()
        response.url = campaign["url"]
        response.headers.get_content_type.return_value = "text/html"
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        good = '<h1>Example</h1><link rel="canonical" href="' + campaign["url"] + '">'
        with patch.object(publisher.urllib.request, "urlopen", return_value=response):
            response.read.return_value = good.encode()
            publisher.check_live(campaign)
            for bad in [
                good.replace("Example", "Old title"),
                good + '<meta name="robots" content="noindex">',
                "<h1>Example</h1>",
            ]:
                response.read.return_value = bad.encode()
                with self.assertRaises(publisher.Failure):
                    publisher.check_live(campaign)


if __name__ == "__main__":
    unittest.main()
