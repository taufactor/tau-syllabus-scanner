import typing

from syllabus_scanner import consumer as syllabus_scanner_consumer
from syllabus_scanner import loader as syllabus_scanner_loader
from syllabus_scanner import non_persistent_models as syllabus_scanner_non_persistent_models


def scan(
        language: syllabus_scanner_non_persistent_models.Language,
        year: int,
        departments: typing.Sequence[syllabus_scanner_non_persistent_models.Department] = (),
) -> syllabus_scanner_non_persistent_models.ScanResults:
    """
    Scan the syllabus site of Tel-Aviv University and retrieve courses information.
    :param language: The syllabus language.
    :param year: The Gregorian year the academic year starts at.
    :param departments: The departments to scan. If none are provided then scan all departments.
    :return: A ScanResults object containing the collected objects from the syllabus scan.
    """
    departments = departments or syllabus_scanner_non_persistent_models.Department.all()

    loader = syllabus_scanner_loader.SyllabusLoader(language=language, year=year, departments=departments)
    consumer = syllabus_scanner_consumer.SyllabusConsumer(departments=departments)
    loader.set_consumer(consumer.consumer)
    loader.run()
    return consumer.results
