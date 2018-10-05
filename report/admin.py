from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser,Reports,Project,Subproject,datesofmonth


class CustomUserAdmin(UserAdmin):
    model    = CustomUser
    add_form = CustomUserCreationForm
    form     = CustomUserChangeForm
admin.site.register(CustomUser, CustomUserAdmin)

admin.register(Reports)(admin.ModelAdmin)
admin.register(Project)(admin.ModelAdmin)
admin.register(Subproject)(admin.ModelAdmin)
admin.register(datesofmonth)(admin.ModelAdmin)
