from django.contrib import admin
from general.models import User
from django.contrib.auth.models import Group


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'email',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    fields = (
        'first_name',
        'last_name',
        'username',
        'password',
        'email',
        'is_superuser',
        'is_active',
        'date_joined',
        'last_login',
    )
    readonly_fields = (
        'date_joined',
        'last_login',
    )
    search_fields = (
        'id',
        'username',
        'email',
    )
    list_filter = (
        'is_superuser',
        'is_active',
    )



admin.site.unregister(Group)
# admin.site.unregister(User)
