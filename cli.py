#!/usr/bin/env python3
import argparse
import json
import logging
import typing
from datetime import datetime

from syllabus_scanner import non_persistent_models as syllabus_scanner_non_persistent_models
from syllabus_scanner import scanner


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
    )


def get_language(language_name: str) -> syllabus_scanner_non_persistent_models.Language:
    return getattr(syllabus_scanner_non_persistent_models.Language, language_name)


def get_departments(
        department_names: typing.Sequence[str],
) -> typing.Sequence[syllabus_scanner_non_persistent_models.Department]:
    return tuple(
        getattr(syllabus_scanner_non_persistent_models.Department, department_name)
        for department_name in sorted(set(department_names))
    )


def get_default_year() -> int:
    today = datetime.today()
    # Move to next year on August.
    # Notice that a academic year is always the one that is starts at.
    # So between January-July we still need to take the previous year.
    # After that, we move to the next school year.
    default_year = today.year if today.month >= 8 else today.year - 1
    return default_year


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lang",
        choices=tuple(language.name for language in syllabus_scanner_non_persistent_models.Language.all()),
        default=syllabus_scanner_non_persistent_models.Language.hebrew.name,
        help="The syllabus language to load",
    )
    parser.add_argument(
        "--json",
        type=str,
        required=True,
        help="The file path to store the result at",
    )
    parser.add_argument(
        "--year",
        default=get_default_year(),
        type=int,
        help="The Gregorian year the academic year starts at",
    )
    parser.add_argument(
        "--department",
        choices=tuple(department.name for department in syllabus_scanner_non_persistent_models.Department.all()),
        nargs="+",
        help="The department name(s) to scan",
    )
    return parser.parse_args()


def main() -> None:
    setup_logger()
    args = get_arguments()

    results = scanner.scan(
        language=get_language(args.lang),
        year=args.year,
        departments=get_departments(department_names=args.department or ()),
    )

    with open(args.json, "w", encoding="utf-8") as json_file:
        json.dump(
            obj=results.serialize(),
            fp=json_file,
            ensure_ascii=False,
        )

    print(results.serialize_text())


if __name__ == "__main__":
    main()
