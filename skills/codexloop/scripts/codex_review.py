#!/usr/bin/env python3
"""Trigger and wait for a Codex code review of one GitHub PR revision.

Adapted from greploop's github_review.py (greptileai/skills, as reworked in
michaelshimeles/skills). MIT, Copyright (c) 2026 Greptile AI; see
LICENSE-greploop beside this file.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_BOTS = ("chatgpt-codex-connector[bot]",)
STUCK_REVIEW_SECONDS = 1800
SUMMARY_MARKER = "<!-- codex-pull-request-review-summary -->"
STATE = re.compile(r"<!--\s*codex-review-state:v1\s+(\{.*?\})\s*-->", re.S)
REVIEWED = re.compile(r"\*\*Reviewed commit:\*\*\s*`([0-9a-f]{7,40})`", re.I)
BADGE = re.compile(r"!\[(P\d) Badge\]")
TITLE = re.compile(r"^\s*\*\*(.*?)\*\*\s*$", re.M)

THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line originalLine
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes { body url createdAt author { login __typename } }
          }
        }
      }
    }
  }
}
"""

THREAD_COMMENTS_QUERY = """
query($id: ID!, $cursor: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { body url createdAt author { login __typename } }
      }
    }
  }
}
"""


class ReviewError(RuntimeError):
    pass


def login(user):
    return (user or {}).get("login", "")


def by_bot(item, bots):
    # REST logins carry the "[bot]" suffix that user accounts cannot register; compare
    # exactly, or a user named after the app could forge receipts and reactions.
    return login(item.get("user")) in bots


def by_graphql_bot(author, bots):
    # GraphQL drops the suffix, so require the Bot type before comparing the bare login.
    return ((author or {}).get("__typename") == "Bot"
            and login(author) in {bot.removesuffix("[bot]") for bot in bots})


def review_state(body):
    """Parse the code-review entry of the summary comment's state marker."""
    if SUMMARY_MARKER not in body:
        return None
    match = STATE.search(body)
    if not match:
        return None
    try:
        return json.loads(match[1]).get("code_review") or None
    except json.JSONDecodeError:
        return None


def reviewed_commit(body):
    match = REVIEWED.search(body)
    return match[1].lower() if match else None


def is_clean_receipt(body):
    return "didn't find any major issues" in body.replace("’", "'").lower()


def is_usage_limit(body):
    return "usage limits" in body.lower() and "codex" in body.lower()


def finding(comment):
    body = comment.get("body") or ""
    badge = BADGE.search(body)
    title = TITLE.search(body)
    heading = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)", "", title[1]).strip() if title else ""
    return {
        "severity": badge[1] if badge else None,
        "title": heading or body.strip().splitlines()[0][:120] if body.strip() else "",
        "path": comment.get("path"),
        "line": comment.get("line") or comment.get("original_line"),
        "url": comment.get("html_url") or comment.get("url"),
    }


def changed(item, old):
    return old is None or item.get("body") != old.get("body")


def fresh(item, stamp, old, triggered, adopted, commit_linked=True):
    """True when an item is a result of this attempt rather than earlier activity."""
    # GitHub timestamps have one-second precision, so an item the snapshot did not
    # contain (or whose body changed) counts even when it shares the trigger's second.
    if changed(item, old):
        return (stamp or "") >= triggered
    # Adopted attempts snapshot after their review began, so their own result can sit
    # unchanged in the snapshot, possibly within the adopted start's second. A result tied
    # to the head is valid whichever run produced it; a commit-less reaction is not.
    if not adopted:
        return False
    return (stamp or "") >= triggered if commit_linked else (stamp or "") > triggered


def outstanding_elsewhere(state, head):
    """True when the summary shows a not-yet-finished review of another commit (running or queued)."""
    commit = (state or {}).get("commit_sha")
    return bool(commit) and commit != head and state.get("status") not in ("completed", "failed")


def evaluate(attempt, current_head, comments, reviews, reactions):
    """Return a fresh Codex review result for the current head, or a reason to keep waiting."""
    if current_head != attempt["head"]:
        raise ReviewError("PR head changed; start a new attempt for the new revision")
    triggered = attempt["triggered_at"]
    bots = attempt["bots"]
    adopted = attempt.get("mode") == "adopted"

    summary = None
    other_running = False
    clean = None
    old_comments = {str(item["id"]): item for item in attempt["comments"]}
    for comment in comments:
        if not by_bot(comment, bots):
            continue
        body = comment.get("body") or ""
        state = review_state(body)
        if outstanding_elsewhere(state, current_head):
            other_running = True
        old = old_comments.get(str(comment["id"]))
        if state is not None and old is not None and state == review_state(old.get("body") or ""):
            # Only the code-review state matters; edits elsewhere in the shared summary
            # (the security review, for example) carry no new code-review result.
            continue
        if not fresh(comment, comment.get("updated_at"), old, triggered, adopted):
            continue
        if is_usage_limit(body):
            raise ReviewError(f"Codex usage limit reached: {comment.get('html_url')}")
        if state is not None:
            if state.get("commit_sha") == current_head:
                if summary is None or comment["updated_at"] > summary[1]["updated_at"]:
                    summary = (state, comment)
            continue
        commit = reviewed_commit(body)
        if is_clean_receipt(body) and commit and current_head.startswith(commit):
            clean = comment

    old_reviews = {str(item["id"]): item for item in attempt["reviews"]}
    fresh_reviews = [
        item for item in reviews
        if by_bot(item, bots)
        and item.get("commit_id") == current_head
        and fresh(item, item.get("submitted_at"), old_reviews.get(str(item["id"])), triggered, adopted)
    ]
    if fresh_reviews:
        review = max(fresh_reviews, key=lambda item: (item["submitted_at"], item["id"]))
        return {
            "status": "review_ready", "clean": False, "head": current_head,
            "source": "review", "source_id": review["id"], "url": review.get("html_url"),
            "updated_at": review["submitted_at"], "body": review.get("body") or "",
        }
    if clean:
        return {
            "status": "review_ready", "clean": True, "head": current_head,
            "source": "comment", "source_id": clean["id"], "url": clean.get("html_url"),
            "updated_at": clean["updated_at"], "body": clean.get("body") or "",
        }
    if summary:
        state, comment = summary
        status = state.get("status")
        if status == "failed":
            raise ReviewError(f"Codex reported a failed review: {comment.get('html_url')}")
        if status == "completed" and state.get("has_any_findings") is False:
            return {
                "status": "review_ready", "clean": True, "head": current_head,
                "source": "summary", "source_id": comment["id"], "url": comment.get("html_url"),
                "updated_at": comment["updated_at"], "body": comment.get("body") or "",
            }
        if status == "completed":
            return {"status": "pending", "reason": "summary reports findings; waiting for the review to post"}
        return {"status": "pending", "reason": f"Codex review is {status or 'queued'}"}

    if other_running or attempt.get("bypassed_running"):
        # A 👍 names no commit; while another review may still finish, it cannot clear this head.
        return {"status": "pending", "reason": "no commit-linked Codex result for the current head"}
    old_reactions = {str(item["id"]): item for item in attempt.get("reactions", [])}
    for reaction in reactions:
        if (reaction.get("content") == "+1" and by_bot(reaction, bots)
                and fresh(reaction, reaction.get("created_at"), old_reactions.get(str(reaction["id"])),
                          triggered, adopted, commit_linked=False)):
            # The head was verified unchanged since the trigger, but the reaction names no commit.
            return {
                "status": "review_ready", "clean": True, "head": current_head,
                "source": "reaction", "source_id": reaction["id"], "url": None,
                "updated_at": reaction["created_at"], "body": "",
            }
    return {"status": "pending", "reason": "no fresh Codex review tied to the current head"}


class GitHub:
    def command(self, *args):
        result = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise ReviewError(result.stderr.strip() or "gh command failed")
        return json.loads(result.stdout)

    def pages(self, endpoint, key=None):
        pages = self.command("api", "--paginate", "--slurp", endpoint)
        return [item for page in pages for item in (page[key] if key else page)]

    def head(self, repo, pr):
        return self.command("api", f"repos/{repo}/pulls/{pr}")["head"]["sha"]

    def snapshot(self, repo, pr):
        return {
            "comments": self.pages(f"repos/{repo}/issues/{pr}/comments?per_page=100"),
            "reviews": self.pages(f"repos/{repo}/pulls/{pr}/reviews?per_page=100"),
            "reactions": self.pages(f"repos/{repo}/issues/{pr}/reactions?per_page=100"),
        }

    def review_comments(self, repo, pr, review_id):
        return self.pages(f"repos/{repo}/pulls/{pr}/reviews/{review_id}/comments?per_page=100")

    def graphql(self, query, **variables):
        args = ["api", "graphql", "-f", f"query={query}"]
        for key, value in variables.items():
            if value is not None:
                args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
        return self.command(*args)


def utc_now():
    return datetime.now(timezone.utc)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def latest_summary(comments, bots):
    summaries = [
        (state, comment) for comment in comments
        if by_bot(comment, bots) and (state := review_state(comment.get("body") or "")) is not None
    ]
    return max(summaries, key=lambda item: item[1].get("updated_at") or "", default=None)


def start(github, repo, pr, output, bots, focus=None, stuck_after=STUCK_REVIEW_SECONDS, force=False, now=utc_now):
    # Reserve the path before posting so rerunning a command cannot post twice.
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump({"status": "preparing", "repo": repo, "pr": pr}, stream)
    try:
        head = github.head(repo, pr)
        snapshot = github.snapshot(repo, pr)
        attempt = {"repo": repo, "pr": pr, "head": head, "bots": list(bots), **snapshot}
        current = latest_summary(snapshot["comments"], bots)
        if current:
            # A running or queued review of another commit can still post a commit-less 👍;
            # recorded even when start proceeds past it, so that reaction never counts.
            attempt["bypassed_running"] = outstanding_elsewhere(current[0], head)
        if current and not force:
            state, comment = current
            fresh = parse_time(comment["updated_at"]) > now() - timedelta(seconds=stuck_after)
            if state.get("status") == "running" and fresh:
                if state.get("commit_sha") == head:
                    # A review of this exact revision is already underway (for example an
                    # automatic review on push); adopt it instead of queueing a duplicate.
                    attempt.update(status="triggered", mode="adopted", trigger_id=None,
                                   triggered_at=comment["updated_at"])
                    output.write_text(json.dumps(attempt, indent=2) + "\n")
                    return {key: value for key, value in attempt.items() if key not in snapshot}
                raise ReviewError(
                    f"Codex is still reviewing {state.get('commit_sha')}; wait for it to finish, then rerun start. "
                    f"Reviews running longer than {stuck_after}s are treated as stuck; pass --force to post anyway."
                )
        if github.head(repo, pr) != head:
            raise ReviewError("PR head changed before the trigger")
    except BaseException:
        # Only release the reservation before posting the trigger.
        output.unlink()
        raise
    body = "@codex review" + (f" {focus}" if focus else "")
    # Persist everything needed to reconcile before posting: if the POST outcome is
    # lost, `wait` can find the comment instead of anyone posting a second trigger.
    attempt.update(status="posting", mode="posted", trigger_body=body)
    output.write_text(json.dumps(attempt, indent=2) + "\n")
    try:
        comment = github.command(
            "api", f"repos/{repo}/issues/{pr}/comments", "--method", "POST", "-f", f"body={body}",
        )
    except (ReviewError, subprocess.TimeoutExpired) as error:
        raise ReviewError(f"trigger outcome unknown ({error}); run wait on {output} to reconcile") from error
    attempt.update(status="triggered", trigger_id=comment["id"], triggered_at=comment["created_at"])
    output.write_text(json.dumps(attempt, indent=2) + "\n")
    return {key: value for key, value in attempt.items() if key not in snapshot}


def reconcile(github, attempt):
    """Recover the trigger of an attempt whose POST outcome was lost."""
    known = {str(item["id"]) for item in attempt["comments"]}
    posted = [
        comment for comment in github.snapshot(attempt["repo"], attempt["pr"])["comments"]
        if str(comment["id"]) not in known and (comment.get("body") or "").strip() == attempt["trigger_body"]
    ]
    if not posted:
        raise ReviewError("the trigger was never posted; remove the attempt file and rerun start")
    comment = min(posted, key=lambda item: (item["created_at"], item["id"]))
    return {**attempt, "status": "triggered", "trigger_id": comment["id"], "triggered_at": comment["created_at"]}


def wait_for_review(github, attempt, timeout, interval, clock=time.monotonic, sleep=time.sleep, save=None):
    if attempt.get("status") == "posting":
        attempt = reconcile(github, attempt)
        if save:
            save(attempt)
    if attempt.get("status") == "preparing":
        # start writes "posting" before it posts, so nothing was posted for this attempt.
        raise ReviewError("start stopped before posting; remove the attempt file and rerun start")
    if attempt.get("status") != "triggered":
        raise ReviewError("attempt has no confirmed trigger; inspect the PR before retrying")
    repo, pr = attempt["repo"], attempt["pr"]
    deadline = clock() + timeout
    while True:
        head = github.head(repo, pr)
        if head != attempt["head"]:
            raise ReviewError("PR head changed; start a new attempt for the new revision")
        snapshot = github.snapshot(repo, pr)
        result = evaluate(attempt, github.head(repo, pr), **snapshot)
        if result["status"] == "review_ready":
            if result["source"] == "review":
                comments = github.review_comments(repo, pr, result["source_id"])
                result["findings"] = [finding(comment) for comment in comments]
            else:
                result["findings"] = []
            return result
        remaining = deadline - clock()
        if remaining <= 0:
            raise ReviewError(f"review timed out: {result['reason']}")
        sleep(min(interval, remaining))


def thread_comments(github, node):
    """All comments of one review thread, following the nested connection's pages."""
    connection = node["comments"]
    comments = list(connection["nodes"])
    while connection["pageInfo"]["hasNextPage"]:
        data = github.graphql(THREAD_COMMENTS_QUERY, id=node["id"], cursor=connection["pageInfo"]["endCursor"])
        connection = data["data"]["node"]["comments"]
        comments += connection["nodes"]
    return comments


def unresolved_threads(github, repo, pr, bots):
    owner, name = repo.split("/", 1)
    threads, cursor = [], None
    while True:
        data = github.graphql(THREADS_QUERY, owner=owner, name=name, number=pr, cursor=cursor)
        page = data["data"]["repository"]["pullRequest"]["reviewThreads"]
        for node in page["nodes"]:
            comments = node["comments"]["nodes"]
            if node["isResolved"] or not comments or not by_graphql_bot(comments[0]["author"], bots):
                continue
            first = finding({**comments[0], "path": node["path"], "line": node["line"],
                             "original_line": node["originalLine"]})
            threads.append({
                "id": node["id"], "outdated": node["isOutdated"], **first,
                "discussion": [{"author": login(item["author"]), "body": item["body"]}
                               for item in thread_comments(github, node)],
            })
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        cursor = page["pageInfo"]["endCursor"]


def resolve_threads(github, thread_ids):
    fields = "\n".join(
        f'  t{index}: resolveReviewThread(input: {{threadId: "{thread}"}}) {{ thread {{ id isResolved }} }}'
        for index, thread in enumerate(thread_ids)
    )
    data = github.graphql("mutation {\n" + fields + "\n}")["data"]
    return [value["thread"] for value in data.values()]


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def thread_id(value):
    if not re.fullmatch(r"[A-Za-z0-9_=-]+", value):
        raise argparse.ArgumentTypeError("not a GraphQL node ID")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("start", help="snapshot state and post one @codex review trigger")
    begin.add_argument("--repo", required=True, help="owner/repository")
    begin.add_argument("--pr", type=positive, required=True)
    begin.add_argument("--output", type=Path, required=True)
    begin.add_argument("--focus", help="extra review instructions appended after '@codex review'")
    begin.add_argument("--bot", action="append", help="exact trusted login; repeat for multiple bots")
    begin.add_argument("--stuck-after", type=positive, default=STUCK_REVIEW_SECONDS,
                       help="seconds after which a running Codex review no longer blocks a new trigger")
    begin.add_argument("--force", action="store_true", help="post a trigger even while a review is running")
    wait = commands.add_parser("wait", help="read results without posting another trigger")
    wait.add_argument("attempt", type=Path)
    wait.add_argument("--timeout", type=positive, default=900)
    wait.add_argument("--interval", type=positive, default=15)
    threads = commands.add_parser("threads", help="list unresolved Codex review threads")
    threads.add_argument("--repo", required=True)
    threads.add_argument("--pr", type=positive, required=True)
    threads.add_argument("--bot", action="append")
    resolve = commands.add_parser("resolve", help="resolve the given review thread IDs")
    resolve.add_argument("thread_ids", nargs="+", type=thread_id)
    args = parser.parse_args()
    github = GitHub()
    try:
        if args.command == "start":
            result = start(github, args.repo, args.pr, args.output, args.bot or DEFAULT_BOTS,
                           args.focus, args.stuck_after, args.force)
        elif args.command == "wait":
            result = wait_for_review(
                github, json.loads(args.attempt.read_text()), args.timeout, args.interval,
                save=lambda attempt: args.attempt.write_text(json.dumps(attempt, indent=2) + "\n"),
            )
        elif args.command == "threads":
            result = unresolved_threads(github, args.repo, args.pr, args.bot or DEFAULT_BOTS)
        else:
            result = resolve_threads(github, args.thread_ids)
        print(json.dumps(result, indent=2))
        return 0
    except (ReviewError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "error", "message": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
