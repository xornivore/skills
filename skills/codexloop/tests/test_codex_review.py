import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/codex_review.py"
SPEC = importlib.util.spec_from_file_location("codex_review", SCRIPT)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)
HEAD = "a" * 40
OLD_HEAD = "b" * 40
BOT = "chatgpt-codex-connector[bot]"
BEFORE = "2026-10-16T10:00:00Z"
TRIGGER = "2026-10-16T10:01:00Z"
AFTER = "2026-10-16T10:05:00Z"
NOW = datetime(2026, 10, 16, 10, 2, tzinfo=timezone.utc)


def summary(status="completed", findings=False, commit=HEAD, **overrides):
    state = {"code_review": {"commit_sha": commit, "has_any_findings": findings,
                             "has_unresolved_findings": findings, "status": status}}
    body = (f"{REVIEW.SUMMARY_MARKER}\n<!-- codex-review-state:v1 {json.dumps(state)} -->\n\n"
            "## Codex Review Summary\n")
    return {"id": 10, "user": {"login": BOT}, "updated_at": AFTER, "body": body,
            "html_url": "https://github.com/o/r/pull/1#issuecomment-10", **overrides}


def receipt(commit=HEAD[:10], **overrides):
    body = ("<!-- codex-review-receipt:v1 -->\n\nCodex Review: Didn’t find any major issues. "
            f"Keep them coming!\n\n**Reviewed commit:** `{commit}`\n")
    return {"id": 20, "user": {"login": BOT}, "updated_at": AFTER, "body": body, **overrides}


def review(**overrides):
    body = "### 💡 Codex Review\n\n**Reviewed commit:** `aaaaaaaaaa`\n"
    return {"id": 30, "user": {"login": BOT}, "commit_id": HEAD, "submitted_at": AFTER,
            "body": body, "html_url": "https://github.com/o/r/pull/1#pullrequestreview-30", **overrides}


def attempt(**overrides):
    return {
        "status": "triggered", "repo": "owner/repo", "pr": 1, "head": HEAD,
        "triggered_at": TRIGGER, "bots": [BOT], "comments": [], "reviews": [], "reactions": [],
        **overrides,
    }


def evaluate(state=None, comments=(), reviews=(), reactions=()):
    return REVIEW.evaluate(state or attempt(), HEAD, list(comments), list(reviews), list(reactions))


def test_fresh_review_with_findings_is_not_clean():
    result = evaluate(reviews=[review()], comments=[summary(findings=True)])
    assert (result["status"], result["clean"], result["source_id"]) == ("review_ready", False, 30)


def test_review_before_trigger_or_on_old_commit_is_ignored():
    stale = [review(submitted_at=BEFORE), review(id=31, commit_id=OLD_HEAD)]
    assert evaluate(reviews=stale)["status"] == "pending"


def test_review_already_in_snapshot_is_ignored():
    old = review()
    assert evaluate(state=attempt(reviews=[old]), reviews=[old])["status"] == "pending"


def test_clean_receipt_for_head_is_clean():
    result = evaluate(comments=[receipt()])
    assert (result["status"], result["clean"], result["source"]) == ("review_ready", True, "comment")


def test_clean_receipt_for_other_commit_is_ignored():
    assert evaluate(comments=[receipt(commit=OLD_HEAD[:10])])["status"] == "pending"


def test_completed_summary_without_findings_is_clean():
    result = evaluate(comments=[summary()])
    assert (result["clean"], result["source"]) == (True, "summary")


def test_completed_summary_with_findings_waits_for_the_review():
    result = evaluate(comments=[summary(findings=True)])
    assert result["status"] == "pending"


def test_running_summary_keeps_waiting():
    assert evaluate(comments=[summary(status="running")])["reason"] == "Codex review is running"


def test_summary_for_another_commit_cannot_complete_the_attempt():
    assert evaluate(comments=[summary(commit=OLD_HEAD)])["status"] == "pending"


def test_unchanged_summary_body_cannot_refresh_an_old_result():
    old = summary(updated_at=BEFORE)
    edited = summary()  # same body, newer timestamp
    assert evaluate(state=attempt(comments=[old]), comments=[edited])["status"] == "pending"


def test_failed_summary_stops():
    with pytest.raises(REVIEW.ReviewError, match="failed review"):
        evaluate(comments=[summary(status="failed", findings=True)])


def test_usage_limit_comment_stops():
    limit = {"id": 40, "user": {"login": BOT}, "updated_at": AFTER,
             "body": "You have reached your Codex usage limits for code reviews."}
    with pytest.raises(REVIEW.ReviewError, match="usage limit"):
        evaluate(comments=[limit])


def test_non_bot_comments_are_ignored():
    impostor = receipt(user={"login": "someone"})
    assert evaluate(comments=[impostor])["status"] == "pending"


def test_new_thumbs_up_reaction_is_a_clean_fallback():
    reaction = {"id": 50, "content": "+1", "user": {"login": BOT}, "created_at": AFTER}
    result = evaluate(reactions=[reaction])
    assert (result["clean"], result["source"]) == (True, "reaction")


def test_old_thumbs_up_reaction_is_ignored():
    reaction = {"id": 50, "content": "+1", "user": {"login": BOT}, "created_at": BEFORE}
    assert evaluate(state=attempt(reactions=[reaction]), reactions=[reaction])["status"] == "pending"


def test_changed_head_is_an_error():
    with pytest.raises(REVIEW.ReviewError, match="head changed"):
        REVIEW.evaluate(attempt(head=OLD_HEAD), HEAD, [], [], [])


def test_finding_parses_badge_title_and_location():
    comment = {
        "body": "**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>"
                "  Reconcile when the base SHA changes**\n\nExplanation.\n\nUseful? React with 👍 / 👎.",
        "path": "src/a.py", "line": None, "original_line": 12, "html_url": "u",
    }
    assert REVIEW.finding(comment) == {
        "severity": "P1", "title": "Reconcile when the base SHA changes",
        "path": "src/a.py", "line": 12, "url": "u",
    }


class FakeGitHub:
    def __init__(self, comments=(), reviews=(), reactions=(), heads=None):
        self.comments, self.reviews, self.reactions = list(comments), list(reviews), list(reactions)
        self.heads = list(heads or [])
        self.posted = []

    def head(self, repo, pr):
        return self.heads.pop(0) if self.heads else HEAD

    def snapshot(self, repo, pr):
        return {"comments": list(self.comments), "reviews": list(self.reviews), "reactions": list(self.reactions)}

    def command(self, *args):
        self.posted.append(args)
        return {"id": 99, "created_at": TRIGGER}

    def review_comments(self, repo, pr, review_id):
        return [{"body": "**![P2 Badge](x) Tidy up**", "path": "a.py", "line": 3, "html_url": "c"}]


def test_start_posts_trigger_and_records_attempt(tmp_path):
    github = FakeGitHub()
    output = tmp_path / "attempt.json"
    result = REVIEW.start(github, "o/r", 1, output, [BOT], focus="for security", now=lambda: NOW)
    assert result["mode"] == "posted" and result["triggered_at"] == TRIGGER
    assert github.posted[0][-1] == "body=@codex review for security"
    assert json.loads(output.read_text())["trigger_id"] == 99


def test_start_refuses_to_overwrite_an_attempt(tmp_path):
    output = tmp_path / "attempt.json"
    output.write_text("{}")
    with pytest.raises(FileExistsError):
        REVIEW.start(FakeGitHub(), "o/r", 1, output, [BOT], now=lambda: NOW)


def test_start_adopts_a_running_review_of_the_same_head(tmp_path):
    running = summary(status="running", updated_at="2026-10-16T10:01:30Z")
    github = FakeGitHub(comments=[running])
    result = REVIEW.start(github, "o/r", 1, tmp_path / "a.json", [BOT], now=lambda: NOW)
    assert (result["mode"], result["triggered_at"]) == ("adopted", "2026-10-16T10:01:30Z")
    assert github.posted == []


def test_start_refuses_while_an_older_commit_is_under_review(tmp_path):
    running = summary(status="running", commit=OLD_HEAD, updated_at="2026-10-16T10:01:30Z")
    output = tmp_path / "a.json"
    with pytest.raises(REVIEW.ReviewError, match="still reviewing"):
        REVIEW.start(FakeGitHub(comments=[running]), "o/r", 1, output, [BOT], now=lambda: NOW)
    assert not output.exists()


def test_start_ignores_a_stuck_running_review(tmp_path):
    running = summary(status="running", commit=OLD_HEAD, updated_at="2026-10-16T08:00:00Z")
    github = FakeGitHub(comments=[running])
    assert REVIEW.start(github, "o/r", 1, tmp_path / "a.json", [BOT], now=lambda: NOW)["mode"] == "posted"


def test_start_releases_reservation_when_head_moves(tmp_path):
    output = tmp_path / "a.json"
    with pytest.raises(REVIEW.ReviewError, match="before the trigger"):
        REVIEW.start(FakeGitHub(heads=[HEAD, OLD_HEAD]), "o/r", 1, output, [BOT], now=lambda: NOW)
    assert not output.exists()


def test_wait_attaches_inline_findings():
    github = FakeGitHub(reviews=[review()])
    result = REVIEW.wait_for_review(github, attempt(), timeout=1, interval=1)
    assert result["findings"] == [{"severity": "P2", "title": "Tidy up", "path": "a.py", "line": 3, "url": "c"}]


def test_wait_times_out_with_reason():
    ticks = iter([0, 0, 5])
    with pytest.raises(REVIEW.ReviewError, match="timed out"):
        REVIEW.wait_for_review(FakeGitHub(), attempt(), timeout=1, interval=1,
                               clock=lambda: next(ticks), sleep=lambda _: None)


def test_wait_on_a_preparing_attempt_says_nothing_was_posted():
    with pytest.raises(REVIEW.ReviewError, match="before posting"):
        REVIEW.wait_for_review(FakeGitHub(), attempt(status="preparing"), timeout=1, interval=1)


class FakeGraphQL:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def graphql(self, query, **variables):
        self.calls.append(variables)
        return self.pages.pop(0)


def thread(id, resolved=False, author="chatgpt-codex-connector", kind="Bot"):
    return {"id": id, "isResolved": resolved, "isOutdated": False, "path": "a.py", "line": 1, "originalLine": 1,
            "comments": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                         "nodes": [{"body": "**![P1 Badge](x) Bug**", "url": "u", "createdAt": AFTER,
                                    "author": {"login": author, "__typename": kind}}]}}


def page(nodes, next_cursor=None):
    info = {"hasNextPage": next_cursor is not None, "endCursor": next_cursor}
    return {"data": {"repository": {"pullRequest": {"reviewThreads": {"pageInfo": info, "nodes": nodes}}}}}


def test_threads_paginates_and_keeps_only_unresolved_codex_threads():
    github = FakeGraphQL([
        page([thread("T1"), thread("T2", resolved=True)], next_cursor="c1"),
        page([thread("T3", author="human"), thread("T4")]),
    ])
    result = REVIEW.unresolved_threads(github, "o/r", 1, [BOT])
    assert [item["id"] for item in result] == ["T1", "T4"]
    assert result[0]["severity"] == "P1"
    assert github.calls[1]["cursor"] == "c1"


def test_adopted_attempt_accepts_a_review_already_in_its_snapshot():
    # Codex finished between the comments and reviews reads of start().
    done = review()
    state = attempt(mode="adopted", reviews=[done])
    result = evaluate(state=state, reviews=[done])
    assert (result["status"], result["source_id"]) == ("review_ready", 30)


def test_adopted_attempt_still_ignores_reviews_before_the_adopted_start():
    old = review(submitted_at=BEFORE)
    assert evaluate(state=attempt(mode="adopted", reviews=[old]), reviews=[old])["status"] == "pending"


def test_reaction_cannot_clear_head_while_another_commit_is_under_review():
    running = summary(status="running", commit=OLD_HEAD, updated_at=BEFORE)
    reaction = {"id": 50, "content": "+1", "user": {"login": BOT}, "created_at": AFTER}
    result = evaluate(comments=[running], reactions=[reaction])
    assert result["status"] == "pending"


def test_reaction_cannot_clear_head_after_bypassing_a_running_review():
    reaction = {"id": 50, "content": "+1", "user": {"login": BOT}, "created_at": AFTER}
    assert evaluate(state=attempt(bypassed_running=True), reactions=[reaction])["status"] == "pending"


def test_start_records_a_bypassed_stuck_review(tmp_path):
    running = summary(status="running", commit=OLD_HEAD, updated_at="2026-10-16T08:00:00Z")
    output = tmp_path / "a.json"
    REVIEW.start(FakeGitHub(comments=[running]), "o/r", 1, output, [BOT], now=lambda: NOW)
    assert json.loads(output.read_text())["bypassed_running"] is True


def test_threads_fall_back_to_original_line_for_outdated_findings():
    node = {**thread("T1"), "isOutdated": True, "line": None, "originalLine": 42}
    result = REVIEW.unresolved_threads(FakeGraphQL([page([node])]), "o/r", 1, [BOT])
    assert (result[0]["line"], result[0]["outdated"]) == (42, True)


def test_results_sharing_the_trigger_second_are_accepted():
    assert evaluate(comments=[receipt(updated_at=TRIGGER)])["clean"] is True
    assert evaluate(reviews=[review(submitted_at=TRIGGER)])["source"] == "review"
    reaction = {"id": 50, "content": "+1", "user": {"login": BOT}, "created_at": TRIGGER}
    assert evaluate(reactions=[reaction])["source"] == "reaction"


def test_snapshot_items_sharing_the_trigger_second_stay_ignored():
    old = review(submitted_at=TRIGGER)
    assert evaluate(state=attempt(reviews=[old]), reviews=[old])["status"] == "pending"


def test_adopted_running_summary_in_its_own_second_is_not_a_result():
    running = summary(status="running", updated_at=TRIGGER)
    state = attempt(mode="adopted", comments=[running])
    assert evaluate(state=state, comments=[running])["status"] == "pending"


class LostPostGitHub(FakeGitHub):
    """Accepts the trigger but loses the response, like a gh timeout after the POST lands."""

    def command(self, *args):
        self.comments.append({"id": 77, "user": {"login": "me"}, "created_at": TRIGGER,
                              "updated_at": TRIGGER, "body": args[-1].removeprefix("body=")})
        raise REVIEW.ReviewError("timed out")


def test_lost_post_leaves_a_reconcilable_attempt(tmp_path):
    github = LostPostGitHub()
    output = tmp_path / "a.json"
    with pytest.raises(REVIEW.ReviewError, match="outcome unknown"):
        REVIEW.start(github, "o/r", 1, output, [BOT], now=lambda: NOW)
    saved = json.loads(output.read_text())
    assert (saved["status"], saved["trigger_body"]) == ("posting", "@codex review")

    github.reviews.append(review())
    persisted = []
    result = REVIEW.wait_for_review(github, saved, timeout=1, interval=1, save=persisted.append)
    assert result["source_id"] == 30
    assert (persisted[0]["status"], persisted[0]["trigger_id"]) == ("triggered", 77)


def test_reconcile_reports_a_trigger_that_never_landed():
    state = attempt(status="posting", trigger_body="@codex review")
    with pytest.raises(REVIEW.ReviewError, match="never posted"):
        REVIEW.wait_for_review(FakeGitHub(), state, timeout=1, interval=1)


def test_threads_fetch_every_page_of_a_long_discussion():
    long = thread("T1")
    long["comments"]["pageInfo"] = {"hasNextPage": True, "endCursor": "k1"}
    reply = {"body": "late rebuttal", "url": "u2", "createdAt": AFTER, "author": {"login": "human"}}
    rest = {"data": {"node": {"comments": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                                           "nodes": [reply]}}}}
    github = FakeGraphQL([page([long]), rest])
    result = REVIEW.unresolved_threads(github, "o/r", 1, [BOT])
    assert [item["body"] for item in result[0]["discussion"]][-1] == "late rebuttal"
    assert github.calls[1] == {"id": "T1", "cursor": "k1"}


def test_rest_identity_requires_the_exact_bot_login():
    # A user account named after the app has no "[bot]" suffix and must not be trusted.
    impostor = {"login": "chatgpt-codex-connector"}
    assert evaluate(comments=[receipt(user=impostor)])["status"] == "pending"
    reaction = {"id": 50, "content": "+1", "user": impostor, "created_at": AFTER}
    assert evaluate(reactions=[reaction])["status"] == "pending"
    limit = {"id": 40, "user": impostor, "updated_at": AFTER,
             "body": "You have reached your Codex usage limits for code reviews."}
    assert evaluate(comments=[limit])["status"] == "pending"


def test_graphql_identity_requires_the_bot_type():
    github = FakeGraphQL([page([thread("T1", kind="User"), thread("T2")])])
    assert [item["id"] for item in REVIEW.unresolved_threads(github, "o/r", 1, [BOT])] == ["T2"]
