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

        old_group = SchoolGroupFactory(end_date=date(2007, 12, 25),
                                       module=self.hierarchy)
        incomplete_user = StudentProfileFactory(school=old_group.school).user
        UserPageVisit.objects.create(user=incomplete_user,
                                     section=descendants[0])
        old_group.userprofile_set.add(incomplete_user.profile)

        new_group = SchoolGroupFactory(end_date=datetime.date.today(),
                                       module=self.hierarchy)

        complete_user = StudentProfileFactory(school=new_group.school).user
        new_group.userprofile_set.add(complete_user.profile)
        for section in descendants:
            UserPageVisit.objects.create(user=complete_user, section=section)

        inprogress_user = StudentProfileFactory(school=new_group.school).user
        new_group.userprofile_set.add(inprogress_user.profile)
        UserPageVisit.objects.create(user=inprogress_user,
                                     section=descendants[0])

        self.icap = ICAPProfileFactory().user
        self.student = StudentProfileFactory().user

    def test_report_access(self):
        # not logged in
        response = self.client.post('/dashboard/reports/aggregate/')
        self.assertEquals(response.status_code, 302)

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
        # country is specified
        pass

    def test_report_all_groups(self):
        # country + institution specified
        pass

    def test_report_single_group(self):
        # group id is specified
        pass
