from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StakeHolder,BackupCodes
from .forms import CustomUserCreationForm,CustomUserChangeForm

# Register your models here.

class StakeHolderAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = StakeHolder
    list_display = ('email','secret','is_staff','is_active')
    list_filter = ('email','secret','is_staff','is_active')

    fieldsets = (
        (None, {
            "fields": (
                'email','password','secret','email_verified','username','origin'
            ),
        }),('Permissions',{
            'fields':('is_staff','is_active')
        })
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    search_fields = ('email',)
    readonly_fields = ('secret',)
    ordering = ('email',)    
    
admin.site.register(StakeHolder,StakeHolderAdmin)
admin.site.register(BackupCodes)