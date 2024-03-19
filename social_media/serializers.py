from rest_framework import serializers

from social_media.models import Profile, Follow, Post, Like, Comment

from user.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "post", "text", "created_at")


class CommentListSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(
        source="user.profile.username", read_only=True
    )

    class Meta:
        model = Comment
        fields = ("id", "profile_name", "text", "created_at")


class ProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField()

    class Meta:
        model = Profile
        fields = ("id", "profile_image")


class FollowingSerializer(serializers.ModelSerializer):
    following = serializers.CharField(
        source="followed.profile.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("following",)


class FollowersSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(
        source="follower.profile.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("follower",)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "username", "birth_date", "created_at", "description")


class ProfileListSerializer(serializers.ModelSerializer):
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "username",
            "image",
            "created_at",
            "following_count",
            "followers_count",
        )

    def get_following_count(self, obj):
        return obj.user.following.count()

    def get_followers_count(self, obj):
        return obj.user.followers.count()


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "username",
            "description",
            "image",
            "created_at",
            "birth_date",
            "following",
            "followers",
        )

    def get_following(self, obj):
        following_profiles = obj.user.following.all()
        return FollowingSerializer(following_profiles, many=True).data

    def get_followers(self, obj):
        followers_profiles = obj.user.followers.all()
        return FollowersSerializer(followers_profiles, many=True).data


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "image",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "posted",
        )


class PostListSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    profile_name = serializers.CharField(
        source="user.profile.username", read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "profile_name",
            "content",
            "image",
            "posted",
            "likes_count",
            "comments_count",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(
        source="user.profile.username", read_only=True
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "profile_name",
            "content",
            "image",
            "posted",
            "likes_count",
            "comments_count",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")
