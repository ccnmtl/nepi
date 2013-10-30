from django.test import TestCase
from django.contrib.auth.models import User
from pagetree.models import Hierarchy, Section
from nepi.main.models import UserProfile
from django import forms

class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')
        UserProfile.objects.get_or_create(user=self.user)[0]
        self.hierarchy = Hierarchy(name="main", base_url="/")
        self.hierarchy.save()

        root = Section.add_root(label="Root", slug="",
                                hierarchy=self.hierarchy)

        root.append_child("Section 1", "section-1")
        root.append_child("Section 2", "section-2")

        self.section1 = Section.objects.get(slug="section-1")
        self.section2 = Section.objects.get(slug="section-2")

    def tearDown(self):
        self.user.delete()
        self.hierarchy.delete()

    def test_set_has_visited(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(profile.get_has_visited(self.section1))
        self.assertFalse(profile.get_has_visited(self.section2))

        profile.set_has_visited([self.section1, self.section2])

        self.assertTrue(profile.get_has_visited(self.section1))
        self.assertTrue(profile.get_has_visited(self.section2))

    def test_set_last_location(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(profile.get_has_visited(self.section1))
        self.assertFalse(profile.get_has_visited(self.section2))

        profile.save_last_location('/section-1/', self.section1)

        self.assertTrue(profile.get_has_visited(self.section1))
        self.assertFalse(profile.get_has_visited(self.section2))

    def test_user_unicode(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)
        uni_name = UserProfile.__unicode__(profile)
        self.assertEqual(uni_name, 'test_student')

    def test_user_display_name(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)
        display_name = UserProfile.display_name(profile)
        self.assertEqual(display_name, 'test_student')

