from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from pagetree.models import Hierarchy
from django.contrib.auth.models import User

from nepi.main.models import UserProfile, Course, School, Country


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


# taken from tobacco
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'role']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Hierarchy)

# end of taken form tobacco

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(School)
admin.site.register(Country)
