import json
from pathlib import Path
import subprocess
import unittest

from narzedzia.abandon_discussion import abandon_discussion


ROOT = Path(__file__).resolve().parents[1]


class AbandonDiscussionTests(unittest.TestCase):
    def event(self, label="PORZUCONA", action="labeled"):
        return {"action": action, "label": {"name": label},
                "repository": {"full_name": "Fencer4Life/Regulamin_Kadry-SPWS"},
                "discussion": {"number": 28}}

    def run_case(self, *, closed=False, reason=None, labels=None, fail=None, target="OUTDATED"):
        calls = []
        def gh(*args):
            calls.append(args)
            if "workflow" in args:
                if fail == "dispatch":
                    raise subprocess.CalledProcessError(1, args)
                return ""
            if any("mutation" in arg for arg in args):
                if fail == "close":
                    raise subprocess.CalledProcessError(1, args)
                return json.dumps({"data": {"closeDiscussion": {"discussion": {
                    "closed": True, "stateReason": target}}}})
            return json.dumps({"data": {"repository": {"discussion": {
                "id": "D_28", "closed": closed, "stateReason": reason,
                "labels": {"nodes": [{"name": name} for name in
                    (labels if labels is not None else ["PORZUCONA"])],
                    "pageInfo": {"hasNextPage": False}}
            }}}})
        return calls, gh

    def test_label_closes_outdated_then_publishes_without_document_mutation(self):
        calls, gh = self.run_case()
        abandon_discussion(self.event(), gh=gh)
        self.assertEqual(len(calls), 3)
        self.assertIn("reason:OUTDATED", " ".join(calls[1]))
        self.assertEqual(calls[2], ("workflow", "run", "pages.yml", "--repo",
            "Fencer4Life/Regulamin_Kadry-SPWS", "--ref", "main"))

    def test_other_labels_and_events_do_nothing(self):
        for label, action in [("rozstrzygnięta", "labeled"), ("PORZUCONA", "unlabeled")]:
            calls, gh = self.run_case()
            abandon_discussion(self.event(label, action), gh=gh)
            self.assertEqual(calls, [])

    def test_duplicate_closes_and_publishes(self):
        calls, gh = self.run_case(labels=["DUPLIKAT"], target="DUPLICATE")
        abandon_discussion(self.event("DUPLIKAT"), gh=gh)
        self.assertIn("reason:DUPLICATE", " ".join(calls[1]))
        self.assertEqual(calls[-1][0], "workflow")

    def test_duplicate_retry_does_not_close_again(self):
        calls, gh = self.run_case(labels=["DUPLIKAT"], closed=True, reason="DUPLICATE")
        abandon_discussion(self.event("DUPLIKAT"), gh=gh)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[-1][0], "workflow")

    def test_removed_label_is_not_processed_from_stale_event(self):
        calls, gh = self.run_case(labels=[])
        abandon_discussion(self.event(), gh=gh)
        self.assertEqual(len(calls), 1)

    def test_retry_for_already_outdated_discussion_only_republishes(self):
        calls, gh = self.run_case(closed=True, reason="OUTDATED")
        abandon_discussion(self.event(), gh=gh)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[-1][0], "workflow")

    def test_conflicting_decision_labels_or_closure_reason_fail_safely(self):
        for options in [{"labels": ["PORZUCONA", "rozstrzygnięta"]},
                        {"labels": ["PORZUCONA", "redakcja-bez-zmiany-sensu"]},
                        {"labels": ["PORZUCONA", "DUPLIKAT"]},
                        {"closed": True, "reason": "RESOLVED"}]:
            calls, gh = self.run_case(**options)
            with self.assertRaises(ValueError):
                abandon_discussion(self.event(), gh=gh)
            self.assertEqual(len(calls), 1)

    def test_close_failure_does_not_dispatch_release(self):
        calls, gh = self.run_case(fail="close")
        with self.assertRaises(subprocess.CalledProcessError):
            abandon_discussion(self.event(), gh=gh)
        self.assertEqual(len(calls), 2)

    def test_dispatch_failure_is_reported_for_retry(self):
        calls, gh = self.run_case(fail="dispatch")
        with self.assertRaises(subprocess.CalledProcessError):
            abandon_discussion(self.event(), gh=gh)
        self.assertEqual(len(calls), 3)

    def test_workflow_is_scoped_and_does_not_generate_decisions(self):
        workflow = (ROOT / ".github/workflows/abandon-discussion.yml").read_text()
        for fragment in ["types: [labeled]", "github.event.label.name == 'PORZUCONA'",
                         "github.event.label.name == 'DUPLIKAT'",
                         "discussions: write", "actions: write", "contents: read",
                         'python -m narzedzia.abandon_discussion "$GITHUB_EVENT_PATH"']:
            self.assertIn(fragment, workflow)
        for fragment in ["contents: write", "pull-requests: write", "git commit",
                         "create_decision", "build_regulamin", "apply_editorial"]:
            self.assertNotIn(fragment, workflow)
