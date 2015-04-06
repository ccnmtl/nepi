from datetime import date
import datetime

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pagetree.models import Hierarchy, UserPageVisit
from pagetree.tests.factories import ModuleFactory

from nepi.main.tests.factories import SchoolGroupFactory, \
    StudentProfileFactory, ICAPProfileFactory, TeacherProfileFactory, \
    InstitutionAdminProfileFactory, CountryAdministratorProfileFactory
from nepi.main.views import BaseReportMixin, DownloadableReportView


class TestReportView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
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
        self.student = StudentProfileFactory(
            country=self.old_group.school.country).user  # unaffiliated user

    def test_report_access(self):
        # not logged in
        response = self.client.post('/dashboard/reports/')
        self.assertEquals(response.status_code, 302)

        # non-ajax
        self.client.login(username=self.icap.username, password="test")
        response = self.client.post('/dashboard/reports/')
        self.assertEquals(response.status_code, 405)

        # student
        self.client.login(username=self.student.username, password="test")
        data = {'country': 'all'}
        response = self.client.post('/dashboard/reports/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_report_all_countries(self):
        data = {'country': 'all'}
        request = RequestFactory().post('/dashboard/reports', data)
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
        self.assertEquals(rows.next(), [4, 1, 0, 2])

        # aggregates are in row 4-8
        rows.next()  # header
        self.assertEquals(rows.next(), ['Completed', 1])
        self.assertEquals(rows.next(), ['Pre-test Score', None])
        self.assertEquals(rows.next(), ['Post-test Score', None])
        self.assertEquals(rows.next(), ['Pre/Post Change', None])
        self.assertEquals(rows.next(), ['Satisfaction Score', None])

    def test_report_country_unaffiliated(self):
        country = self.old_group.school.country
        data = {'country': country.name,
                'school': 'unaffiliated'}

        request = RequestFactory().post('/dashboard/reports', data)
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
        self.assertEquals(rows.next(), [1, 0, 0, 0])

    def test_report_all_schools(self):
        country = self.new_group.school.country
        data = {'country': country.name,
                'school': 'all'}
        request = RequestFactory().post('/dashboard/reports', data)
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

    def test_report_all_groups(self):
        # country + institution specified
        country = self.old_group.school.country
        school = self.old_group.school
        data = {'country': country.name,
                'school': school.pk}
        request = RequestFactory().post('/dashboard/reports', data)
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

    def test_report_single_group(self):
        # group id is specified
        group = self.old_group
        country = self.old_group.school.country
        school = self.old_group.school
        data = {'country': country.name,
                'school': school.pk,
                'schoolgroup': group.pk}
        request = RequestFactory().post('/dashboard/reports', data)
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

    def test_get_country_and_school(self):
        data = {'school': self.new_group.school.id,
                'country': self.new_group.school.country.name}
        request = self.factory.post('/dashboard/reports/aggregate/', data)

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
        request = self.factory.post('/dashboard/reports/aggregate/', data)
        request.user = country.user
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(int(school_id), self.old_group.school.id)

        request.user = self.icap
        (country_name, school_id) = mixin.get_country_and_school(request)
        self.assertEquals(country_name, self.old_group.school.country.name)
        self.assertEquals(int(school_id), self.old_group.school.id)
