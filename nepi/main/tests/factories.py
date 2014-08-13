from datetime import datetime
from django.contrib.auth.models import User
from nepi.main.models import Country, School, Group, UserProfile, \
    PendingTeachers
import factory
import random
import string


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


def country_choice(n):
    cc = ''.join(random.choice(string.ascii_uppercase + string.digits)
                 for _ in range(2))
    while Country.objects.filter(name=cc):
        cc = ''.join(random.choice(string.ascii_uppercase + string.digits)
                     for _ in range(2))
    return cc


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country

    name = factory.Sequence(lambda n: country_choice(n))
    display_name = factory.Sequence(lambda n: "country %d" % n)


class SchoolFactory(factory.DjangoModelFactory):
    FACTORY_FOR = School
    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: "school %d" % n)


class SchoolGroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    school = factory.SubFactory(SchoolFactory)
    creator = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: "group %d" % n)
    start_date = datetime.now()
    end_date = datetime.now()


class UserProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
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


class PendingTeacherFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PendingTeachers
    user_profile = factory.SubFactory(StudentProfileFactory)
    school = factory.SubFactory(SchoolFactory)
