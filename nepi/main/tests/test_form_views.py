'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from nepi.main.models import Country, School
from nepi.main.models import Course
from nepi.main.views import CreateSchoolView
from nepi.main.views import CreateCourseView
from datetime import datetime
from factories import UserFactory, CourseFactory


class TestFormViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.country = Country(name='LS')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.course = Course(school=self.school,
                             name="Course",
                             start_date=datetime.now(),
                             end_date=datetime.now())
        self.student = User(first_name="student", last_name="student",
                            username="student", email="student@email.com",
                            password="student")
        self.student.save()
        self.teacher = User(first_name="teacher", last_name="teacher",
                            username="teacher", email="teacher@email.com",
                            password="teacher")
        self.teacher.save()

    def test_create_school(self):
        '''CreateSchoolView'''
        u = UserFactory()
        request = self.factory.post(
            '/add_school/',
            {"name": "School Needs Name",
             "creator" : u,
             "country": self.country})
        CreateSchoolView.as_view()(request)

    def test_create_course(self):
        '''CreateSchoolView'''
        u = UserFactory()
        request = self.factory.post(
            '/add_course/',
            {"name": "Course Needs Name",
             "creator" : u,
             "country": self.country,
             "school": self.school})
        CreateCourseView.as_view()(request)
