from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase
from factories import SchoolGroupFactory
from nepi.main.models import AggregateQuizScore, PendingTeachers
from nepi.main.tests.factories import StudentProfileFactory, \
    TeacherProfileFactory, ICAPProfileFactory, \
    CountryAdministratorProfileFactory, \
    SchoolFactory, InstitutionAdminProfileFactory
from pagetree.models import Hierarchy, Section, UserPageVisit
from pagetree.tests.factories import HierarchyFactory, ModuleFactory
import datetime


class TestGroup(TestCase):
    def test_unicode(self):
        grp = SchoolGroupFactory()
        self.assertEqual(str(grp), grp.name)

    def test_format_time(self):
        start = date(2007, 1, 5)
        end = date(2007, 12, 25)
        grp = SchoolGroupFactory(start_date=start, end_date=end)

        self.assertEquals(grp.formatted_start_date(), "01/05/2007")
        self.assertEquals(grp.formatted_end_date(), "12/25/2007")

    def test_is_active(self):
        start = date(2007, 1, 5)
        end = date(2007, 12, 25)
        grp = SchoolGroupFactory(start_date=start, end_date=end)

        self.assertFalse(grp.is_active())

        delta = datetime.timedelta(days=-90)
        grp.end_date = datetime.date.today() + delta
        self.assertTrue(grp.is_active())

        delta = datetime.timedelta(days=90)
        grp.end_date = datetime.date.today() + delta
        self.assertTrue(grp.is_active())


class TestUserProfile(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.teacher = TeacherProfileFactory().user
        self.school_admin = InstitutionAdminProfileFactory().user
        self.icap = ICAPProfileFactory().user
        self.country_admin = CountryAdministratorProfileFactory().user
        ModuleFactory("main", "/")
        self.hierarchy = Hierarchy.objects.get(name='main')

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), self.student.username)

    def test_display_name(self):
        self.assertEquals(self.student.profile.display_name(),
                          self.student.username)

    def test_user_profile_roles(self):
        self.assertTrue(self.student.profile.is_student())
        self.assertFalse(self.teacher.profile.is_student())
        self.assertFalse(self.school_admin.profile.is_student())
        self.assertFalse(self.country_admin.profile.is_student())
        self.assertFalse(self.icap.profile.is_student())

        self.assertFalse(self.student.profile.is_teacher())
        self.assertTrue(self.teacher.profile.is_teacher())
        self.assertFalse(self.school_admin.profile.is_teacher())
        self.assertFalse(self.country_admin.profile.is_teacher())
        self.assertFalse(self.icap.profile.is_teacher())

        self.assertFalse(self.student.profile.is_institution_administrator())
        self.assertFalse(self.teacher.profile.is_institution_administrator())
        self.assertTrue(
            self.school_admin.profile.is_institution_administrator())
        self.assertFalse(
            self.country_admin.profile.is_institution_administrator())
        self.assertFalse(self.icap.profile.is_institution_administrator())

        self.assertFalse(self.student.profile.is_country_administrator())
        self.assertFalse(self.teacher.profile.is_country_administrator())
        self.assertFalse(self.school_admin.profile.is_country_administrator())
        self.assertTrue(self.country_admin.profile.is_country_administrator())
        self.assertFalse(self.icap.profile.is_country_administrator())

        self.assertFalse(self.student.profile.is_icap())
        self.assertFalse(self.teacher.profile.is_icap())
        self.assertFalse(self.school_admin.profile.is_icap())
        self.assertFalse(self.country_admin.profile.is_icap())
        self.assertTrue(self.icap.profile.is_icap())

        self.assertEquals(self.student.profile.role(), 'student')
        self.assertEquals(self.teacher.profile.role(), 'faculty')
        self.assertEquals(self.country_admin.profile.role(), 'country')
        self.assertEquals(self.icap.profile.role(), 'icap')

    def test_last_location(self):
        self.assertEquals(self.student.profile.last_location(self.hierarchy),
                          self.hierarchy.get_root())

        section = Section.objects.get(slug='two')
        UserPageVisit.objects.create(user=self.student, section=section)
        self.assertEquals(self.student.profile.last_location(self.hierarchy),
                          section)

    def test_percent_complete(self):
        root = self.hierarchy.get_root()
        self.assertEquals(self.student.profile.percent_complete(root), 0)

        # visit section one & child one
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')
        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(self.student.profile.percent_complete(root), 50)

    def test_percent_complete_session(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=child_one)
        pct = self.student.profile.percent_complete(section_one)
        self.assertEquals(pct, 100)

    def test_sessions_completed(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        self.assertEquals(self.student.profile.sessions_completed(
            self.hierarchy), 2)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(
            self.student.profile.sessions_completed(self.hierarchy), 3)

    def test_joined_groups(self):
        group = SchoolGroupFactory()

        self.assertEquals(self.student.profile.joined_groups().count(), 0)

        self.student.profile.group.add(group)
        self.assertEquals(self.student.profile.joined_groups().count(), 1)

        group.archived = True
        group.save()
        self.assertEquals(self.student.profile.joined_groups().count(), 0)


class TestPendingTeachers(TestCase):
    def test_unicode(self):
        school = SchoolFactory()
        student = StudentProfileFactory()
        teacher = PendingTeachers.objects.create(user_profile=student,
                                                 school=school)

        label = "%s - %s" % (student, school)
        self.assertEquals(label, teacher.__unicode__())


class TestAggregateQuizScore(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

        hierarchy = HierarchyFactory()

        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page One',
            'slug': 'page-one',
            'pageblocks': [{
                'label': 'pretest page one',
                'css_extra': 'foo',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the first quiz',
                'questions': []},
            ],
            'children': [],
        })
        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page Two',
            'slug': 'page-two',
            'pageblocks': [{
                'label': 'pretest page two',
                'css_extra': 'foo',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the second quiz',
                'questions': []},
            ],
            'children': [],
        })
        hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page Three',
            'slug': 'page-three',
            'pageblocks': [{
                'label': 'pretest page three',
                'css_extra': 'bar',
                'block_type': 'Quiz',
                'rhetorical': False,
                'description': 'the third quiz',
                'questions': []},
            ],
            'children': [],
        })

    def test_basics(self):
        aqs = AggregateQuizScore(quiz_class='foo')
        self.assertFalse(aqs.needs_submit())
        self.assertTrue(aqs.unlocked(self.user))

    def test_quizzes(self):
        quizzes = AggregateQuizScore(quiz_class='foo').quizzes().order_by(
            'description')
        self.assertEquals(quizzes.count(), 2)

        self.assertEquals(quizzes[0].description, 'the first quiz')
        self.assertEquals(quizzes[1].description, 'the second quiz')
