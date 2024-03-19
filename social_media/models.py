import os
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "following"]


def profile_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.displayed_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/user_images/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        unique=True, related_name="profile"
    )
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True)
    description = models.TextField(max_length=255)
    image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def follow(self, profile_to_follow):
        if profile_to_follow != self.user:
            Follow.objects.get_or_create(follower=self.user, followed=profile_to_follow)

    def unfollow(self, profile_to_unfollow):
        Follow.objects.filter(follower=self.user, followed=profile_to_unfollow).delete()

    def __str__(self):
        return self.username


def post_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.displayed_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post_images/", filename)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=post_image_path, null=True, blank=True)
    hashtag = models.TextField(max_length=55)

    def __str__(self):
        return f"Post crated at {self.posted} by {self.author}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return (f"Created at {self.created_at} by {self.author.profile.username} "
                f"on post {self.post}")


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "post"]

    def __str__(self):
        return f"{self.user.profile.username} liked {self.post}"
