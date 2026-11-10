# Manually publishing a campaign

The **Publish publicity campaign** Action publishes the reviewed Bluesky and/or
Slack text from `publicity/campaigns/<id>.toml`. LinkedIn and X remain manual.
It never runs on merge, on a schedule or when an article changes.

The code uses Python's standard library; no social SDK or extra service is needed.
Bluesky text includes clickable link facets, not an image/link-preview card.
Slack messages use plain text with unfurls disabled, avoiding accidental mentions.

## One-time GitHub setup

Merge this workflow to the default branch before using it. Under repository
**Settings → Environments**, create `publicity`. Restrict deployment branches to
the default branch (`main`). Required reviewers are optional: the manual publish
dispatch is the maintainer's explicit publication step.

Add these environment entries (not credentials in campaign files):

| Type | Name | Value |
| --- | --- | --- |
| Variable | `BLUESKY_IDENTIFIER` | The SQLFluff account handle, e.g. `sqlfluff.com` |
| Secret | `BLUESKY_APP_PASSWORD` | Dedicated Bluesky app password |
| Secret | `SLACK_BOT_TOKEN` | Bot User OAuth Token beginning `xoxb-` |
| Variable | `SLACK_CHANNEL_ID` | Intended channel's ID, e.g. `C0123456789` |

The automatically supplied `GITHUB_TOKEN` writes posting receipts to a separate
`publicity-state` branch. No personal GitHub token is needed. Repository or
organisation policy must allow this job's `contents: write` permission. If a
ruleset prevents creation or updates of that branch, adjust the rule for this
state branch; do not remove protection from `main`. The publisher refuses to
post unless it can first write and read back a pending receipt.

Do not delete the state branch or rename campaign IDs after posting. If Netlify
builds every branch, exclude `publicity-state` from its branch-deploy selection
to avoid unnecessary builds for receipt commits.

## Bluesky credential

1. Sign in to the **SQLFluff** Bluesky account.
2. Open **Settings → Privacy and Security → App Passwords** (or find App Passwords
   in Settings), then create one named `SQLFluff GitHub publicity`.
3. Leave direct-message access disabled. Copy the generated password directly
   into GitHub's `BLUESKY_APP_PASSWORD` environment secret.
4. Set `BLUESKY_IDENTIFIER` to the account handle, without `@`.

The initial implementation uses `https://bsky.social` as the account's PDS.
If SQLFluff moves to a different hosting provider, update the publisher before
using it. Use an app password, not the account's main password. Revoke it from
Bluesky and replace the GitHub secret when rotating access. Never paste it into
an issue, chat, workflow input or tracked file.

Reference: https://bsky.app/settings/app-passwords and
https://bsky.network/docs/advanced-guides/posts/

## Slack credential

1. At https://api.slack.com/apps create an app **From scratch**, named
   `SQLFluff Updates`, in the SQLFluff workspace. An existing suitable app can
   be used instead; make sure you know which channels it is permitted to post to.
2. In **OAuth & Permissions**, add the **Bot Token Scope** `chat:write`.
   No history-reading scope, user token or `chat:write.public` is required.
3. Install the app to the workspace (or reinstall after changing scopes).
   Follow your workspace's approval process if app installation is restricted.
4. Copy **Bot User OAuth Token** directly into GitHub's `SLACK_BOT_TOKEN` secret.
   Signing secrets and app-level tokens are different credentials and will not work.
5. Invite the bot to the intended channel, for example `/invite @SQLFluff Updates`.
6. Open the channel details and copy its **Channel ID** into `SLACK_CHANNEL_ID`.
   For a test-channel post, use a separate, clearly labelled smoke-test campaign
   ID. Posting an actual campaign to a test channel still consumes that
   campaign's Slack receipt. Restore the production channel variable and invite
   the bot there before publishing real campaigns.

No event subscriptions, incoming webhook or public server is required.
This version expects a non-rotating bot token. If your workspace requires token
rotation, add refresh-token support before use rather than supplying a token
that will expire unattended. Rotate/revoke credentials through Slack's app
management and update the GitHub secret together.

References: https://docs.slack.dev/reference/methods/chat.postMessage/ and
https://docs.slack.dev/authentication/tokens/

## Run it

1. Review the final article and each channel's copy in a PR. Set the campaign's
   `status = "ready"` once that copy is approved, then merge it.
2. Wait for the production article to deploy. The publisher checks its title,
   canonical URL and indexing metadata, as well as its local draft flag/date.
3. Open **Actions → Publish publicity campaign → Run workflow**. Use branch
   `main`, enter `sqlmesh-templater` or `sqlfluff-4-5-performance`, choose a
   channel and leave **mode = dry-run**. The summary shows the exact copy and
   the existing receipt status. Dry runs need no Bluesky or Slack credentials
   and never create the state branch or send a message.
4. Review the output. Run again with **mode = publish** and the intended
   channel(s). This sends real posts using the configured account/channel.
5. Read the summary and inspect the actual posts. Bluesky receipts contain a
   public URL; Slack receipts contain the channel ID and message timestamp.

Published channels are skipped on subsequent runs, even if the copy is edited.
Selecting **both** handles each channel independently; one failure does not
prevent the other channel's attempt. There is no automatic repost or force flag.

## Interrupted runs and reconciliation

Each `(campaign ID, channel)` has a JSON receipt at
`publicity/receipts/<id>/<channel>.json` on branch `publicity-state`.
It records the destination, text hash, source commit and workflow run, followed
by the returned post identifiers when successful. These are public receipts;
never add tokens to them.

A `pending` receipt means an attempt started but a durable success was not
recorded. The server may have accepted the post before a timeout, cancellation
or receipt-write failure. Reruns stop for that channel, avoiding a duplicate.

Check the configured Bluesky account or Slack channel for the exact post:

- If it exists, edit the receipt on `publicity-state` to `status: "published"`
  and add a `result` object containing the Bluesky `url`/`uri`, or Slack
  `channel`/`ts`. Retain the other fields as an audit trail.
- Only after confirming no post exists, delete that channel's pending receipt
  on the state branch, fix the credentials/configuration if needed, then rerun
  that channel. Deleting a receipt enables a new external posting attempt.
- If uncertain, leave the receipt pending and investigate. Do not blindly
  delete it or change the campaign ID to get around the check.

An authentication failure may also leave a conservative pending receipt, even
when no post was sent. This implementation prioritises avoiding duplicate
announcements over automatic retry of ambiguous errors.

## Local verification

`python -m unittest discover -s publicity/tests -v` exercises approval checks,
source visibility, live-page validation, dry-run isolation, UTF-8 link facets,
independent channels, pending receipts and duplicate prevention. Tests use fake
HTTP responses; they do not contact or post to Bluesky or Slack.
