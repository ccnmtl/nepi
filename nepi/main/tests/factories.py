from datetime import datetime
from django.contrib.auth.models import User
from nepi.main.models import (Country,
                              School,
                              Group,
                              UserProfile)
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country

    name = factory.Sequence(lambda n: "%d" % (n))
    display_name = factory.Sequence(lambda n: "country %d" % n)


class SchoolFactory(factory.DjangoModelFactory):
    FACTORY_FOR = School
    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: "school %d" % n)


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    school = factory.SubFactory(SchoolFactory)
    creator = factory.SubFactory(UserFactory)
    name = "A Group"
    start_date = datetime.now()
    end_date = datetime.now()


class UserProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = 'ST'
    country = factory.SubFactory(CountryFactory)
    school = factory.SubFactory(SchoolFactory)


class StudentProfileFactory(UserProfileFactory):
    profile_type = 'ST'


class TeacherProfileFactory(UserProfileFactory):
    profile_type = 'TE'


class ICAPProfileFactory(UserProfileFactory):
    profile_type = 'IC'
