# Publish the reviewed Sendspin migration response

Read [the draft](pr-5868-sendspin-reply.json) and [updated description](pr-5868-description.md). The bundle is restricted to final head faa413dca07cd13e2392a063c811debd6c46c514 and the new Bot-only thread 4224254633. Earlier bundles refer to earlier published revisions and must not be reused.

Update the description through REST, avoiding the old gh pr edit GraphQL projectCards error:

```bash
cd /mnt/data/Projects/mass/ma-provider-msx-bridge
jq -n --rawfile body docs/pr-5868-description.md '{body: $body}' |
  gh api --method PATCH repos/music-assistant/server/pulls/5868 --input - --jq .html_url
```

After final-head lint, test, provider-scope and Verify succeed, publish the owner-reviewed reply:

```bash
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-sendspin-reply.json --check &&
python3 scripts/publish_pr_review_replies.py --bundle docs/pr-5868-sendspin-reply.json --publish --reviewed-by-human
```

After checking the posted reply and verifying the discussion is unchanged, resolve only that thread:

```bash
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"PRRT_kwDOCxIirM6qjr9F"}) { thread { id isResolved } } }'
```

The publisher holds a POSIX file lock to reject simultaneous local runs under the same OS user. Different machines still require coordination. A changed PR head, discussion, or new open thread stops publication; do not bypass the guard or regenerate a bundle simply to repost already answered threads.
