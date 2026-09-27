from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserProfile, Post


# Profile shown inside User admin
class ProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0


# Custom User admin
class CustomUserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


admin.site.register(Post)