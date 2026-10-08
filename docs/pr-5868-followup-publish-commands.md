# Publish the reviewed PR #5868 follow-up

Read the [four reply drafts](pr-5868-followup-replies.json) and [updated description](pr-5868-description.md) first. CLAUDE.md requires the owner to read AI-drafted bot replies before posting; if a human joins a thread, the reply must be written by the owner. These commands use the existing authenticated gh account. They do not change draft status.

## 1. Update the PR description

```bash
cd /mnt/data/Projects/mass/ma-provider-msx-bridge
gh pr edit 5868 --repo music-assistant/server --body-file docs/pr-5868-description.md
```

The body edit triggers PR Checks / Verify on the current head. The final-head Test workflow is https://github.com/music-assistant/server/actions/runs/37833590467. Wait for lint, test, provider-scope and Verify to succeed before the next step. Do not remove those required checks to bypass a pending or failing run.

## 2. Preview, verify and publish four responses

```bash
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-followup-replies.json
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-followup-replies.json --check
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-followup-replies.json --publish --reviewed-by-human
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-followup-replies.json --check
```

Run each command only if the previous one succeeds. The publisher refuses a changed PR head, new open comments, a changed discussion, failed/pending checks, or an unreviewed human discussion. Repeated publication of the same reviewed text is idempotent. If a pending review produces GitHub's one-pending-review-per-user error, submit or remove the intended pending review first; do not delete published replies to work around it.

## 3. Resolve the four fixed bot threads after successful publication

Check the inline replies before resolving. Run the live check above immediately before these commands; do not proceed if a discussion has changed.

```bash
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"PRRT_kwDOCxIirM6qeipU"}) { thread { id isResolved } } }'
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"PRRT_kwDOCxIirM6qeipv"}) { thread { id isResolved } } }'
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"PRRT_kwDOCxIirM6qeiqZ"}) { thread { id isResolved } } }'
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"PRRT_kwDOCxIirM6qeiq5"}) { thread { id isResolved } } }'
```

No reply to the human support-issue commenter is sent by these commands. See [the analysis and owner-reply talking points](support-6624-followup-analysis.md).
