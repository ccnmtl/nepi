from django.contrib.auth.models import User
from django.test import TestCase
from factories import SchoolGroupFactory
from nepi.main.models import AggregateQuizScore
from nepi.main.tests.factories import StudentProfileFactory, \
    TeacherProfileFactory, ICAPProfileFactory
from pagetree.models import Hierarchy, Section, UserPageVisit
from pagetree.tests.factories import HierarchyFactory, ModuleFactory


class TestGroup(TestCase):
    def test_unicode(self):
        grp = SchoolGroupFactory()
        self.assertEqual(str(grp), grp.name)


class TestUserProfile(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.teacher = TeacherProfileFactory().user
        self.icap = ICAPProfileFactory().user
        ModuleFactory("main", "/")
        self.hierarchy = Hierarchy.objects.get(name='main')

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), self.student.username)

    def test_percent_complete(self):
        self.assertEquals(self.student.profile.percent_complete(), 0)

        # visit section one & child one
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')
        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(self.student.profile.percent_complete(), 40)

    def test_percent_complete_module(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        pct = self.student.profile.percent_complete_module(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        pct = self.student.profile.percent_complete_module(section_one)
        self.assertEquals(pct, 0)

        UserPageVisit.objects.create(user=self.student, section=child_one)
        pct = self.student.profile.percent_complete_module(section_one)
        self.assertEquals(pct, 100)

    def test_sessions_completed(self):
        section_one = Section.objects.get(slug='one')
        child_one = Section.objects.get(slug='introduction')

        self.assertEquals(self.student.profile.sessions_completed(), 2)

        UserPageVisit.objects.create(user=self.student, section=section_one)
        UserPageVisit.objects.create(user=self.student, section=child_one)
        self.assertEquals(self.student.profile.sessions_completed(), 3)


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

    def test_quizzes(self):
        quizzes = AggregateQuizScore(quiz_class='foo').quizzes().order_by(
            'description')
        self.assertEquals(quizzes.count(), 2)

        self.assertEquals(quizzes[0].description, 'the first quiz')
        self.assertEquals(quizzes[1].description, 'the second quiz')
