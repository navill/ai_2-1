from django.contrib import admin

# Register your models here.
from accounts.models import CommonUser


class CommonUserAdmin(admin.ModelAdmin):
    fields = ['username', 'email', 'birth', 'role', 'is_active']
    list_display = ['username', 'email', 'last_login', 'date_joined']


admin.site.register(CommonUser, CommonUserAdmin)
