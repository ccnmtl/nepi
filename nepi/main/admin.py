from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from pagetree.models import Hierarchy, UserPageVisit

from nepi.main.models import UserProfile, \
    Group, School, Country, PendingTeachers


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'role']


class SchoolGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'creator', 'archived']


class PendingTeacherAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'school']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Hierarchy)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Group, SchoolGroupAdmin)
admin.site.register(School)
admin.site.register(Country)
admin.site.register(PendingTeachers, PendingTeacherAdmin)


class UserPageVisitAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'section', 'status']

admin.site.register(UserPageVisit, UserPageVisitAdmin)
