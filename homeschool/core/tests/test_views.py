import datetime
from unittest import mock

import pytz
from dateutil.relativedelta import MO, SU, relativedelta
from django.utils import timezone

from homeschool.courses.models import Course
from homeschool.courses.tests.factories import CourseFactory, CourseTaskFactory
from homeschool.schools.models import SchoolYear
from homeschool.schools.tests.factories import GradeLevelFactory, SchoolYearFactory
from homeschool.students.models import Coursework
from homeschool.students.tests.factories import (
    CourseworkFactory,
    EnrollmentFactory,
    StudentFactory,
)
from homeschool.test import TestCase


class TestIndex(TestCase):
    def test_ok(self):
        self.get_check_200("core:index")


class TestApp(TestCase):
    def test_ok(self):
        user = self.make_user()

        with self.login(user):
            self.get_check_200("core:app")

    def test_unauthenticated_access(self):
        self.assertLoginRequired("core:app")

    @mock.patch("homeschool.core.views.timezone")
    def test_has_monday(self, timezone):
        user = self.make_user()
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        monday = now.date() + relativedelta(weekday=MO(-1))
        timezone.now.return_value = now

        with self.login(user):
            self.get("core:app")

        self.assertContext("monday", monday)

    @mock.patch("homeschool.core.views.timezone")
    def test_has_sunday(self, timezone):
        user = self.make_user()
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        sunday = now.date() + relativedelta(weekday=SU(+1))
        timezone.now.return_value = now

        with self.login(user):
            self.get("core:app")

        self.assertContext("sunday", sunday)

    @mock.patch("homeschool.core.views.timezone")
    def test_has_today(self, timezone):
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        timezone.now.return_value = now
        today = now.date()
        user = self.make_user()
        SchoolYearFactory(
            school=user.school,
            start_date=today - datetime.timedelta(days=90),
            end_date=today + datetime.timedelta(days=90),
        )

        with self.login(user):
            self.get("core:app")

        self.assertContext("today", today)

    @mock.patch("homeschool.core.views.timezone")
    def test_has_schedules(self, timezone):
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        sunday = now.date()
        monday = sunday - datetime.timedelta(days=6)
        timezone.now.return_value = now
        user = self.make_user()
        student = StudentFactory(school=user.school)
        school_year = SchoolYearFactory(
            school=user.school,
            start_date=sunday - datetime.timedelta(days=90),
            end_date=sunday + datetime.timedelta(days=90),
            days_of_week=SchoolYear.MONDAY
            + SchoolYear.TUESDAY
            + SchoolYear.WEDNESDAY
            + SchoolYear.THURSDAY
            + SchoolYear.FRIDAY,
        )
        grade_level = GradeLevelFactory(school_year=school_year)
        course = CourseFactory(
            grade_level=grade_level,
            days_of_week=Course.MONDAY
            + Course.WEDNESDAY
            + Course.THURSDAY
            + Course.FRIDAY,
        )
        task_1 = CourseTaskFactory(course=course)
        task_2 = CourseTaskFactory(course=course)
        task_3 = CourseTaskFactory(course=course)
        coursework = CourseworkFactory(
            student=student, course_task=task_1, completed_date=monday
        )
        EnrollmentFactory(student=student, grade_level=grade_level)

        with self.login(user), self.assertNumQueries(11):
            self.get("core:app")

        expected_schedule = {
            "student": student,
            "courses": [
                {
                    "course": course,
                    "days": [
                        {"week_date": monday, "coursework": [coursework]},
                        {"week_date": monday + datetime.timedelta(days=1)},
                        {
                            "week_date": monday + datetime.timedelta(days=2),
                            "task": task_2,
                        },
                        {
                            "week_date": monday + datetime.timedelta(days=3),
                            "task": task_3,
                        },
                        {"week_date": monday + datetime.timedelta(days=4)},
                    ],
                }
            ],
        }
        self.assertContext("schedules", [expected_schedule])

    @mock.patch("homeschool.core.views.timezone")
    def test_has_week_dates(self, timezone):
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        sunday = now.date()
        monday = sunday - datetime.timedelta(days=6)
        timezone.now.return_value = now
        user = self.make_user()
        SchoolYearFactory(
            school=user.school,
            start_date=sunday - datetime.timedelta(days=90),
            end_date=sunday + datetime.timedelta(days=90),
            days_of_week=SchoolYear.MONDAY
            + SchoolYear.TUESDAY
            + SchoolYear.WEDNESDAY
            + SchoolYear.THURSDAY
            + SchoolYear.FRIDAY,
        )

        with self.login(user):
            self.get("core:app")

        expected_week_dates = [
            monday,
            monday + datetime.timedelta(days=1),
            monday + datetime.timedelta(days=2),
            monday + datetime.timedelta(days=3),
            monday + datetime.timedelta(days=4),
        ]
        self.assertContext("week_dates", expected_week_dates)

    def test_no_school_year(self):
        user = self.make_user()
        StudentFactory(school=user.school)

        with self.login(user):
            self.get("core:app")

        self.assertContext("schedules", [])


class TestDaily(TestCase):
    def test_ok(self):
        user = self.make_user()

        with self.login(user):
            self.get_check_200("core:daily")

    def test_unauthenticated_access(self):
        self.assertLoginRequired("core:daily")

    def test_has_day(self):
        user = self.make_user()
        today = timezone.now().date()

        with self.login(user):
            self.get("core:daily")

        self.assertContext("day", today)

    def test_no_school_year(self):
        user = self.make_user()
        StudentFactory(school=user.school)

        with self.login(user):
            self.get("core:daily")

        self.assertContext("schedules", [])

    @mock.patch("homeschool.core.views.timezone")
    def test_school_not_run_on_day(self, timezone):
        now = datetime.datetime(2020, 1, 26, tzinfo=pytz.utc)
        sunday = now.date()
        timezone.now.return_value = now
        user = self.make_user()
        SchoolYearFactory(
            school=user.school,
            start_date=sunday - datetime.timedelta(days=90),
            end_date=sunday + datetime.timedelta(days=90),
            days_of_week=SchoolYear.MONDAY,
        )

        with self.login(user):
            self.get("core:daily")

        self.assertContext("schedules", [])

    @mock.patch("homeschool.core.views.timezone")
    def test_has_schedules(self, timezone):
        now = datetime.datetime(2020, 1, 24, tzinfo=pytz.utc)
        friday = now.date()
        timezone.now.return_value = now
        user = self.make_user()
        student = StudentFactory(school=user.school)
        school_year = SchoolYearFactory(
            school=user.school,
            start_date=friday - datetime.timedelta(days=90),
            end_date=friday + datetime.timedelta(days=90),
            days_of_week=SchoolYear.FRIDAY,
        )
        grade_level = GradeLevelFactory(school_year=school_year)
        course = CourseFactory(grade_level=grade_level, days_of_week=Course.FRIDAY)
        task_1 = CourseTaskFactory(course=course)
        coursework = CourseworkFactory(
            student=student, course_task=task_1, completed_date=friday
        )
        course_2 = CourseFactory(grade_level=grade_level, days_of_week=Course.FRIDAY)
        task_2 = CourseTaskFactory(course=course_2)
        course_3 = CourseFactory(grade_level=grade_level, days_of_week=Course.THURSDAY)
        CourseTaskFactory(course=course_3)
        course_4 = CourseFactory(grade_level=grade_level, days_of_week=Course.FRIDAY)
        EnrollmentFactory(student=student, grade_level=grade_level)

        with self.login(user):
            self.get("core:daily")

        expected_schedule = {
            "student": student,
            "courses": [
                {"course": course, "coursework": [coursework]},
                {"course": course_2, "task": task_2},
                {"course": course_3},
                {"course": course_4, "task": None},
            ],
        }
        self.assertContext("schedules", [expected_schedule])

    def test_specific_day(self):
        user = self.make_user()
        day = datetime.date(2020, 1, 20)

        with self.login(user):
            self.get("core:daily_for_date", year=day.year, month=day.month, day=day.day)

        self.assertContext("day", day)

    def test_surrounding_dates_no_school_year(self):
        user = self.make_user()
        today = timezone.now().date()

        with self.login(user):
            self.get("core:daily")

        self.assertContext("ereyesterday", today - datetime.timedelta(days=2))
        self.assertContext("yesterday", today - datetime.timedelta(days=1))
        self.assertContext("tomorrow", today + datetime.timedelta(days=1))
        self.assertContext("overmorrow", today + datetime.timedelta(days=2))

    @mock.patch("homeschool.core.views.timezone")
    def test_surrounding_dates(self, timezone):
        now = datetime.datetime(2020, 1, 22, tzinfo=pytz.utc)
        wednesday = now.date()
        timezone.now.return_value = now
        user = self.make_user()
        SchoolYearFactory(
            school=user.school,
            start_date=wednesday - datetime.timedelta(days=90),
            end_date=wednesday + datetime.timedelta(days=90),
            days_of_week=SchoolYear.TUESDAY
            + SchoolYear.WEDNESDAY
            + SchoolYear.THURSDAY,
        )

        with self.login(user):
            self.get("core:daily")

        previous_thursday = wednesday - datetime.timedelta(days=6)
        self.assertContext("ereyesterday", previous_thursday)
        self.assertContext("yesterday", wednesday - datetime.timedelta(days=1))
        self.assertContext("tomorrow", wednesday + datetime.timedelta(days=1))
        next_tuesday = wednesday + datetime.timedelta(days=6)
        self.assertContext("overmorrow", next_tuesday)

    def test_complete_daily(self):
        today = timezone.now().date()
        user = self.make_user()
        student = StudentFactory(school=user.school)
        school_year = SchoolYearFactory(school=user.school)
        grade_level = GradeLevelFactory(school_year=school_year)
        course = CourseFactory(grade_level=grade_level)
        task = CourseTaskFactory(course=course)
        data = {
            "completed_date": "{:%Y-%m-%d}".format(today),
            f"task-{student.id}-{task.id}": "on",
        }

        with self.login(user):
            self.post("core:daily", data=data)

        self.assertTrue(
            Coursework.objects.filter(
                student=student, course_task=task, completed_date=today
            ).exists()
        )

    def test_incomplete_daily(self):
        today = timezone.now().date()
        user = self.make_user()
        student = StudentFactory(school=user.school)
        school_year = SchoolYearFactory(school=user.school)
        grade_level = GradeLevelFactory(school_year=school_year)
        course = CourseFactory(grade_level=grade_level)
        task = CourseTaskFactory(course=course)
        CourseworkFactory(student=student, course_task=task)
        data = {
            "completed_date": "{:%Y-%m-%d}".format(today),
            f"task-{student.id}-{task.id}": "off",
        }

        with self.login(user):
            self.post("core:daily", data=data)

        self.assertFalse(
            Coursework.objects.filter(student=student, course_task=task).exists()
        )