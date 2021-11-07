import os
import re

from syllabus_scanner import non_persistent_models as syllabus_scanner_non_persistent_models

URLS = {
    syllabus_scanner_non_persistent_models.Language.hebrew:
        os.getenv("SYLLABUS_URL", "https://www.ims.tau.ac.il/tal/kr/Search_L.aspx"),
    syllabus_scanner_non_persistent_models.Language.english:
        os.getenv("SYLLABUS_URL", "https://www.ims.tau.ac.il/tal/kr/Search_L.aspx?lang=EN")
}
USER_AGENT = os.getenv(
    "SYLLABUS_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
)
HEADERS = {"User-Agent": USER_AGENT}

PAGE_QUEUE_SIZE_MULTIPLIER = 2

YEAR_PATTERN = re.compile(r"^.*(\d{4})/\d{4}.*$")
COURSE_AND_GROUP_PATTERN = re.compile(r"^(\d{4}-\d{4})\s+(קב'|Gr):\s(\d{2})$")
FACULTY_AND_SCHOOL_PATTERN = re.compile(r"^(.*)/(.*)$")
