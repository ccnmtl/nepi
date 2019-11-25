from __future__ import unicode_literals

from datetime import date
import datetime

from django.core.cache import cache
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from pagetree.models import Hierarchy, UserPageVisit, Section
from pagetree.tests.factories import ModuleFactory
from quizblock.models import Quiz, Question, Answer, Submission, Response

from nepi.main.tests.factories import SchoolGroupFactory, \
    StudentProfileFactory, ICAPProfileFactory, TeacherProfileFactory, \
    InstitutionAdminProfileFactory, CountryAdministratorProfileFactory
from nepi.main.views import BaseReportMixin, DownloadableReportView


class TestReportBase(TestCase):

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()
        self.report_view_url = reverse('report-view')
        self.report_download_url = reverse('report-download')

        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchies = Hierarchy.objects.filter(name='optionb-en')
        self.hierarchy = self.hierarchies[0]
        root = self.hierarchy.get_root()
        descendants = root.get_descendants()

        self.old_group = SchoolGroupFactory(end_date=date(2007, 12, 25),
                                            module=self.hierarchy)
        incomplete_user = \
            StudentProfileFactory(school=self.old_group.school).user
        UserPageVisit.objects.create(user=incomplete_user,
                                     section=descendants[0])
        self.old_group.userprofile_set.add(incomplete_user.profile)

        self.new_group = SchoolGroupFactory(end_date=datetime.date.today(),
                                            module=self.hierarchy)

        complete_user = \
            StudentProfileFactory(school=self.new_group.school).user
        self.new_group.userprofile_set.add(complete_user.profile)
        for section in descendants:
            UserPageVisit.objects.create(user=complete_user, section=section,
                                         status='complete')

        inprogress_user = \
            StudentProfileFactory(school=self.new_group.school).user
        self.new_group.userprofile_set.add(inprogress_user.profile)
        UserPageVisit.objects.create(user=inprogress_user,
                                     section=descendants[0])

        # unaffiliated
        self.icap = ICAPProfileFactory(
            country=self.new_group.school.country).user
        UserPageVisit.objects.create(user=self.icap, section=descendants[0])

        self.student = StudentProfileFactory(
            country=self.old_group.school.country).user  # unaffiliated user
        UserPageVisit.objects.create(user=self.student, section=descendants[0])

        pretest = Quiz.objects.create()
        q1 = Question.objects.create(
            quiz=pretest, text='single answer',
            question_type='single choice')
        Answer.objects.create(question=q1, label='Yes', value='1',
                              correct=True)
        Answer.objects.create(question=q1, label='No', value='0')

        posttest = Quiz.objects.create()
        q2 = Question.objects.create(
            quiz=posttest, text='single answer',
            question_type='single choice')
        Answer.objects.create(question=q2, label='Yes', value='1',
                              correct=True)
        Answer.objects.create(question=q2, label='No', value='0')

        section = Section.objects.get(slug='two')
        section.append_pageblock('Quiz', 'pretest', content_object=pretest)
        section = Section.objects.get(slug='four')
        section.append_pageblock('Quiz', 'posttest', content_object=posttest)

        # answer the pretest
        s = Submission.objects.create(quiz=pretest, user=complete_user)
        Response.objects.create(question=q1, submission=s, value='0')

        # answer the posttest
        s = Submission.objects.create(quiz=posttest, user=complete_user)
        Response.objects.create(question=q2, submission=s, value='1')


class TestReportView(TestReportBase):

    def test_not_logged_in(self):
        # not logged in
        response = self.client.get(self.report_view_url)
        self.assertEqual(response.status_code, 302)

    def test_student(self):
        # student
        self.client.login(username=self.student.username, password="test")
        response = self.client.get(self.report_view_url)
        self.assertEqual(response.status_code, 403)

    def test_icap(self):
        # faculty
        self.client.login(username=self.icap.username, password="test")
        response = self.client.get(self.report_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['user'], self.icap)
        self.assertEqual(len(response.context_data['countries']), 5)


class TestDownloadableReportView(TestReportBase):

    def test_post(self):
        # not logged in
        response = self.client.post(self.report_download_url)
        self.assertEqual(response.status_code, 302)

        # student
        self.client.login(username=self.student.username, password="test")
        data = {'country': 'all'}
        response = self.client.post(self.report_download_url, data)
        self.assertEqual(response.status_code, 403)

        # faculty
        self.client.login(username=self.icap.username, password="test")
        data = {'country': 'all'}
        response = self.client.post(self.report_download_url, data)
        self.assertEqual(response.status_code, 200)

    def test_aggregate_report_all_countries(self):
        data = {'country': 'all'}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEqual(next(rows), ['CRITERIA'])
        self.assertEqual(next(rows),
                         ['Country', 'Institution', 'Group', 'Total Members'])
        self.assertEqual(next(rows), ["All Countries", None, None, 4])

        next(rows)  # separator
        self.assertEqual(next(rows), ['LANGUAGE'])  # header
        self.assertEqual(next(rows), ['English'])

        next(rows)  # separator
        self.assertEqual(next(rows), ['STUDENT PROGRESS'])  # header
        self.assertEqual(next(rows),
                         ['Completed', 'Incomplete', 'In Progress'])
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEqual(next(rows), [1, 0, 3])

        # aggregates are in row 4-8
        next(rows)  # separator
        self.assertEqual(next(rows), ['COMPLETED USER AVERAGES'])
        self.assertEqual(next(rows), ['Completed', 1])
        self.assertEqual(next(rows), ['Pre-test Score', 0])
        self.assertEqual(next(rows), ['Post-test Score', 100])
        self.assertEqual(next(rows), ['Pre/Post Change', 100])
        self.assertEqual(next(rows), ['Satisfaction Score', None])

    def test_aggregate_report_country_unaffiliated(self):
        country = self.old_group.school.country
        data = {'country': country.name,
                'school': 'unaffiliated'}

        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEqual(next(rows), ['CRITERIA'])
        self.assertEqual(next(rows),
                         ['Country', 'Institution', 'Group', 'Total Members'])
        self.assertEqual(
            next(rows),
            [country.display_name, 'Unaffiliated Students', None, 1])
        next(rows)  # header
        next(rows)  # header
        self.assertEqual(next(rows), ['English'])
        next(rows)  # header
        next(rows)  # header
        next(rows)  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEqual(next(rows), [0, 0, 1])

    def test_aggregate_report_all_schools(self):
        country = self.new_group.school.country
        data = {'country': country.name,
                'school': 'all'}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEqual(next(rows), ['CRITERIA'])
        self.assertEqual(next(rows),
                         ['Country', 'Institution', 'Group', 'Total Members'])
        self.assertEqual(
            next(rows),
            [country.display_name, 'All Institutions', None, 2])
        next(rows)  # header
        next(rows)  # header
        self.assertEqual(next(rows), ['English'])
        next(rows)  # header
        next(rows)  # header
        next(rows)  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEqual(next(rows), [1, 0, 1])

    def test_aggregate_report_all_groups(self):
        # country + institution specified
        country = self.old_group.school.country
        school = self.old_group.school
        data = {'country': country.name,
                'school': school.pk}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEqual(next(rows), ['CRITERIA'])
        self.assertEqual(next(rows),
                         ['Country', 'Institution', 'Group', 'Total Members'])
        self.assertEqual(
            next(rows),
            [country.display_name, school.name, None, 1])
        next(rows)  # header
        next(rows)  # header
        self.assertEqual(next(rows), ['English'])
        next(rows)  # header
        next(rows)  # header
        next(rows)  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEqual(next(rows), [0, 1, 0])

    def test_aggregate_report_single_group(self):
        # group id is specified
        group = self.old_group
        country = self.old_group.school.country
        school = self.old_group.school
        data = {'country': country.name,
                'school': school.pk,
                'schoolgroup': group.pk}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEqual(next(rows), ['CRITERIA'])
        self.assertEqual(next(rows),
                         ['Country', 'Institution', 'Group', 'Total Members'])
        self.assertEqual(
            next(rows),
            [country.display_name, school.name, group.name, 1])
        next(rows)  # header
        next(rows)  # header
        self.assertEqual(next(rows), ['English'])
        next(rows)  # header
        next(rows)  # header
        next(rows)  # header
        self.assertEqual(next(rows), [0, 1, 0])

    def test_detailed_report_values(self):
        with self.settings(PARTICIPANT_SECRET='foo'):
            data = {'country': 'all'}
            request = RequestFactory().post(self.report_download_url, data)
            request.user = self.icap

            view = DownloadableReportView()
            view.request = request

            users, groups = view.get_users_and_groups(request, self.hierarchy)

            rows = view.get_detailed_report_values(self.hierarchies, users)
            row = ['participant_id', 'country', 'group', 'completed',
                   'percent_complete', 'total_time_elapsed',
                   'actual_time_spent', 'completion_date', 'pre-test score',
                   'post-test score', '1_1', '1_2']
            self.assertEqual(next(rows), row)

            # expecting 4 user results to show up
            row = next(rows)
            row = next(rows)
            row = next(rows)
            row = next(rows)

            try:
                next(rows)
                self.assertFalse('unexpected row')
            except StopIteration:
                pass  # expected

    def test_detailed_report_keys(self):
        data = {'country': 'all'}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        rows = view.get_detailed_report_keys(self.hierarchies)

        row = ['hierarchy', 'itemIdentifier', 'exercise type', 'itemType',
               'itemText', 'answerIdentifier', 'answerText']
        self.assertEqual(next(rows), row)

        self.assertEqual(next(rows), '')

        row = ['', 'participant_id', 'profile', 'string',
               'Randomized Participant Id']
        self.assertEqual(next(rows), row)

        row = ['', 'country', 'profile', 'string', 'affiliated country']
        self.assertEqual(next(rows), row)

        row = ['', 'group', 'profile', 'list', 'Groups']
        self.assertEqual(next(rows), row)

        row = ['', 'completed', 'profile', 'boolean',
               'pages visits + pre + post tests']
        self.assertEqual(next(rows), row)

        row = ['', 'percent_complete', 'profile', 'percent',
               '% of hierarchy completed']
        self.assertEqual(next(rows), row)

        row = ['', 'total_time_elapsed', 'profile', 'hours:minutes:seconds',
               'total time period over which the module was accessed']
        self.assertEqual(next(rows), row)

        row = ['', 'actual_time_spent', 'profile', 'hours:minutes:seconds',
               'actual time spent completing the module']
        self.assertEqual(next(rows), row)

        row = ['', 'completion_date', 'profile', 'date/time',
               'the date the user completed the module']
        self.assertEqual(next(rows), row)

        row = ['', 'pre-test score', 'profile', 'percent',
               'Pre-test Score']
        self.assertEqual(next(rows), row)

        row = ['', 'post-test score', 'profile', 'percent',
               'Post-test Score']
        self.assertEqual(next(rows), row)

        row = ['optionb-en', '1_1', 'Quiz', 'single choice',
               b'single answer', 1, b'Yes']
        self.assertEqual(next(rows), row)

        row = ['optionb-en', '1_1', 'Quiz', 'single choice',
               b'single answer', 2, b'No']
        self.assertEqual(next(rows), row)

        row = ['optionb-en', '1_2', 'Quiz', 'single choice',
               b'single answer', 3, b'Yes']
        self.assertEqual(next(rows), row)

        row = ['optionb-en', '1_2', 'Quiz', 'single choice',
               b'single answer', 4, b'No']
        self.assertEqual(next(rows), row)

        try:
            next(rows)
            self.assertFalse('unexpected row')
        except StopIteration:
            pass  # expected

    def test_detailed_report_values_no_users(self):
        group = SchoolGroupFactory()
        country = group.school.country
        school = group.school
        data = {'country': country.name,
                'school': school.pk,
                'schoolgroup': 'all',
                'report-type': 'values'}

        self.client.login(username=self.icap.username, password="test")
        response = self.client.post(self.report_download_url, data)
        self.assertEqual(response.status_code, 200)

        row = (b'participant_id,country,group,completed,percent_complete,'
               b'total_time_elapsed,actual_time_spent,completion_date,'
               b'pre-test score,post-test score,1_1,1_2\r\n')
        self.assertEqual(row, next(response.streaming_content))  # header row
        with self.assertRaises(StopIteration):
            next(response.streaming_content)


class TestBaseReportMixin(TestReportBase):

    def test_get_country_and_school(self):
        data = {'school': self.new_group.school.id,
                'country': self.new_group.school.country.name}
        request = self.factory.post(self.report_download_url, data)

        mixin = BaseReportMixin()

        teacher = TeacherProfileFactory(school=self.old_group.school,
                                        country=self.old_group.school.country)
        request.user = teacher.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEqual(country_name, self.old_group.school.country.name)
        self.assertEqual(school_id, self.old_group.school.id)

        school = InstitutionAdminProfileFactory(
            school=self.old_group.school,
            country=self.old_group.school.country)
        request.user = school.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEqual(country_name, self.old_group.school.country.name)
        self.assertEqual(school_id, self.old_group.school.id)

        country = CountryAdministratorProfileFactory(
            country=self.old_group.school.country)
        request.user = country.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEqual(country_name, self.old_group.school.country.name)
        self.assertEqual(int(school_id), self.new_group.school.id)

        data = {'school': self.old_group.school.id,
                'country': self.old_group.school.country.name}
        request = self.factory.post(self.report_download_url, data)
        request.user = country.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEqual(country_name, self.old_group.school.country.name)
        self.assertEqual(int(school_id), self.old_group.school.id)

        request.user = self.icap
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEqual(country_name, self.old_group.school.country.name)
        self.assertEqual(int(school_id), self.old_group.school.id)

    def test_get_country_criteria(self):
        mixin = BaseReportMixin()
        data = {'country': 'all'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_country_criteria(request), 'All Countries')

        data = {'country': self.new_group.school.country.name}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_country_criteria(request),
                         self.new_group.school.country.display_name)

        data = {'country': 'foo'}
        request = self.factory.post(self.report_download_url, data)
        self.assertIsNone(mixin.get_country_criteria(request))

    def test_get_school_criteria(self):
        mixin = BaseReportMixin()
        data = {'school': '1234'}
        request = self.factory.post(self.report_download_url, data)
        self.assertIsNone(mixin.get_school_criteria(request))

        data = {'school': 'all'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_school_criteria(request),
                         'All Institutions')

        data = {'school': 'unaffiliated'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_school_criteria(request),
                         'Unaffiliated Students')

        data = {'school': self.new_group.school.id}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_school_criteria(request),
                         self.new_group.school.name)

    def test_get_group_criteria(self):
        mixin = BaseReportMixin()
        data = {'schoolgroup': '1234'}
        request = self.factory.post(self.report_download_url, data)
        self.assertIsNone(mixin.get_group_criteria(request))

        data = {'schoolgroup': 'all'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_group_criteria(request), 'All Groups')

        data = {'schoolgroup': self.new_group.id}
        request = self.factory.post(self.report_download_url, data)
        self.assertEqual(mixin.get_group_criteria(request),
                         self.new_group.name)
