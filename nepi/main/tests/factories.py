from datetime import datetime
from django.contrib.auth.models import User
from nepi.main.models import Country, School, Course
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    name = "LS"
    region = "Region 1"


class SchoolFactory(factory.DjangoModelFactory):
    FACTORY_FOR = School
    country = factory.SubFactory(CountryFactory)
    name = "Test School"


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course
    school = factory.SubFactory(SchoolFactory)
    semester = "Fall"
    name = "A Course"
    start_date = datetime.now()
    end_date = datetime.now()
