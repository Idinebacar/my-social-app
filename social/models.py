from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Post Model

class Post(models.Model):

    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)

    content = models.CharField(max_length=200)

    post_image = models.ImageField(upload_to="posts/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def like_count(self):
        return self.liked_by.count()

    def __str__(self):
        return (
            f"{self.user.username} "
            f"({self.created_at:%Y-%m-%d %H:%M}): "
            f"{self.content}"
        )


# User Profile Model
class UserProfile(models.Model):

    user = models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)

    following = models.ManyToManyField("self", related_name="followers", symmetrical=False, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True, blank=True)

    bio = models.CharField(max_length=500, null=True, blank=True)

    website_url = models.URLField(max_length=200, null=True, blank=True)

    facebook_url = models.URLField(max_length=200, null=True, blank=True)

    instagram_url = models.URLField(max_length=200, null=True, blank=True)

    linkedin_url = models.URLField( max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username


# Automatically Create Profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
