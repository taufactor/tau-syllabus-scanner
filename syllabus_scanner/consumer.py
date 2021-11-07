import asyncio
import logging
import typing

from syllabus_scanner import defines as syllabus_scanner_defines
from syllabus_scanner import non_persistent_models as syllabus_scanner_non_persistent_models
from syllabus_scanner import page_parser as syllabus_scanner_page_parser

_logger = logging.getLogger(__name__)


class SyllabusConsumer:
    def __init__(self, departments: typing.Sequence[syllabus_scanner_non_persistent_models.Department]):
        self._done = False
        self._courses: typing.List[syllabus_scanner_non_persistent_models.CourseInfo, ...] = []
        self._failures: typing.List[syllabus_scanner_non_persistent_models.CourseGroupParsingFailure, ...] = []
        self.expected_completions = len(departments)

    @property
    def results(self) -> syllabus_scanner_non_persistent_models.ScanResults:
        assert self.is_done
        return syllabus_scanner_non_persistent_models.ScanResults(
            courses=tuple(self._courses),
            failures=tuple(self._failures),
        )

    @property
    def is_done(self) -> bool:
        return self._done

    async def consumer(self, queue: asyncio.Queue) -> None:
        async for page_entry in self.pages(queue):
            _logger.debug("Processing page %s of department %s.", page_entry.page_number, page_entry.department.name)
            parser = syllabus_scanner_page_parser.SyllabusPageParser(page_entry=page_entry)
            parser.parse()
            self._courses.extend(parser.courses)
            self._failures.extend(parser.failures)
            _logger.debug(
                "Done processing page %s of department %s. Total number of courses is %s."
                "Total number of failures is %s.",
                page_entry.page_number,
                page_entry.department.name,
                len(self._courses),
                len(self._failures),
            )
        self._done = True
        _logger.info("Done processing all pages.")

    async def pages(self, queue: asyncio.Queue):
        num_completions = 0
        while num_completions < self.expected_completions:
            page_entry: syllabus_scanner_non_persistent_models.PageEntry = await queue.get()
            if page_entry.is_valid:
                yield page_entry
            else:
                num_completions += 1
            queue.task_done()
