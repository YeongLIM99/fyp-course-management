from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, Interview, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # ensure that the instructor and trainee required to be add in and processed from the form
    # where update would be further control in admin panel

    # user password wont be encrypted and the form cannot be used since POST method involve if not include the form here
    # user details can still be edited in the admin panel but cannot be used to create new user
    form = UserChangeForm
    add_form = UserCreationForm

    # fields are displayed on the change list page of the admin
    list_display = ('username', 'email', 'password', 'contact', 'address', 'age', 'weight',
                    'height', 'gender', 'medical', 'education', 'date_joined', 'resume',
                    'is_active', 'is_superuser', 'is_instructor', 'is_trainee', 'is_staff', 'is_failed',
                    'last_login', 'to_arrange', 'is_arranged', 'backup_email',
                    'is_created_email', 'is_sent_interview')
    # filters in the right sidebar of the change list page of the admin
    list_filter = ('is_active', 'is_superuser', 'is_instructor', 'is_trainee', 'is_staff', 'is_failed',
                   'to_arrange', 'is_arranged', 'is_created_email', 'is_sent_interview')

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password', 'date_joined')
        }),
        ('Personal info', {
            'fields': ('backup_email', 'contact', 'address', 'age', 'weight',
                       'height', 'gender', 'medical', 'education', 'resume')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser', 'is_instructor', 'is_trainee', 'is_staff')
        }),
        ('Status', {
            'fields': ('last_login', 'to_arrange', 'is_arranged', 'is_failed', 'is_created_email', 'is_sent_interview')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal info', {
            'fields': ('contact', 'address', 'age', 'weight',
                       'height', 'gender', 'medical', 'education', 'resume')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser', 'is_instructor', 'is_trainee', 'is_staff', 'is_failed')
        }),
        ('Status', {
            'fields': ('last_login', 'to_arrange', 'is_arranged', 'is_failed', 'is_created_email', 'is_sent_interview')
        })
    )

    search_fields = ('username', 'email')      # search box on the admin change list page
    ordering = ('username', 'email')
    filter_horizontal = ()


admin.site.register(Interview)
admin.site.register(Profile)
