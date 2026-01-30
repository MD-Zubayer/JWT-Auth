from django.contrib import admin
from .models import User
# Register your models here.



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active','is_superuser', 'is_verified')
    search_fields = ('email',)
    ordering = ('id',)