from django.contrib.auth.models import User
from nepi.main.models import Country
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    name = "LS"
    region = "Region 1"
