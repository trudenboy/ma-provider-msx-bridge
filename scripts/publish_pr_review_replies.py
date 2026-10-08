#!/usr/bin/env python3
"""
Preview, check, or publish reviewed replies to PR #5868 discussions.

Requires Python 3.10+ and an authenticated GitHub CLI for live operations.
No review thread is resolved and no PR metadata is changed.
"""

# CLI output and subprocess invocation of gh are intentional.
# ruff: noqa: T201, S603

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = "music-assistant/server"
PR = 5868
COMMENTS = """nodes { id body url author { login __typename } }
pageInfo { hasNextPage endCursor }"""
THREAD_QUERY = """query($cursor:String) {
  repository(owner:"music-assistant",name:"server") {
    pullRequest(number:5868) {
      reviewThreads(first:100,after:$cursor) {
        nodes { id isResolved comments(first:100) { COMMENTS } }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}""".replace("COMMENTS", COMMENTS)
COMMENT_QUERY = """query($id:ID!,$cursor:String) {
  node(id:$id) { ... on PullRequestReviewThread {
    comments(first:100,after:$cursor) { COMMENTS }
  } }
}""".replace("COMMENTS", COMMENTS)


def gh(endpoint: str, **fields: Any) -> Any:
    """Call gh without a shell; refuse API errors, including GraphQL errors."""
    command = ["gh", "api", endpoint]
    if endpoint == "graphql":
        for key, value in fields.items():
            if value is not None:
                command.extend(["-f", f"{key}={value}"])
        payload = None
    elif fields:
        command.extend(["--method", "POST", "--input", "-"])
        payload = json.dumps(fields)
    else:
        payload = None
    result = subprocess.run(command, input=payload, text=True, capture_output=True, check=False)
    if result.returncode:
        details = "\n".join(part.strip() for part in (result.stderr, result.stdout) if part.strip())
        raise ValueError(f"GitHub API failed ({endpoint}): {details}")
    data = json.loads(result.stdout)
    if isinstance(data, dict) and data.get("errors"):
        raise ValueError(f"GraphQL returned errors: {data['errors']}")
    return data


def live_threads() -> list[dict[str, Any]]:
    """Read every review thread and every comment, with pagination."""
    threads: list[dict[str, Any]] = []
    cursor = None
    while True:
        page = gh("graphql", query=THREAD_QUERY, cursor=cursor)["data"]["repository"][
            "pullRequest"
        ]["reviewThreads"]
        for thread in page["nodes"]:
            comments = thread["comments"]
            nodes = list(comments["nodes"])
            while comments["pageInfo"]["hasNextPage"]:
                comments = gh(
                    "graphql",
                    query=COMMENT_QUERY,
                    id=thread["id"],
                    cursor=comments["pageInfo"]["endCursor"],
                )["data"]["node"]["comments"]
                nodes.extend(comments["nodes"])
            thread["comments"]["nodes"] = nodes
            threads.append(thread)
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        cursor = page["pageInfo"]["endCursor"]


def check_head_and_ci(bundle: dict[str, Any]) -> None:
    """Check the exact PR revision and the latest GitHub Actions check of each name."""
    pr = gh(f"repos/{REPO}/pulls/{PR}")
    if pr["state"] != "open" or pr["head"]["sha"] != bundle["expected_head"]:
        raise ValueError("PR is closed or its head changed; review and regenerate the bundle.")
    latest: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        checks = gh(
            f"repos/{REPO}/commits/{bundle['expected_head']}/check-runs?per_page=100&page={page}"
        )["check_runs"]
        for check in checks:
            if check["app"]["slug"] == "github-actions":
                previous = latest.get(check["name"])
                if previous is None or check["id"] > previous["id"]:
                    latest[check["name"]] = check
        if len(checks) < 100:
            break
        page += 1
    if not bundle.get("required_checks"):
        raise ValueError("The bundle must name required CI checks.")
    for name in bundle["required_checks"]:
        check = latest.get(name)
        if check is None or check["status"] != "completed" or check["conclusion"] != "success":
            raise ValueError(f"CI check {name!r} is missing, pending, or unsuccessful.")


def marker(bundle: dict[str, Any], reply: dict[str, Any]) -> str:
    """Identify one reply to one reviewed revision."""
    return f"<!-- msx-review-reply:{PR}:{reply['root_comment_id']}:{bundle['expected_head']} -->"


def signature(comments: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    """Compare the exact reviewed discussion, including author identities."""
    return [(comment["id"], comment["body"], comment["author"]) for comment in comments]


def plan(
    bundle: dict[str, Any], viewer: str, *, publishing: bool, resolved_unanswered: bool = False
) -> list[dict[str, Any]]:
    """Validate the selected frozen discussion set before returning candidates."""
    known = {reply["thread_id"]: reply for reply in bundle["threads"]}
    if len(known) != len(bundle["threads"]):
        raise ValueError("Duplicate thread in reply bundle.")
    targets = (
        {
            reply["thread_id"]
            for reply in bundle["threads"]
            if reply["resolved_at_snapshot"] and len(reply["comments"]) == 1
        }
        if resolved_unanswered
        else set()
    )
    seen = set()
    candidates = []
    for thread in live_threads():
        if resolved_unanswered:
            if thread["id"] not in targets:
                continue
            if not thread["isResolved"]:
                raise ValueError(f"Selected thread {thread['id']} was reopened; review it again.")
            seen.add(thread["id"])
        elif thread["isResolved"]:
            continue
        reply = known.get(thread["id"])
        if reply is None:
            raise ValueError(f"New open thread {thread['id']}; review it before publishing.")
        comments = thread["comments"]["nodes"]
        tag = marker(bundle, reply)
        published = [
            comment
            for comment in comments
            if comment["author"] and comment["author"]["login"] == viewer and tag in comment["body"]
        ]
        if published:
            expected = reply["body"].strip() + "\n\n" + tag
            if len(published) != 1 or published[0]["body"].strip() != expected:
                raise ValueError("An existing marked reply differs; review it manually.")
            original = [comment for comment in comments if comment is not published[0]]
            if signature(original) != signature(reply["comments"]):
                raise ValueError("Discussion changed after publication; review it manually.")
            print(f"Already published: {reply['root_comment_id']}")
            continue
        if signature(comments) != signature(reply["comments"]):
            raise ValueError(f"Discussion {reply['root_comment_id']} changed; review it again.")
        root_id = int(comments[0]["url"].split("#discussion_r")[-1])
        if root_id != reply["root_comment_id"]:
            raise ValueError("Root comment does not match the reply target.")
        if not reply["body"].strip():
            raise ValueError("Reply body is empty.")
        human = any(
            not comment["author"] or comment["author"]["__typename"] != "Bot"
            for comment in comments
        )
        if human and reply.get("human_authored") is not True:
            if publishing:
                raise ValueError(
                    f"Thread {root_id} includes a human reviewer: rewrite the reply "
                    "in your own words and set human_authored to true."
                )
            print(f"Human-authored text required before publication: {root_id}")
        candidates.append(reply)
    if targets - seen:
        raise ValueError("Selected resolved discussions disappeared; review the bundle again.")
    return candidates


def main() -> None:
    """Run an offline preview by default; opt in explicitly to live operations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs/pr-5868-replies.json",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only live verification")
    mode.add_argument("--publish", action="store_true", help="Post validated replies")
    parser.add_argument("--reviewed-by-human", action="store_true")
    parser.add_argument(
        "--resolved-unanswered",
        action="store_true",
        help="Use only threads resolved with one root comment in the reviewed bundle",
    )
    args = parser.parse_args()
    if args.publish and not args.reviewed_by_human:
        parser.error("--publish requires --reviewed-by-human")
    try:
        bundle = json.loads(args.bundle.read_text())
        if bundle["repo"] != REPO or bundle["pr"] != PR:
            raise ValueError("This script is restricted to music-assistant/server PR #5868.")
        if not args.check and not args.publish:
            for reply in bundle["threads"]:
                selected = (
                    reply["resolved_at_snapshot"] and len(reply["comments"]) == 1
                    if args.resolved_unanswered
                    else not reply["resolved_at_snapshot"]
                )
                if selected:
                    print(f"Thread {reply['root_comment_id']}\n{reply['body']}\n")
            print("Offline preview only; live open threads and CI require --check.")
            return
        check_head_and_ci(bundle)
        viewer = gh("user")["login"]
        candidates = plan(
            bundle, viewer, publishing=args.publish, resolved_unanswered=args.resolved_unanswered
        )
        print(f"Verified head {bundle['expected_head']}; {len(candidates)} reply candidate(s).")
        for reply in candidates:
            print(f"Thread {reply['root_comment_id']}\n{reply['body']}\n")
        if args.publish:
            for reply in candidates:
                # Revalidate the full discussion and CI immediately before every write.
                check_head_and_ci(bundle)
                current = plan(
                    bundle, viewer, publishing=True, resolved_unanswered=args.resolved_unanswered
                )
                if not any(item["thread_id"] == reply["thread_id"] for item in current):
                    continue
                response = gh(
                    f"repos/{REPO}/pulls/{PR}/comments/{reply['root_comment_id']}/replies",
                    body=reply["body"].strip() + "\n\n" + marker(bundle, reply),
                )
                print(f"Published: {response['html_url']}")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
