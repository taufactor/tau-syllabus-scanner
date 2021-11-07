import enum
import functools
import logging
import typing

from bs4.element import Tag

_logger = logging.getLogger(__name__)


class Language(enum.Enum):
    hebrew = "Hebrew"
    english = "English"

    @classmethod
    def all(cls) -> typing.Tuple["Language", ...]:
        return tuple(language for language in cls)

    def serialize(self) -> str:
        return self.name

    def serialize_text(self) -> str:
        return self.value

    def __srt__(self) -> str:
        return self.serialize_text()


class Department(enum.Enum):
    arts = "08"
    engineering = "05"
    social_sciences = "10-11"
    life_sciences = "04"
    humanities = "06-16-07"
    exact_sciences = "03-09"
    law = "14"
    management = "12"
    medicine = "01"
    neuroscience = "15"
    special_units = "2171-2172"  # שפות זרות
    special_study_programs = "1880-1882-1883"  # כלים שלובים ומתחברים פלוס
    cyber = "1843"
    abroad_students = "2120"

    @classmethod
    def all(cls) -> typing.Sequence["Department"]:
        return tuple(department for department in cls)

    def serialize(self) -> str:
        return self.name

    def serialize_text(self) -> str:
        return self.name

    def __str__(self):
        return self.serialize_text()


@functools.total_ordering
class PageEntry(typing.NamedTuple):
    department: Department
    page_number: int
    body: typing.Optional[Tag]

    @property
    def is_valid(self) -> bool:
        return self.body is not None

    def __lt__(self, other: "PageEntry") -> bool:
        return (self.department.name, self.page_number) < (other.department.name, other.page_number)

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, PageEntry):
            return False
        return self.department == other.department and self.page_number == other.page_number

    def __hash__(self) -> int:
        return hash((self.department, self.page_number))


class Semester(enum.Enum):
    a = "A"
    b = "B"
    all_year = "All Year"  # Deduced
    summer = "Summer"

    @staticmethod
    def from_text(text: str) -> "Semester":
        text_to_semester_mapping = {
            "א'": Semester.a,
            "ב'": Semester.b,
            "קיץ": Semester.summer,
            "First": Semester.a,
            "Second": Semester.b,
            "Summer": Semester.summer,
        }
        semester = text_to_semester_mapping.get(text)
        if semester is None:
            _logger.error("Got a Unexpected semester %s.", text)
            raise ValueError(F"Got a Unexpected semester {text}.")
        return semester

    def serialize(self) -> str:
        return self.name

    def serialize_text(self) -> str:
        return self.value

    def __str__(self):
        return self.serialize_text()


class MeetingType(enum.Enum):
    lecture = "Lecture"
    exercise = "Exercise"
    lecture_and_exercise = "Lecture and Exercise"
    lecture_and_laboratory = "Lecture and Laboratory"
    project = "Project"
    workshop = "Workshop"
    seminar = "Seminar"
    seminar_paper = "Seminar Paper"
    proseminar = "Proseminar"
    practicum = "Practicum"
    colloqium = "Colloqium"
    laboratory = "Laboratory"
    field_trip = "Field Trip"
    personal_training = "Personal Training"
    bibliography_tutorial = "Bibliography Tutorial"
    guided_readings = "Guided Readings"

    @classmethod
    def all(cls) -> typing.Tuple["MeetingType", ...]:
        return tuple(meeting_type for meeting_type in cls)

    @staticmethod
    def from_text(text: str) -> "MeetingType":
        hebrew_mapping = {
            "שיעור": MeetingType.lecture,
            "תרגיל": MeetingType.exercise,
            "שיעור ותרגיל": MeetingType.lecture_and_exercise,
            "שיעור ומעבדה": MeetingType.lecture_and_laboratory,
            "פרוייקט": MeetingType.project,
            "סדנה": MeetingType.workshop,
            "סמינר": MeetingType.seminar,
            "פרוסמינר": MeetingType.proseminar,
            "עבודה סמינריונית": MeetingType.seminar_paper,
            "עבודה מעשית": MeetingType.practicum,
            "קולוקויום": MeetingType.colloqium,
            "מעבדה": MeetingType.laboratory,
            "סיור": MeetingType.field_trip,
            "הדרכה אישית": MeetingType.personal_training,
            "הדרכה ביבליוגרפית": MeetingType.bibliography_tutorial,
            "קריאה מודרכת": MeetingType.guided_readings,
            "Tutorial": MeetingType.personal_training,
        }
        english_mapping = {meeting_type.value: meeting_type for meeting_type in MeetingType.all()}
        text_to_meeting_type_mapping = {**hebrew_mapping, **english_mapping}

        meeting_type = text_to_meeting_type_mapping.get(text)
        if meeting_type is None:
            _logger.error("Got a Unexpected meeting type %s.", text)
            raise ValueError(F"Got a Unexpected meeting type {text}.")
        return meeting_type

    def serialize(self) -> str:
        return self.name

    def serialize_text(self) -> str:
        return self.value

    def __str__(self):
        return self.serialize_text()


class Day(enum.Enum):
    sunday = "Sunday"
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"

    @staticmethod
    def from_text(text: str) -> "Day":
        text_to_day_mapping = {
            "א": Day.sunday,
            "ב": Day.monday,
            "ג": Day.tuesday,
            "ד": Day.wednesday,
            "ה": Day.thursday,
            "ו": Day.friday,
            "Sun": Day.sunday,
            "Mon": Day.monday,
            "Tue": Day.tuesday,
            "Wed": Day.wednesday,
            "Thu": Day.thursday,
            "Fri": Day.friday,
        }
        day = text_to_day_mapping.get(text)
        if day is None:
            _logger.error("Got a Unexpected day %s.", text)
            raise ValueError(F"Got a Unexpected day {text}.")
        return day

    def serialize(self) -> str:
        return self.name

    def serialize_text(self) -> str:
        return self.value

    def __str__(self):
        return self.serialize_text()


class Teacher(typing.NamedTuple):
    honorific: str
    full_name: str

    @classmethod
    def from_text(cls, teacher_name_text: str) -> "Teacher":
        teacher_split = teacher_name_text.split(" ", 1)
        if len(teacher_split) != 2:
            _logger.error("Invalid teacher name %s.", teacher_name_text)
            raise ValueError(F"Invalid teacher name {teacher_name_text}.")
        return Teacher(
            honorific=teacher_split[0],
            full_name=teacher_split[1],
        )

    def serialize(self) -> dict:
        return {
            "honorific": self.honorific,
            "full_name": self.full_name,
        }

    def serialize_text(self) -> str:
        return F"{self.honorific} {self.full_name}"

    def __str__(self):
        return self.serialize_text()


class CourseGroupMeetingInfo(typing.NamedTuple):
    meeting_type: MeetingType
    teachers: typing.Set[Teacher]
    # Location
    building: typing.Optional[str]
    room: typing.Optional[str]
    # Time
    semester: Semester
    day: typing.Optional[Day]
    starting_time: typing.Optional[str]
    ending_time: typing.Optional[str]

    def serialize(self) -> dict:
        response = {
            "meeting_type": self.meeting_type.serialize(),
            "teachers": tuple(teacher.serialize() for teacher in sorted(self.teachers)),
            "semester": self.semester.serialize(),
        }
        if self.building is not None:
            response["building"] = self.building
        if self.room is not None:
            response["room"] = self.room
        if self.day is not None:
            response["day"] = self.day.serialize()
        if self.starting_time is not None:
            response["starting_time"] = self.starting_time
        if self.ending_time is not None:
            response["ending_time"] = self.ending_time
        return response

    def serialize_text(self, indent: int = 0) -> str:
        response = ""
        response += "\t" * indent + F"Meeting type: {self.meeting_type.serialize_text()}\n"
        response += "\t" * indent + F"Semester: {self.semester.serialize_text()}\n"
        if self.building:
            response += "\t" * indent + F"Building: {self.building}\n"
        if self.room:
            response += "\t" * indent + F"Room: {self.room}\n"
        if self.day:
            response += "\t" * indent + F"Day: {self.day}\n"
        if self.starting_time:
            response += "\t" * indent + F"Starting time: {self.starting_time}\n"
        if self.ending_time:
            response += "\t" * indent + F"Ending time: {self.ending_time}\n"
        if self.teachers:
            response += "\t" * indent + F"Teachers:\n"
            for teacher in sorted(self.teachers):
                response += "\t" * (indent+1) + F"{teacher.serialize_text()}\n"
        return response

    def __str__(self):
        return self.serialize_text()


class CourseGroupInfo(typing.NamedTuple):
    course_code: str
    course_name: str
    course_group_name: str
    faculty: str
    school: str
    meetings: typing.Tuple[CourseGroupMeetingInfo, ...]

    @property
    def semester(self) -> Semester:
        semesters: typing.Set[Semester] = {meeting.semester for meeting in self.meetings}
        if len(semesters) == 1:
            return tuple(semesters)[0]
        if Semester.summer in semesters:
            _logger.error(
                "Did not expect %s-%s to have %s meetings when there are other semesters in the group as well.",
                self.course_code,
                self.course_group_name,
                Semester.summer.name,
            )
            raise ValueError(
                F"Did not expect {self.course_code}-{self.course_group_name} to have {Semester.summer.name} meetings "
                "when there are other semesters in the group as well.",
            )
        if Semester.all_year in semesters:
            _logger.error(
                "Found semester type %s in %s-%s meetings, which should only be deduced on the entire group.",
                Semester.all_year.name,
                self.course_code,
                self.course_group_name,
            )
            raise ValueError(
                F"Found semester type {Semester.all_year.name} in {self.course_code}-{self.course_group_name} "
                "meetings, which should only be deduced on the entire group.",
            )
        return Semester.all_year

    @property
    def teachers(self) -> typing.Iterable[Teacher]:
        teachers: typing.Set[Teacher] = set()
        for meeting in self.meetings:
            teachers = teachers.union(meeting.teachers)
        return teachers

    def serialize(self) -> dict:
        return {
            "course_code": self.course_code,
            "course_name": self.course_name,
            "course_group_name": self.course_group_name,
            "semester": self.semester.serialize(),
            "faculty": self.faculty,
            "school": self.school,
            "meetings": tuple(course_group_meeting.serialize() for course_group_meeting in self.meetings)
        }

    def serialize_text(self, indent: int = 0) -> str:
        response = ""
        response += "\t" * indent + F"Course code: {self.course_code}\n"
        response += "\t" * indent + F"Course name: {self.course_name}\n"
        response += "\t" * indent + F"Course group name: {self.course_group_name}\n"
        response += "\t" * indent + F"Semester: {self.semester.serialize_text()}\n"
        response += "\t" * indent + F"Faculty: {self.faculty}\n"
        response += "\t" * indent + F"School: {self.school}\n"
        if self.meetings:
            response += "\t" * indent + "Meetings:\n"
            for course_group_meeting in self.meetings:
                response += F"{course_group_meeting.serialize_text(indent=indent+1)}"
        return response

    def __str__(self):
        return self.serialize_text()


class CourseInfo(typing.NamedTuple):
    course_code: str
    year: int
    course_groups: typing.List[CourseGroupInfo]

    def serialize(self) -> dict:
        return {
            "course_code": self.course_code,
            "year": self.year,
            "course_groups": tuple(course_group.serialize() for course_group in self.course_groups),
        }

    def serialize_text(self, indent: int = 0) -> str:
        response = ""
        response += "\t" * indent + F"Course code: {self.course_code}\n"
        response += "\t" * indent + F"Year: {self.year}\n"
        if self.course_groups:
            response += "\t" * indent + "Groups:\n"
            for course_group in self.course_groups:
                response += F"{course_group.serialize_text(indent=indent+1)}"
        return response

    def __str__(self):
        return self.serialize_text()


class CourseGroupParsingFailure(typing.NamedTuple):
    department: Department
    page_number: int
    index_in_page: int
    exception_message: str

    def serialize(self) -> dict:
        return {
            "department": self.department.serialize(),
            "page_number": self.page_number,
            "index_in_page": self.index_in_page,
            "exception_message": self.exception_message,
        }

    def serialize_text(self, indent: int = 0) -> str:
        response = ""
        response += "\t" * indent + F"Department: {self.department.serialize_text()}\n"
        response += "\t" * indent + F"Page number: {self.page_number}\n"
        response += "\t" * indent + F"Index in page: {self.index_in_page}\n"
        response += "\t" * indent + F"Exception message: {self.exception_message}\n"
        return response


class ScanResults(typing.NamedTuple):
    courses: typing.Tuple[CourseInfo, ...]
    failures: typing.Tuple[CourseGroupParsingFailure, ...]

    def serialize(self) -> dict:
        return {
            "courses": tuple(course.serialize() for course in self.courses),
            "failures": tuple(failure.serialize() for failure in self.failures),
        }

    def serialize_text(self, indent: int = 0) -> str:
        if not self.courses:
            return "No courses!"
        response = ""
        if self.courses:
            response += "\t" * indent + "Courses:\n"
            for course in self.courses:
                response += F"{course.serialize_text(indent=indent+1)}"
        if self.failures:
            response += "\t" * indent + "Failures:\n"
            for failure in self.failures:
                response += F"{failure.serialize_text(indent=indent+1)}"
        return response

    def __str__(self):
        return self.serialize_text()
