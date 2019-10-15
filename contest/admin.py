from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
	Profile,
	Contest,
	Test,
	Atempt,
	Classification,
	Team,
	TeamMember,
	SafeExecError
	)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Contest)
admin.site.register(Test)
admin.site.register(Atempt)
admin.site.register(Classification)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(SafeExecError)

