# PR #5868 follow-up publication

The four inline comments are from OzGav, a human reviewer. `CLAUDE.md` says "Replies to human reviewers are written by humans." Review and rewrite the drafts in `docs/pr-5868-ozgav-followup-replies.json` in your own words, then set `human_authored` to `true` on each reviewed entry. The publisher intentionally rejects the supplied AI-authored draft bundle as-is.

A condensed description for the new head is prepared in `docs/pr-5868-description.md`. It preserves the current owner's checklist state. After reviewing it, publish through REST (avoids the deprecated GraphQL projectCards field):

```bash
jq -n --rawfile body docs/pr-5868-description.md '{body: $body}' | \
  gh api --method PATCH repos/music-assistant/server/pulls/5868 --input - --jq .html_url
```

This triggers the PR metadata Verify check for the new head.

After the required CI checks pass and the description has been refreshed for the current head, run:

```bash
python3 scripts/publish_pr_review_replies.py \
  --bundle docs/pr-5868-ozgav-followup-replies.json --check

python3 scripts/publish_pr_review_replies.py \
  --bundle docs/pr-5868-ozgav-followup-replies.json \
  --publish --reviewed-by-human
```

The script verifies the current commit, CI, every original comment, and absence of new open discussions. It prevents duplicate publication. It does not resolve threads.

The general review draft is in `docs/pr-5868-ozgav-followup-review.md`. Do not post it unchanged as a human-authored reply. The official website note is a separate patch, `docs/patches/pr-5868-msx-docs-seek.patch`. Apply it in a current checkout of `music-assistant/music-assistant.io` with:

```bash
git apply --check --unidiff-zero /absolute/path/to/ma-provider-msx-bridge/docs/patches/pr-5868-msx-docs-seek.patch
git apply --unidiff-zero /absolute/path/to/ma-provider-msx-bridge/docs/patches/pr-5868-msx-docs-seek.patch
```

The public provider docs page already includes the note in this provider PR. The official MA docs repository has not been modified.
