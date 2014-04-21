from datetime import datetime
from django.contrib.auth.models import User
#from activities.models import NurseConversation
#from activities.models import PatientConversation
#from activities.models import ConversationDialog
from pagetree.models import Hierarchy
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)

class NurseConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = NurseConversation
    starting = "Asking patient appropriate question part one"
    response_one = ""
    response_two = ""

class PatientConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PatientConversation
    starting = ""
    response_one = "Patient thought can go here"
    response_two = "Patient response can go here"

class ConversationDialogFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationDialog
    order = 1
    content = "This is the nurse's first line"

from django.test import TestCase
from django.contrib.auth.models import User
from nepi.main.models import UserProfile, Country, School
from nepi.main.models import Course
from datetime import datetime
from factories import CountryFactory, SchoolFactory, CourseFactory
from factories import UserProfileFactory, TeacherProfileFactory
from factories import ICAPProfileFactory, HierarchyFactory


class TestCountry(TestCase):
    def test_unicode(self):
        c = CountryFactory()
        self.assertEqual(str(c), "LS")


class TestSchool(TestCase):
    def test_unicode(self):
        s = SchoolFactory()
        self.assertEqual(str(s), "Test School")


class TestCourse(TestCase):
    def test_unicode(self):
        c = CourseFactory()
        self.assertEqual(str(c), "A Course")


class TestUserProfile(TestCase):
    def setUp(self):
        self.student = User(first_name="student", last_name="student",
                            username="student", email="student@email.com",
                            password="student")
        self.student.save()
        self.teacher = User(first_name="teacher", last_name="teacher",
                            username="teacher", email="teacher@email.com",
                            password="teacher")
        self.teacher.save()
        self.icap = User(first_name="icapp", last_name="icapp",
                         username="icapp", email="icapp@email.com",
                         password="icapp")
        self.icap.save()
        self.country1 = Country(name='LS', region='Region 1')
        self.country1.save()
        self.country2 = Country(name='GM', region='Region 1')
        self.country1.save()
        self.country3 = Country(name='TG', region='Region 1')
        self.country1.save()
        self.school = School(country=self.country1, name='School 1')
        self.school.save()
        self.course = Course(school=self.school,
                             semester="Fall 2018", name="Course",
                             start_date=datetime.now(),
                             end_date=datetime.now())
        self.course.save()
        self.student_profile = UserProfile(
            user=self.student, profile_type='ST', country=self.country1,
            school=self.school)

        self.student_profile.save()
        self.teacher_profile = UserProfile(
            user=self.teacher, profile_type='TE', country=self.country1,
            school=self.school)
        self.teacher_profile.save()
        self.icap_profile = UserProfile(
            user=self.icap, profile_type='IC',
            country=self.country1, school=self.school)
        self.icap_profile.save()

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), "student")
        self.assertEquals(unicode(self.teacher), "teacher")
        self.assertEquals(unicode(self.icap), "icapp")
