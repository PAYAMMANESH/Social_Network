from django.contrib import admin
from .models import Relation, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(Relation)


class PofileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class ExtendedUserAdmin(UserAdmin):
    inlines = [PofileInline]


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
