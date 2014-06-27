from datetime import datetime
from django.contrib.auth.models import User
from nepi.main.models import (Country,
                              School,
                              Group,
                              UserProfile)
from pagetree.models import Hierarchy
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    name = "LS"


class SchoolFactory(factory.DjangoModelFactory):
    FACTORY_FOR = School
    country = factory.SubFactory(CountryFactory)
    name = "Test School"


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


class HierarchyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hierarchy
    name = "main"
    base_url = "/"

    @factory.post_generation
    def populate(self, create, extracted, **kwargs):
        self.get_root().add_child_section_from_dict(
            {
                'label': 'Welcome',
                'slug': 'welcome',
                'pageblocks': [
                    {'label': 'Welcome to your new Site',
                     'css_extra': '',
                     'block_type': 'Text Block',
                     'body': 'You should now use the edit link to add content',
                     },
                ],
                'children': [],
            })
