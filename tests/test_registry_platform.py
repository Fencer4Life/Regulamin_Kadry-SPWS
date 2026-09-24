from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PLATFORM_FILES = (
    "_config.yml",
    "Gemfile",
    "_layouts/default.html",
    "_layouts/decision.html",
    "_includes/decision-card.html",
    "assets/rejestr.css",
    "assets/rejestr.js",
    "assets/dyskusje.js",
    "_data/discussions.json",
    ".github/workflows/validate.yml",
    ".github/workflows/pages.yml",
)


class RegistryPlatformTests(unittest.TestCase):
    def test_required_platform_files_exist(self):
        missing = [path for path in REQUIRED_PLATFORM_FILES if not (ROOT / path).is_file()]
        self.assertEqual(missing, [], f"Brak plików platformy rejestru: {missing}")

    def test_index_exposes_search_and_agreed_filters(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        required = (
            'id="search"',
            'id="filter-type"',
            'id="filter-status"',
            'id="filter-season"',
            'id="filter-subject"',
            'id="filter-effect"',
            'id="page-size"',
            'id="pagination-top"',
            'id="pagination-bottom"',
            "site.decyzje",
            "decision-card.html",
        )
        missing = [fragment for fragment in required if fragment not in index]
        self.assertEqual(missing, [], f"Indeks nie zawiera wyszukiwarki lub filtrów: {missing}")

    def test_newest_decisions_are_rendered_first(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("site.decyzje | sort: 'slug' | reverse", index)

    def test_header_links_to_discussions_and_new_proposal(self):
        layout = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
        self.assertIn("Otwarte dyskusje", layout)
        self.assertIn("site.data.discussions.open_items.size", layout)
        self.assertIn("Otwórz nową dyskusję", layout)
        self.assertTrue((ROOT / "dyskusje.html").is_file())

    def test_discussion_page_separates_open_and_closed_and_links_decisions(self):
        page = (ROOT / "dyskusje.html").read_text(encoding="utf-8")
        for fragment in (
            "site.data.discussions",
            "snapshot.open_items",
            "snapshot.closed_items",
            "Otwarte dyskusje",
            "Zamknięte dyskusje i decyzje",
            "discussion_url",
            "Przyjęta",
            "Porzucona",
            "Duplikat",
            "Zamknięta",
            "Zobacz decyzję",
        ):
            self.assertIn(fragment, page)
        self.assertFalse((ROOT / "_data" / "open_discussions.json").exists())

    def test_open_discussion_cards_have_the_approved_ux_contract(self):
        page = (ROOT / "dyskusje.html").read_text(encoding="utf-8")
        css = (ROOT / "assets/rejestr.css").read_text(encoding="utf-8")
        script = (ROOT / "assets/dyskusje.js").read_text(encoding="utf-8")
        layout = (ROOT / "_layouts/default.html").read_text(encoding="utf-8")
        for fragment in (
            'class="discussion-list discussion-grid"',
            'class="discussion-rail discussion-age-fresh"',
            'class="discussion-number"',
            'class="discussion-priority discussion-priority-{{ discussion.priority | downcase }}"',
            '<span>priorytet</span><strong>{{ discussion.priority | escape }}</strong>',
            'data-created-at="{{ discussion.created_at }}"',
            'class="discussion-coordinator"',
            'class="discussion-pills"',
            'class="discussion-comments"',
            "remove_first: '[Dyskusja]'",
            "discussion.depends_on",
            "discussion.labels",
            "Odśwież dane",
        ):
            self.assertIn(fragment, page)
        for fragment in (
            ".discussion-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));",
            ".discussion-rail",
            ".discussion-age-fresh",
            ".discussion-age-medium",
            ".discussion-age-long",
        ):
            self.assertIn(fragment, css)
        self.assertRegex(css, r"\.discussion-pills\s*\{[^}]*margin-top:\s*auto;")
        self.assertRegex(css, r"\.discussion-comments\s*\{[^}]*margin-top:\s*12px;")
        self.assertRegex(css, r"\.discussion-priority\s*\{[^}]*width:\s*100%;[^}]*max-width:\s*100%;[^}]*overflow:\s*hidden;")
        for fragment in ("calendarDayAge", "discussion-age-fresh", "odswiez", "Date.now()"):
            self.assertIn(fragment, script)
        self.assertIn("assets/dyskusje.js", layout)

    def test_layout_cache_busts_css_and_javascript_after_each_release(self):
        layout = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
        version = "?v={{ site.time | date: '%s' }}"
        self.assertIn("rejestr.css' | relative_url }}" + version, layout)
        self.assertIn("dyskusje.js' | relative_url }}" + version, layout)

    def test_closed_discussions_use_compact_paginated_sidebar(self):
        page = (ROOT / "dyskusje.html").read_text(encoding="utf-8")
        css = (ROOT / "assets/rejestr.css").read_text(encoding="utf-8")
        script = (ROOT / "assets/dyskusje.js").read_text(encoding="utf-8")
        for fragment in (
            'class="discussion-page-layout"',
            'class="discussion-archive-panel"',
            'data-discussion-archive-toggle',
            'Zamknięte dyskusje ({{ snapshot.closed_items.size }})',
            'class="discussion-archive-card"',
            'data-discussion-archive-item',
            'data-discussion-archive-previous',
            'data-discussion-archive-next',
            'data-discussion-archive-page',
        ):
            self.assertIn(fragment, page)
        for fragment in (
            ".discussion-page-layout",
            ".discussion-archive-panel",
            ".discussion-archive-card",
            ".discussion-archive-toggle",
        ):
            self.assertIn(fragment, css)
        for fragment in (
            "archivePageSize = 20",
            "data-discussion-archive-item",
            "data-discussion-archive-toggle",
            "data-discussion-archive-previous",
            "data-discussion-archive-next",
        ):
            self.assertIn(fragment, script)

    def test_config_publishes_decision_collection(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        for fragment in ("decyzje:", "output: true", "permalink: /decyzje/:name/", "- .DS_Store"):
            self.assertIn(fragment, config)

    def test_source_link_uses_the_explicit_repository_url(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        layout = (ROOT / "_layouts" / "decision.html").read_text(encoding="utf-8")
        self.assertIn(
            "repository_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS",
            config,
        )
        self.assertIn("site.repository_url", layout)
        self.assertNotIn("site.github.repository_url", layout)

    def test_views_derive_the_public_decision_number_from_the_slug(self):
        card = (ROOT / "_includes" / "decision-card.html").read_text(encoding="utf-8")
        layout = (ROOT / "_layouts" / "decision.html").read_text(encoding="utf-8")
        self.assertIn("include.decision.slug | slice: 0, 6 | upcase", card)
        self.assertNotIn("include.decision.id", card)
        self.assertIn("page.slug | slice: 0, 6 | upcase", layout)
        self.assertNotIn("page.id", layout)

    def test_pull_requests_validate_but_only_main_deploys_pages(self):
        validate = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertTrue(validate.startswith("name: CI\n"))
        self.assertTrue(pages.startswith("name: Release\n"))
        self.assertIn("pull_request:", validate)
        self.assertIn("workflow_dispatch:", validate)
        self.assertIn("python -m unittest discover -s tests -v", validate)
        self.assertIn("bundle exec jekyll build --strict_front_matter", validate)
        self.assertIn("branches: [main]", pages)
        self.assertIn("workflow_dispatch:", pages)
        self.assertIn("pages: write", pages)
        self.assertIn("id-token: write", pages)
        self.assertIn("test:\n    runs-on: ubuntu-latest", pages)
        self.assertIn("python -m unittest discover -s tests -v", pages)
        self.assertIn("needs: [build, test]", pages)
        self.assertIn("bundle exec jekyll build --strict_front_matter", pages)
        self.assertNotIn("actions/jekyll-build-pages", pages)
        self.assertNotIn("pull_request:", pages)

    def test_pages_refreshes_discussions_safely(self):
        pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        for fragment in (
            "schedule:",
            "*/15",
            "discussion:",
            "discussions: read",
            "sync_discussions.py",
            "states:[OPEN,CLOSED]",
            "closedAt",
            "body",
            "pageInfo",
            "endCursor",
            "--paginate --slurp",
            "_data/discussions.json",
        ):
            self.assertIn(fragment, pages)

    def test_decision_creation_workflow_is_idempotent_and_serialized(self):
        workflow = ROOT / ".github" / "workflows" / "create-decision.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for fragment in ("rozstrzygnięta", "concurrency:", "discussion_url", "--draft", "decyzja"):
            self.assertIn(fragment, text)
        self.assertNotIn("FORMULARZ-ROZSTRZYGNIECIA", text)
        for fragment in ("gh pr list", "git switch --track", "istniejącej roboczej gałęzi"):
            self.assertIn(fragment, text)

    def test_fast_editorial_path_builds_tests_and_commits_markdown_with_docx(self):
        workflow = (ROOT / ".github" / "workflows" / "create-decision.yml").read_text(
            encoding="utf-8"
        )
        for fragment in (
            "redakcja-bez-zmiany-sensu",
            "narzedzia.apply_editorial_change",
            "prepare_regulamin normalize-and-build",
            "normalize_regulamin_markdown",
            "REGULAMIN_DOCX_PATH",
            "docx_parity",
            "actions/upload-artifact",
            "regulamin-candidate",
        ):
            self.assertIn(fragment, workflow)

    def test_ci_builds_and_exposes_the_candidate_docx_for_pr_review(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        for fragment in (
            "build_regulamin_docx",
            "prepare_regulamin verify",
            "normalize_regulamin_markdown",
            "REGULAMIN_DOCX_PATH",
            "docx_parity",
            "validate_regulation_change.py",
            "actions/upload-artifact",
            "regulamin-candidate",
        ):
            self.assertIn(fragment, workflow)

    def test_documentation_treats_markdown_automation_as_current(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("Źródłem kanonicznym jest kontrolowany Markdown", contributing)
        self.assertIn("sekcji `Artifacts`", contributing)
        self.assertIn("normalize-and-build", contributing)
        self.assertIn("source-draft", contributing)
        self.assertIn("kanoniczny Markdown", readme)
        self.assertIn("ZTP", readme)
        self.assertIn("BRUDNOPIS ZE ŹRÓDŁA — DO OPRACOWANIA", readme)
        self.assertIn("normalizuje strukturę", readme)
        self.assertNotIn("Planowana ścieżka Markdown", readme)
        self.assertNotIn("Planowane przejście na Markdown", contributing)

    def test_merged_decision_closes_its_discussion_as_resolved(self):
        workflow = ROOT / ".github" / "workflows" / "resolve-discussion.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for fragment in ("pull_request:", "workflow_dispatch:", "pr_number:", "closed", "merged", "resolve_discussion.py", "RESOLVED", "closeDiscussion", "actions: write", "gh workflow run pages.yml --ref main"):
            self.assertIn(fragment, text)
        self.assertLess(text.index("closeDiscussion"), text.index("gh workflow run pages.yml --ref main"))

    def test_architecture_decision_index_keeps_newest_entries_first(self):
        index = (ROOT / "dokumentacja" / "adr" / "index.html").read_text(encoding="utf-8")
        self.assertIn("najnowszy ADR znajduje się zawsze na samej górze", index)
        numbers = [int(value) for value in re.findall(r"<h2>ADR-(\d+)", index)]
        self.assertEqual(numbers, sorted(numbers, reverse=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
