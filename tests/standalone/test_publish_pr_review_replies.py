"""Exercise the publisher CLI and its GitHub boundary."""

# Exercise a fixed local script through a subprocess boundary.
# ruff: noqa: S603

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/publish_pr_review_replies.py"


def test_preview_is_offline_and_selects_only_open_threads(tmp_path: Path) -> None:
    """An offline preview must not include resolved discussions."""
    bundle = tmp_path / "replies.json"
    bundle.write_text(
        json.dumps(
            {
                "repo": "music-assistant/server",
                "pr": 5868,
                "expected_head": "abc",
                "threads": [
                    {
                        "thread_id": "open",
                        "resolved_at_snapshot": False,
                        "root_comment_id": 123,
                        "body": "Reviewed reply",
                    },
                    {
                        "thread_id": "closed",
                        "resolved_at_snapshot": True,
                        "root_comment_id": 456,
                        "body": "Do not post",
                    },
                ],
            }
        )
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": ""},
    )
    assert result.returncode == 0, result.stderr
    assert "Reviewed reply" in result.stdout
    assert "Do not post" not in result.stdout


def test_publish_requires_explicit_human_review_before_network(tmp_path: Path) -> None:
    """A write request without attestation stops before contacting GitHub."""
    bundle = tmp_path / "replies.json"
    bundle.write_text('{"threads": []}')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish"],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": ""},
    )
    assert result.returncode != 0
    assert "--reviewed-by-human" in result.stderr


def github_cli(tmp_path: Path, *, human_authored: bool = True) -> tuple[Path, dict[str, str]]:
    """Provide a fake gh executable at the external API boundary."""
    thread: dict[str, Any] = {
        "id": "open",
        "isResolved": False,
        "comments": {
            "nodes": [
                {
                    "id": "comment",
                    "body": "Please fix previous",
                    "author": {"login": "reviewer", "__typename": "User"},
                    "url": "https://github.com/x#discussion_r123",
                }
            ],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        },
    }
    bundle = tmp_path / "replies.json"
    bundle.write_text(
        json.dumps(
            {
                "repo": "music-assistant/server",
                "pr": 5868,
                "expected_head": "abc",
                "required_checks": ["test", "Verify"],
                "threads": [
                    {
                        "thread_id": "open",
                        "root_comment_id": 123,
                        "resolved_at_snapshot": False,
                        "comments": thread["comments"]["nodes"],
                        "human_authored": human_authored,
                        "body": "My own reviewed reply",
                    }
                ],
            }
        )
    )
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps(
            {
                "head": "abc",
                "threads": [thread],
                "checks": [
                    {
                        "name": name,
                        "id": index,
                        "status": "completed",
                        "conclusion": "success",
                        "app": {"slug": "github-actions"},
                    }
                    for index, name in enumerate(["test", "Verify"])
                ],
            }
        )
    )
    gh = tmp_path / "gh"
    gh.write_text(
        f"#!{sys.executable}\n"
        """# Exercise a fixed local script through a subprocess boundary.
# ruff: noqa: S603

import json, os, sys
from pathlib import Path
from typing import Any
state_path = Path(os.environ["FAKE_GH_STATE"])
state = json.loads(state_path.read_text())
args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if "POST" in args:
    if state.get("post_error"):
        print(json.dumps({"message": "Validation Failed", "errors": [state["post_error"]]}))
        print("gh: Validation Failed (HTTP 422)", file=sys.stderr)
        sys.exit(1)
    payload = json.load(sys.stdin)
    state["threads"][0]["comments"]["nodes"].append({"id": "posted", "body": payload["body"],
        "author": {"login": "owner", "__typename": "User"}, "url": "https://github.com/reply"})
    state_path.write_text(json.dumps(state))
    print(json.dumps({"html_url": "https://github.com/reply"}))
elif args[1] == "graphql":
    if state.get("paged_comments") and any("node(id:$id)" in arg for arg in args):
        print(json.dumps({"data": {"node": {"comments": {
            "nodes": state["paged_comments"], "pageInfo": {"hasNextPage": False}}}}}))
        sys.exit(0)
    if state.get("paged_threads"):
        after = any(arg.startswith("cursor=") for arg in args)
        threads = state["paged_threads"] if after else state["threads"]
        print(json.dumps({"data": {"repository": {"pullRequest": {"reviewThreads": {
            "nodes": threads, "pageInfo": {"hasNextPage": not after,
                "endCursor": "next"}}}}}}))
        sys.exit(0)
    print(json.dumps({"data": {"repository": {"pullRequest": {"reviewThreads": {
        "nodes": state["threads"], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}}))
elif args[1] == "user":
    print('{"login": "owner"}')
elif "check-runs" in args[1]:
    print(json.dumps({"check_runs": state["checks"], "total_count": len(state["checks"])}))
else:
    state["head_reads"] = state.get("head_reads", 0) + 1
    state_path.write_text(json.dumps(state))
    if state.get("change_head_before_write") and state["head_reads"] > 1:
        state["head"] = "changed"
    print(json.dumps({"state": "open", "head": {"sha": state["head"]}}))
"""
    )
    gh.chmod(0o755)
    env = dict(
        os.environ,
        PATH=str(tmp_path),
        FAKE_GH_STATE=str(state),
        FAKE_GH_LOG=str(tmp_path / "calls.jsonl"),
    )
    return bundle, env


def test_live_check_is_read_only_and_checks_current_ci(tmp_path: Path) -> None:
    """Successful live verification never posts a reply."""
    bundle, env = github_cli(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--check"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    calls = (tmp_path / "calls.jsonl").read_text()
    assert "check-runs" in calls
    assert "POST" not in calls


@pytest.mark.parametrize("changed", ["head", "ci", "comment", "new-thread", "race"])
def test_changed_review_context_blocks_every_write(tmp_path: Path, changed: str) -> None:
    """A changed revision, discussion, or CI result must not receive stale replies."""
    bundle, env = github_cli(tmp_path)
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    if changed == "head":
        state["head"] = "different"
    elif changed == "ci":
        state["checks"].append(
            {
                "name": "test",
                "id": 99,
                "status": "in_progress",
                "conclusion": None,
                "app": {"slug": "github-actions"},
            }
        )
    elif changed == "comment":
        state["threads"][0]["comments"]["nodes"][0]["body"] = "Edited request"
    elif changed == "new-thread":
        state["threads"].append({"id": "new", "isResolved": False})
    else:
        state["change_head_before_write"] = True
    state_path.write_text(json.dumps(state))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish", "--reviewed-by-human"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "POST" not in (tmp_path / "calls.jsonl").read_text()


def test_human_thread_requires_human_written_text(tmp_path: Path) -> None:
    """A global review flag cannot replace human authorship of a human reply."""
    bundle, env = github_cli(tmp_path, human_authored=False)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish", "--reviewed-by-human"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "human_authored" in result.stderr
    assert "POST" not in (tmp_path / "calls.jsonl").read_text()


def test_publication_is_idempotent_and_leaves_resolved_threads_alone(tmp_path: Path) -> None:
    """Two runs post once, with no resolve mutation or change to PR metadata."""
    bundle, env = github_cli(tmp_path)
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    state["threads"].append(
        {
            "id": "closed",
            "isResolved": True,
            "comments": {"nodes": [], "pageInfo": {"hasNextPage": False}},
        }
    )
    state_path.write_text(json.dumps(state))
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--bundle",
                str(bundle),
                "--publish",
                "--reviewed-by-human",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()]
    writes = [call for call in calls if "POST" in call]
    assert len(writes) == 1
    assert writes[0][1] == "repos/music-assistant/server/pulls/5868/comments/123/replies"
    assert "resolveReviewThread" not in str(calls)


def test_pagination_cannot_hide_a_new_discussion(tmp_path: Path) -> None:
    """An unseen open thread on a second page blocks publication."""
    bundle, env = github_cli(tmp_path)
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    state["paged_threads"] = [
        {
            "id": "new",
            "isResolved": False,
            "comments": {"nodes": [], "pageInfo": {"hasNextPage": False}},
        }
    ]
    state_path.write_text(json.dumps(state))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish", "--reviewed-by-human"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "New open thread" in result.stderr
    assert "POST" not in (tmp_path / "calls.jsonl").read_text()


def test_pagination_cannot_hide_a_human_in_a_bot_thread(tmp_path: Path) -> None:
    """A human joining a bot thread still requires the owner's own reply."""
    bundle, env = github_cli(tmp_path, human_authored=False)
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    root = state["threads"][0]["comments"]["nodes"][0]
    root["author"] = {"login": "copilot", "__typename": "Bot"}
    human = {
        "id": "human",
        "body": "Please explain in your own words",
        "author": {"login": "human", "__typename": "User"},
        "url": "https://github.com/comment",
    }
    state["paged_comments"] = [human]
    state["threads"][0]["comments"]["pageInfo"] = {"hasNextPage": True, "endCursor": "next"}
    state_path.write_text(json.dumps(state))
    data = json.loads(bundle.read_text())
    data["threads"][0]["comments"] = [root, human]
    bundle.write_text(json.dumps(data))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish", "--reviewed-by-human"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "human_authored" in result.stderr
    assert "POST" not in (tmp_path / "calls.jsonl").read_text()


def test_api_validation_details_are_reported(tmp_path: Path) -> None:
    """A failed POST must expose GitHub's actionable validation explanation."""
    bundle, env = github_cli(tmp_path)
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    state["post_error"] = {"field": "body", "code": "custom", "message": "Reply was rejected"}
    state_path.write_text(json.dumps(state))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--publish", "--reviewed-by-human"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "Reply was rejected" in result.stderr


def test_resolved_unanswered_mode_posts_once_without_reopening(tmp_path: Path) -> None:
    """Opt-in publication covers the frozen unanswered resolved set exactly once."""
    bundle, env = github_cli(tmp_path)
    data = json.loads(bundle.read_text())
    data["threads"][0]["resolved_at_snapshot"] = True
    bundle.write_text(json.dumps(data))
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    state["threads"][0]["isResolved"] = True
    state["threads"].append(
        {
            "id": "already-answered",
            "isResolved": True,
            "comments": {"nodes": [], "pageInfo": {"hasNextPage": False}},
        }
    )
    state_path.write_text(json.dumps(state))
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--bundle",
                str(bundle),
                "--resolved-unanswered",
                "--publish",
                "--reviewed-by-human",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert len([call for call in calls if "POST" in call]) == 1
    assert "resolveReviewThread" not in str(calls)
    assert json.loads(state_path.read_text())["threads"][0]["isResolved"] is True


@pytest.mark.parametrize("change", ["reopened", "answered", "missing"])
def test_resolved_batch_stops_when_a_selected_thread_changes(tmp_path: Path, change: str) -> None:
    """Closed-batch publication cannot silently accept a changed reviewed target."""
    bundle, env = github_cli(tmp_path)
    data = json.loads(bundle.read_text())
    data["threads"][0]["resolved_at_snapshot"] = True
    bundle.write_text(json.dumps(data))
    state_path = tmp_path / "state.json"
    state = json.loads(state_path.read_text())
    thread = state["threads"][0]
    thread["isResolved"] = True
    if change == "reopened":
        thread["isResolved"] = False
    elif change == "answered":
        comment = dict(thread["comments"]["nodes"][0], id="new-comment", body="Already answered")
        thread["comments"]["nodes"].append(comment)
    else:
        state["threads"] = []
    state_path.write_text(json.dumps(state))
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bundle",
            str(bundle),
            "--resolved-unanswered",
            "--publish",
            "--reviewed-by-human",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "POST" not in (tmp_path / "calls.jsonl").read_text()


def test_parallel_publisher_stops_before_contacting_github(tmp_path: Path) -> None:
    """A second process cannot publish while the first is between validation and POST."""
    bundle, env = github_cli(tmp_path)
    env["TMPDIR"] = str(tmp_path)
    ready = tmp_path / "ready"
    release = tmp_path / "release"
    env["FAKE_GH_READY"] = str(ready)
    env["FAKE_GH_RELEASE"] = str(release)
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        fake_gh.read_text().replace(
            "args = sys.argv[1:]",
            "args = sys.argv[1:]\n"
            "import time\n"
            "ready = Path(os.environ['FAKE_GH_READY'])\n"
            "if not ready.exists():\n"
            "    ready.touch()\n"
            "    while not Path(os.environ['FAKE_GH_RELEASE']).exists():\n"
            "        time.sleep(0.02)",
        )
    )
    command = [
        sys.executable,
        str(SCRIPT),
        "--bundle",
        str(bundle),
        "--publish",
        "--reviewed-by-human",
    ]
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    ) as first:
        try:
            deadline = time.monotonic() + 10
            while not ready.exists():
                assert time.monotonic() < deadline, "First publisher never reached its API boundary"
                time.sleep(0.02)
            second = subprocess.run(
                command, capture_output=True, text=True, check=False, env=env, timeout=10
            )
            assert second.returncode != 0
            assert "Another publication is running" in second.stderr
            assert not (tmp_path / "calls.jsonl").exists()
        finally:
            release.touch()
            _, first_stderr = first.communicate(timeout=10)
    assert first.returncode == 0, first_stderr
    calls = [json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert len([call for call in calls if "POST" in call]) == 1
