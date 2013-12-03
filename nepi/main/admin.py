from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from nepi.main.models import UserProfile, Course, School, LearningModule
from nepi.main.models import Country


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(School)
admin.site.register(LearningModule)
admin.site.register(Country)
