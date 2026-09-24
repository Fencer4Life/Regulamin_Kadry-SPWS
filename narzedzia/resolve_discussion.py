"""Read and validate the source discussion number from a decision card."""

import argparse
import re
from pathlib import Path


DISCUSSION_URL = re.compile(
    r"https://github\.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/(\d+)"
)


def discussion_number_from_card(path: Path) -> int:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("discussion_url:"):
            continue
        value = line.removeprefix("discussion_url:").strip()
        match = DISCUSSION_URL.fullmatch(value)
        if match:
            return int(match.group(1))
        break
    raise ValueError(f"Niepoprawny discussion_url w karcie decyzji: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path)
    args = parser.parse_args()
    print(discussion_number_from_card(args.card))


if __name__ == "__main__":
    main()
