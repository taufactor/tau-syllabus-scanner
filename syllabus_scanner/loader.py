import asyncio
import logging
import typing

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag

from syllabus_scanner import defines as syllabus_scanner_defines
from syllabus_scanner import non_persistent_models as syllabus_scanner_non_persistent_models

_logger = logging.getLogger(__name__)


class SyllabusLoader:
    def __init__(
            self,
            language: syllabus_scanner_non_persistent_models.Language,
            year: int,
            departments: typing.Sequence[syllabus_scanner_non_persistent_models.Department],
    ):
        self._language = language
        self._year = year
        self.departments = departments
        queue_size = len(self.departments) * syllabus_scanner_defines.PAGE_QUEUE_SIZE_MULTIPLIER
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.consumer: typing.Optional[asyncio.Task] = None

    async def _load_syllabus_pages(self, department: syllabus_scanner_non_persistent_models.Department) -> None:
        async with ClientSession(headers=syllabus_scanner_defines.HEADERS) as session:
            page_number = 1
            first_page = await self._get_first_page(session=session, department=department)
            parsed_page = BeautifulSoup(first_page, features="html.parser")
            parsed_body = parsed_page.body
            if parsed_body is None:
                _logger.error(F"Page number %s of department %s does not have a body.", page_number, department.name)
                raise ValueError(F"Page number {page_number} of department {department.name} does not have a body.")

            page_entry = syllabus_scanner_non_persistent_models.PageEntry(
                department=department,
                page_number=page_number,
                body=parsed_body,
            )
            await self.queue.put(page_entry)
            _logger.debug("Loaded page %s of department %s.", page_number, department.name)

            while True:
                next_page = await self._get_next_page(session=session, body=parsed_body)
                if next_page is None:
                    break
                page_number += 1
                parsed_page = BeautifulSoup(next_page, features="html.parser")
                parsed_body = parsed_page.body
                if parsed_body is None:
                    raise ValueError(F"Page number {page_number} does not have a body.")

                page_entry = syllabus_scanner_non_persistent_models.PageEntry(
                    department=department,
                    page_number=page_number,
                    body=parsed_body,
                )
                await self.queue.put(page_entry)
                _logger.debug("Loaded page %s of department %s.", page_number, department.name)

            empty_page = syllabus_scanner_non_persistent_models.PageEntry(
                department=department,
                page_number=-1,
                body=None,
            )
            await self.queue.put(empty_page)

    async def _get_first_page(
            self,
            session: ClientSession,
            department: syllabus_scanner_non_persistent_models.Department,
    ) -> bytes:
        params = {
            "lstYear1": str(self._year),
            "lstDep1": department.value,
            "ckYom": ["1", "2", "3", "4", "5", "6"],
        }

        if self._language == syllabus_scanner_non_persistent_models.Language.english:
            params["taulang"] = "eng"

        async with session.post(
            url=syllabus_scanner_defines.URLS[self._language],
            data=params,
        ) as response:
            if response.status != 200:
                raise ValueError(F"Failed to fetch first syllabus page. status_code={response.status}")
            return await response.read()

    async def _get_next_page(self, session: ClientSession, body: Tag) -> typing.Optional[bytes]:
        if not body.find("input", attrs={"id": "next"}):
            return None

        form = body.find("form", attrs={"id": "frmgrid"})
        method = form.attrs["method"].upper()
        params = {
            "__VIEWSTATE": form.find("input", attrs={"id": "__VIEWSTATE"}).attrs["value"],
            "__EVENTVALIDATION": form.find("input", attrs={"id": "__EVENTVALIDATION"}).attrs["value"],
            "dir1": "1",
        }

        async with session.request(
            method=method,
            url=syllabus_scanner_defines.URLS[self._language],
            data=params,
        ) as response:
            if response.status != 200:
                raise ValueError(F"Failed to fetch next syllabus page. status_code={response.status}")
            return await response.read()

    def set_consumer(self, consumer: typing.Callable[[asyncio.Queue], typing.Coroutine]) -> None:
        loop = asyncio.get_event_loop()
        self.consumer = loop.create_task(consumer(self.queue))

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            asyncio.wait((
                self._run(),
            )),
        )

    async def _run(self):
        loop = asyncio.get_event_loop()
        producer_tasks = tuple(
            loop.create_task(self._load_syllabus_pages(department=department))
            for department in self.departments
        )
        await asyncio.wait(producer_tasks)
        await self.queue.join()
