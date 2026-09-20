"""Close a labeled discussion without creating a decision or editing the regulation."""

import json
from pathlib import Path
import subprocess
import sys


REASONS = {"PORZUCONA": "OUTDATED", "DUPLIKAT": "DUPLICATE"}
DECISION_LABELS = {"rozstrzygnięta", "redakcja-bez-zmiany-sensu"}


def call_gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def graphql(gh, query, *variables):
    result = json.loads(gh("api", "graphql", "-f", f"query={query}", *variables))
    if result.get("errors"):
        raise ValueError("GitHub GraphQL zgłosił błąd; nie kontynuowano operacji")
    return result["data"]


def abandon_discussion(event, *, gh=call_gh):
    label = event.get("label", {}).get("name")
    if event.get("action") != "labeled" or label not in REASONS:
        return "Pominięto: to nie jest nadanie etykiety zamykającej."
    repo = event["repository"]["full_name"]
    owner, name = repo.split("/")
    number = int(event["discussion"]["number"])
    data = graphql(gh,
        "query($owner:String!,$name:String!,$number:Int!){"
        "repository(owner:$owner,name:$name){discussion(number:$number){"
        "id closed stateReason labels(first:100){nodes{name} pageInfo{hasNextPage}}}}}",
        "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"number={number}")
    discussion = data["repository"]["discussion"]
    if discussion is None:
        raise ValueError("Nie znaleziono dyskusji")
    if discussion["labels"]["pageInfo"]["hasNextPage"]:
        raise ValueError("Niepełna lista etykiet; wymagana kontrola ręczna")
    labels = {item["name"] for item in discussion["labels"]["nodes"]}
    if label not in labels:
        return "Pominięto: etykieta została już usunięta."
    if labels & (DECISION_LABELS | (set(REASONS) - {label})):
        raise ValueError("Sprzeczne etykiety dyskusji; usuń nieaktualną etykietę przed ponowieniem")
    reason = REASONS[label]
    if discussion["closed"]:
        if discussion["stateReason"] != reason:
            raise ValueError("Dyskusję zamknięto z innym powodem; wymagana kontrola ręczna")
    else:
        # The interpolated reason comes only from the fixed mapping, never user text.
        result = graphql(gh,
            "mutation($discussionId:ID!){closeDiscussion(input:{discussionId:$discussionId,"
            f"reason:{reason}" + "}){discussion{closed stateReason}}}",
            "-f", f"discussionId={discussion['id']}")
        closed = result["closeDiscussion"]["discussion"]
        if not closed["closed"] or closed["stateReason"] != reason:
            raise ValueError("GitHub nie potwierdził zamknięcia z oczekiwanym powodem")
    # GITHUB_TOKEN mutations do not reliably trigger another workflow. Dispatch explicitly.
    gh("workflow", "run", "pages.yml", "--repo", repo, "--ref", "main")
    return f"Dyskusja #{number}: {reason}. Zlecono publikację strony."


if __name__ == "__main__":
    try:
        print(abandon_discussion(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
    except (ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Nie zakończono automatyzacji: {error}", file=sys.stderr)
        sys.exit(1)
