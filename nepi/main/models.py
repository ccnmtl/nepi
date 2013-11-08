from django.db import models
from django.forms import ModelForm
from django.db.models import signals
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django import forms

'''Add change delete are by default for each django model.
   Need to add permissions for visibility.'''


class Country(models.Model):
    #note : non soverign countries and partially recognized
    #and unrecognized states were not included in this list, 
    #other areas canary islands and such are also not included
    ALGERIA = 'DZ'
    ANGOLA = 'AO'
    BENIN = 'BJ'
    BOTSWANA = 'BW'
    BURINKAFASO = 'BF'
    BURUNDI = 'BI'
    CAMEROON = 'CM'
    CAPEVERDE = 'CV'
    CENTRALAFRICANREPUBLIC = 'CF'
    CHAD = 'TD'
    COMORORS = 'KM'
    COTEDIVOIR = 'CI'
    DEMOCRATICREPUBLICOFCONGO = 'CD'
    DJIBOUTI = 'DJ'
    EGPYT = 'EG'
    EQUITORIALGUINEA = 'GQ'
    ERITEA = 'ER'
    ETHIOPIA = 'ET'
    GABON = 'GA'
    GAMBIA = 'GM'
    GHANA = 'GH'
    GUINEA = 'GN'
    GUINEABISSU = 'GW'
    KENYA = 'KE'
    LESOTHO = 'LS'
    LIBERIA = 'LR'
    LIBYA = 'LY'
    MADAGASCAR = 'MG'
    MALAWI = 'MW'
    MALI = 'ML'
    MAURITANIA = 'MR'
    MAURITIUS = 'MU'
    MOROCCO = 'MA'
    MOZAMBIQUE = 'MZ'
    NAMBIA = 'NA'
    NIGER = 'NE'
    NIGERIA = 'NG'
    #REPUBLICOFCONGO = ''
    RWANDA = 'RW'
    SAOTOMEANDPRINCIPE = 'ST'
    SENEGAL = 'SN'
    SEYCHELLES = 'SC'
    SIERRALEONE = 'SL'
    SOMALIA = 'SO'
    SOUTHAFRICA = 'ZA'
    #SOUTHSUDAN = ''
    SUDAN = 'SD'
    SWAZILAND = 'SZ'
    TANZANIA = 'TZ'
    TOGO = 'TG'
    TUNISIA = 'TN'
    UGANDA = 'UG'
    ZAMBIA = 'ZM'
    ZIMBABWE = 'ZW'


    # http://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_Africa
    # http://sustainablesources.com/resources/country-abbreviations/
    # http://www.paladinsoftware.com/Generic/countries.htm

    COUNTRY_CHOICES = (

        (ALGERIA, 'Algeria'),
        (ANGOLA, 'Angola'),
        (BENIN, 'Benin'),
        (BOTSWANA, 'Botswana'),
        (BURINKAFASO, 'Burinka Faso'),
        (BURUNDI, 'Burundi'),
        (CAMEROON, 'Cameroon'),
        (CAPEVERDE, 'Cape Verde'),
        (CENTRALAFRICANREPUBLIC, 'Central African Republic'),
        (CHAD, 'Chad'),
        (COMORORS, 'Comorors'),
        (COTEDIVOIR, 'Cote D\'Voir'),
        (DEMOCRATICREPUBLICOFCONGO, 'Democratic Republic of Congo'),
        (DJIBOUTI, 'Djibouti'),
        (EGPYT, 'Egypt'),
        (EQUITORIALGUINEA, 'Equitorial Guinea'),
        (ERITEA, 'Eritrea'),
        (ETHIOPIA, 'Ethiopia'),
        (GABON, 'Gabon'),
        (GAMBIA, 'Gambia'),
        (GHANA, 'Ghana'),
        (GUINEA, 'Guinea'),
        (GUINEABISSU, 'Guinea Bissu'),
        (KENYA, 'Kenya'),
        (LESOTHO, 'Lesotho'),
        (LIBERIA, 'Liberia'),
        (LIBYA, 'Libya'),
        (MADAGASCAR, 'Madagascar'),
        (MALAWI, 'Malawi'),
        (MALI, 'Mali'),
        (MAURITANIA, 'Mauritania'),
        (MAURITIUS, 'Mauritius'),
        (MOROCCO, 'Morocco'),
        (MOZAMBIQUE, 'Mozambique'),
        (NAMBIA, 'Nabia'),
        (NIGER, 'Niger'),
        (NIGERIA, 'Nigeria'),
        #(REPUBLICOFCONGO, 'Republic of Congo'),
        (RWANDA, 'Rawanda'),
        (SAOTOMEANDPRINCIPE, 'Sao Tome and Principe'),
        (SENEGAL, 'Senegal'),
        (SEYCHELLES, 'Seychelles'),
        (SIERRALEONE, 'Sierraleone'),
        (SOMALIA, 'Somalia'),
        (SOUTHAFRICA, 'South Africa'),
        #(SOUTHSUDAN, 'South Sudan'),
        (SUDAN, 'Sudan'),
        (SWAZILAND, 'Swaziland'),
        (TANZANIA, 'Tanzania'),
        (TOGO, 'Togo'),
        (TUNISIA, 'Tunisia'),
        (UGANDA, 'Uganda'),
        (ZAMBIA, 'Zambia'),
        (ZIMBABWE, 'Zimbawe'),
    )
    
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    region = models.CharField(max_length=50)

    def __unicode__(self):
        return self.country


class School(models.Model):
    class Meta:
        permissions = (
            ("view_school", ""),
        )
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=200, default='')

    def __unicode__(self):
        return self.name


class LearningModule(models.Model):
    '''Need to store learning modules.'''
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    '''Need to store learning modules.'''
    class Meta:
        permissions = (
            ("view_course", "only the teacher of course and ICAP should see course"),
        )
    # Should limit the choices
    school = models.ForeignKey(School)
    module = models.ForeignKey(LearningModule)
    # is there any course that may have more than one module
    semester = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    ICAP = 'IC'
    TEACHER = 'TE'
    STUDENT = 'ST'

    PROFILE_CHOICES = (
        (ICAP, 'ICAP'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    )
    user = models.ForeignKey(User, related_name="application_user")
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)
    country = models.ForeignKey(Country)
    course = models.ManyToManyField(Course, null=True, blank=True)
    school = models.ForeignKey(School, null=True, blank=True)

    def __unicode__(self):
        return self.user.username + " " + self.profile_type


class PendingRegister(models.Model):
    #school = models.ForeignKey(School, null=True, blank=True)#models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    userprofile = models.ForeignKey(UserProfile, null=True, blank=True)
    course = models.CharField(max_length=50, null=True, blank=True)
    profile_type = models.CharField(max_length=2, null=True, blank=True)







# class ICAPStaff(models.Model):
#     '''How do we differentiate between ICAP admins
#     (those who add modules/content) and those who
#     simply edit schools etc.'''
#     profile = models.ForeignKey(UserProfile)
#     #region = models.CharField(max_length=200)

#     def __unicode__(self):
#         return self.user.username



# class Teacher(models.Model):
#     '''Assuming each school has many teachers but each
#     teacher works at only one school.'''
#     class Meta:
#         permissions = (
#             ("view_teacher", ""),
#         )
#     school = models.ForeignKey(School)
#     profile = models.ForeignKey(UserProfile)

#     def __unicode__(self):
#         return self.user.name + " " + self.user.school


# class Student(models.Model):
#     class Meta:
#         permissions = (
#             ("view_students", "students should only be visible by their teacher and ICAP staff."),
#         )
#     '''Only designated people of the school may add teachers.'''
#     school = models.ForeignKey(School)
#     course = models.ManyToManyField(Course)
#     profile = models.ForeignKey(UserProfile)

#     def __unicode__(self):
#         return self.user.name + " " + self.user.country




