from datetime import date
from django.test.testcases import TestCase
from nepi.main.tests.factories import SchoolGroupFactory, \
    StudentProfileFactory, ICAPProfileFactory
from pagetree.models import Hierarchy, UserPageVisit
from pagetree.tests.factories import ModuleFactory
import datetime
import json


class TestAggregateReportView(TestCase):

    def setUp(self):
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

        self.icap = ICAPProfileFactory().user
        self.student = StudentProfileFactory().user

    def test_report_access(self):
        # not logged in
        response = self.client.post('/dashboard/reports/aggregate/')
        self.assertEquals(response.status_code, 405)

        # non-ajax
        self.client.login(username=self.icap.username, password="test")
        response = self.client.post('/dashboard/reports/aggregate/')
        self.assertEquals(response.status_code, 405)

        # student
        self.client.login(username=self.student.username, password="test")
        data = {'country': 'all'}
        response = self.client.post('/dashboard/reports/aggregate/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_report_all_countries(self):
        self.client.login(username=self.icap.username, password="test")

        data = {'country': 'all'}
        response = self.client.post('/dashboard/reports/aggregate/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        ctx = json.loads(response.content)
        self.assertEquals(ctx['total'], 3)
        self.assertEquals(ctx['completed'], 1)
        self.assertEquals(ctx['incomplete'], 1)
        self.assertEquals(ctx['inprogress'], 1)

    def test_report_all_schools(self):
        self.client.login(username=self.icap.username, password="test")

        data = {'country': self.new_group.school.country.name,
                'school': 'all'}
        response = self.client.post('/dashboard/reports/aggregate/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        ctx = json.loads(response.content)
        self.assertEquals(ctx['total'], 2)
        self.assertEquals(ctx['completed'], 1)
        self.assertEquals(ctx['incomplete'], 0)
        self.assertEquals(ctx['inprogress'], 1)

    def test_report_all_groups(self):
        # country + institution specified
        self.client.login(username=self.icap.username, password="test")

        data = {'country': self.old_group.school.country.name,
                'school': self.old_group.school.pk}
        response = self.client.post('/dashboard/reports/aggregate/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        ctx = json.loads(response.content)
        self.assertEquals(ctx['total'], 1)
        self.assertEquals(ctx['completed'], 0)
        self.assertEquals(ctx['incomplete'], 1)
        self.assertEquals(ctx['inprogress'], 0)

    def test_report_single_group(self):
        # group id is specified
        self.client.login(username=self.icap.username, password="test")
        data = {'group': self.old_group.pk}
        response = self.client.post('/dashboard/reports/aggregate/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        ctx = json.loads(response.content)
        self.assertEquals(ctx['total'], 1)
        self.assertEquals(ctx['completed'], 0)
        self.assertEquals(ctx['incomplete'], 1)
        self.assertEquals(ctx['inprogress'], 0)
