from homeschool.courses.tests.factories import CourseFactory, CourseTaskFactory
from homeschool.test import TestCase


class TestCourseDetailView(TestCase):
    def test_unauthenticated_access(self):
        course = CourseFactory()
        self.assertLoginRequired("courses:detail", uuid=course.uuid)

    def test_get(self):
        user = self.make_user()
        course = CourseFactory(grade_level__school_year__school__admin=user)

        with self.login(user):
            self.get_check_200("courses:detail", uuid=course.uuid)


class TestCourseTaskUpdateView(TestCase):
    def test_unauthenticated_access(self):
        task = CourseTaskFactory()
        self.assertLoginRequired("courses:task_edit", uuid=task.uuid)

    def test_get(self):
        user = self.make_user()
        task = CourseTaskFactory(course__grade_level__school_year__school__admin=user)

        with self.login(user):
            self.get_check_200("courses:task_edit", uuid=task.uuid)

    def test_get_other_user(self):
        user = self.make_user()
        task = CourseTaskFactory()

        with self.login(user):
            response = self.get("courses:task_edit", uuid=task.uuid)

        self.response_404(response)

    def test_post(self):
        user = self.make_user()
        task = CourseTaskFactory(
            description="some description",
            duration=30,
            course__grade_level__school_year__school__admin=user,
        )
        data = {"description": "new description", "duration": 15}

        with self.login(user):
            response = self.post("courses:task_edit", uuid=task.uuid, data=data)

        task.refresh_from_db()
        self.assertEqual(task.description, data["description"])
        self.assertEqual(task.duration, data["duration"])
        self.response_302(response)

    def test_redirect_next(self):
        next_url = "/another/location/"
        user = self.make_user()
        task = CourseTaskFactory(course__grade_level__school_year__school__admin=user)
        data = {"description": "new description", "duration": 15}
        url = self.reverse("courses:task_edit", uuid=task.uuid)
        url += f"?next={next_url}"

        with self.login(user):
            response = self.post(url, data=data)

        self.response_302(response)
        self.assertIn(next_url, response.get("Location"))