import datetime
from django.contrib.auth.models import User
from nepi.main.models import Country, School, Group, UserProfile, \
    PendingTeachers
import factory
import random
import string


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    last_name = factory.Sequence(lambda n: "Last%d" % n)
    first_name = factory.Sequence(lambda n: "First%d" % n)
    email = factory.Sequence(lambda n: "username%d@localhost" % n)


def country_choice(n):
    cc = ''.join(random.choice(string.ascii_uppercase)  # nosec
                 for _ in range(2))
    while Country.objects.filter(name=cc):
        cc = ''.join(random.choice(string.ascii_uppercase)  # nosec
                     for _ in range(2))
    return cc


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    name = factory.Sequence(lambda n: country_choice(n))
    display_name = factory.Sequence(lambda n: "country %d" % n)


class SchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = School
    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: "school %d" % n)


class SchoolGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    school = factory.SubFactory(SchoolFactory)
    creator = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: "group %d" % n)
    start_date = datetime.date.today()
    end_date = datetime.date.today()


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = 'ST'
    country = factory.SubFactory(CountryFactory)


class StudentProfileFactory(UserProfileFactory):
    profile_type = 'ST'


class TeacherProfileFactory(UserProfileFactory):
    profile_type = 'TE'
    school = factory.SubFactory(SchoolFactory)


class InstitutionAdminProfileFactory(UserProfileFactory):
    profile_type = 'IN'
    school = factory.SubFactory(SchoolFactory)


class ICAPProfileFactory(UserProfileFactory):
    profile_type = 'IC'


class CountryAdministratorProfileFactory(UserProfileFactory):
    profile_type = 'CA'


class PendingTeacherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PendingTeachers
    user_profile = factory.SubFactory(StudentProfileFactory)
    school = factory.SubFactory(SchoolFactory)
