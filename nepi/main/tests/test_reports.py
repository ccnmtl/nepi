from datetime import date
import datetime
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pagetree.models import Hierarchy, UserPageVisit
from pagetree.tests.factories import ModuleFactory

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
            UserPageVisit.objects.create(user=complete_user, section=section)

        inprogress_user = \
            StudentProfileFactory(school=self.new_group.school).user
        self.new_group.userprofile_set.add(inprogress_user.profile)
        UserPageVisit.objects.create(user=inprogress_user,
                                     section=descendants[0])

        self.icap = ICAPProfileFactory(
            country=self.new_group.school.country).user
        UserPageVisit.objects.create(user=self.icap, section=descendants[0])

        self.student = StudentProfileFactory(
            country=self.old_group.school.country).user  # unaffiliated user
        UserPageVisit.objects.create(user=self.student, section=descendants[0])


class TestReportView(TestReportBase):

    def test_not_logged_in(self):
        # not logged in
        response = self.client.get(self.report_view_url)
        self.assertEquals(response.status_code, 302)

    def test_student(self):
        # student
        self.client.login(username=self.student.username, password="test")
        response = self.client.get(self.report_view_url)
        self.assertEquals(response.status_code, 403)

    def test_icap(self):
        # faculty
        self.client.login(username=self.icap.username, password="test")
        response = self.client.get(self.report_view_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['user'], self.icap)
        self.assertEquals(len(response.context_data['countries']), 5)


class TestDownloadableReportView(TestReportBase):

    def test_post(self):
        # not logged in
        response = self.client.post(self.report_download_url)
        self.assertEquals(response.status_code, 302)

        # student
        self.client.login(username=self.student.username, password="test")
        data = {'country': 'all'}
        response = self.client.post(self.report_download_url, data)
        self.assertEquals(response.status_code, 403)

        # faculty
        self.client.login(username=self.icap.username, password="test")
        data = {'country': 'all'}
        response = self.client.post(self.report_download_url, data)
        self.assertEquals(response.status_code, 200)

    def test_aggregate_report_all_countries(self):
        data = {'country': 'all'}
        request = RequestFactory().post(self.report_download_url, data)
        request.user = self.icap

        view = DownloadableReportView()
        view.request = request

        users, groups = view.get_users_and_groups(request, self.hierarchy)

        rows = view.get_aggregate_report(
            request, self.hierarchy, users, groups)
        self.assertEquals(rows.next(), ['CRITERIA'])
        self.assertEquals(rows.next(), ['Country', 'Institution', 'Group'])
        self.assertEquals(rows.next(), ["All Countries", None, None])

        self.assertEquals(rows.next(), ['MEMBERS'])  # header
        self.assertEquals(
            rows.next(),
            ['Total Users', 'Completed', 'Incomplete', 'In Progress'])
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEquals(rows.next(), [4, 1, 0, 3])

        # aggregates are in row 4-8
        rows.next()  # header
        self.assertEquals(rows.next(), ['Completed', 1])
        self.assertEquals(rows.next(), ['Pre-test Score', None])
        self.assertEquals(rows.next(), ['Post-test Score', None])
        self.assertEquals(rows.next(), ['Pre/Post Change', None])
        self.assertEquals(rows.next(), ['Satisfaction Score', None])

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
        self.assertEquals(rows.next(), ['CRITERIA'])
        self.assertEquals(rows.next(), ['Country', 'Institution', 'Group'])
        self.assertEquals(
            rows.next(),
            [country.display_name, 'Unaffiliated Students', None])
        rows.next()  # header
        rows.next()  # header

        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEquals(rows.next(), [1, 0, 0, 1])

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
        self.assertEquals(rows.next(), ['CRITERIA'])
        self.assertEquals(rows.next(), ['Country', 'Institution', 'Group'])
        self.assertEquals(
            rows.next(),
            [country.display_name, 'All Institutions', None])
        rows.next()  # header
        rows.next()  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEquals(rows.next(), [2, 1, 0, 1])

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
        self.assertEquals(rows.next(), ['CRITERIA'])
        self.assertEquals(rows.next(), ['Country', 'Institution', 'Group'])
        self.assertEquals(
            rows.next(),
            [country.display_name, school.name, None])
        rows.next()  # header
        rows.next()  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEquals(rows.next(), [1, 0, 1, 0])

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
        self.assertEquals(rows.next(), ['CRITERIA'])
        self.assertEquals(rows.next(), ['Country', 'Institution', 'Group'])
        self.assertEquals(
            rows.next(),
            [country.display_name, school.name, group.name])
        rows.next()  # header
        rows.next()  # header
        # counts are in row 2. total, completed, incomplete inprogress
        self.assertEquals(rows.next(), [1, 0, 1, 0])

    def test_detailed_report_values(self):
        with self.settings(PARTICIPANT_SECRET='foo'):
            data = {'country': 'all'}
            request = RequestFactory().post(self.report_download_url, data)
            request.user = self.icap

            view = DownloadableReportView()
            view.request = request

            users, groups = view.get_users_and_groups(request, self.hierarchy)

            rows = view.get_detailed_report_values(self.hierarchies, users)
            row = ['participant_id', 'country', 'group', 'percent_complete',
                   'total_time_elapsed', 'actual_time_spent',
                   'completion_date']
            self.assertEquals(rows.next(), row)

            # expecting 4 user results to show up
            row = rows.next()
            row = rows.next()
            row = rows.next()
            row = rows.next()

            try:
                rows.next()
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
        self.assertEquals(rows.next(), row)

        self.assertEquals(rows.next(), '')

        row = ['', 'participant_id', 'profile', 'string',
               'Randomized Participant Id']
        self.assertEquals(rows.next(), row)

        row = ['', 'country', 'profile', 'string', 'affiliated country']
        self.assertEquals(rows.next(), row)

        row = ['', 'group', 'profile', 'list', 'Groups']
        self.assertEquals(rows.next(), row)

        row = ['', 'percent_complete', 'profile', 'percent',
               '% of hierarchy completed']
        self.assertEquals(rows.next(), row)

        row = ['', 'total_time_elapsed', 'profile', 'hours:minutes:seconds',
               'total time period over which the module was accessed']
        self.assertEquals(rows.next(), row)

        row = ['', 'actual_time_spent', 'profile', 'hours:minutes:seconds',
               'actual time spent completing the module']
        self.assertEquals(rows.next(), row)

        row = ['', 'completion_date', 'profile', 'date/time',
               'the date the user completed the module']
        self.assertEquals(rows.next(), row)

        try:
            rows.next()
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
        self.assertEquals(response.status_code, 200)

        row = ('participant_id,country,group,percent_complete,'
               'total_time_elapsed,actual_time_spent,completion_date\r\n')
        self.assertEquals(row, response.streaming_content.next())  # header row
        with self.assertRaises(StopIteration):
            response.streaming_content.next()


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
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(school_id, self.old_group.school.id)

        school = InstitutionAdminProfileFactory(
            school=self.old_group.school,
            country=self.old_group.school.country)
        request.user = school.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(school_id, self.old_group.school.id)

        country = CountryAdministratorProfileFactory(
            country=self.old_group.school.country)
        request.user = country.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(int(school_id), self.new_group.school.id)

        data = {'school': self.old_group.school.id,
                'country': self.old_group.school.country.name}
        request = self.factory.post(self.report_download_url, data)
        request.user = country.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(int(school_id), self.old_group.school.id)

        request.user = self.icap
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(int(school_id), self.old_group.school.id)

    def test_get_country_criteria(self):
        mixin = BaseReportMixin()
        data = {'country': 'all'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_country_criteria(request), 'All Countries')

        data = {'country': self.new_group.school.country.name}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_country_criteria(request),
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
        self.assertEquals(mixin.get_school_criteria(request),
                          'All Institutions')

        data = {'school': 'unaffiliated'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_school_criteria(request),
                          'Unaffiliated Students')

        data = {'school': self.new_group.school.id}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_school_criteria(request),
                          self.new_group.school.name)

    def test_get_group_criteria(self):
        mixin = BaseReportMixin()
        data = {'schoolgroup': '1234'}
        request = self.factory.post(self.report_download_url, data)
        self.assertIsNone(mixin.get_group_criteria(request))

        data = {'schoolgroup': 'all'}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_group_criteria(request), 'All Groups')

        data = {'schoolgroup': self.new_group.id}
        request = self.factory.post(self.report_download_url, data)
        self.assertEquals(mixin.get_group_criteria(request),
                          self.new_group.name)
