from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import (
    Profile,
    Post,
    Comment,
    Follow,
    Like,
)
from social_media.permissions import IsOwnerOrReadOnly

from social_media.serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileSerializer,
    ProfileImageSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentSerializer,
    LikeSerializer,
    CommentListSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer

        if self.action == "retrieve":
            return ProfileDetailSerializer

        if self.action == "upload_image":
            return ProfileImageSerializer

        return ProfileSerializer

    def get_queryset(self):
        username = self.request.query_params.get("username")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        queryset = self.queryset

        if username:
            queryset = queryset.filter(
                username__icontains=username
            )
        if first_name:
            queryset = queryset.filter(
                first_name__icontains=first_name
            )
        if last_name:
            queryset = queryset.filter(
                last_name__icontains=last_name
            )

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow"
    )
    def follow(self, request, pk=None):
        if request.user.profile.pk == int(pk):
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_follow = get_object_or_404(Profile, pk=pk)
        print(user_to_follow)
        if Follow.objects.filter(
                follower=request.user.profile.user,
                followed=user_to_follow.user
        ).exists():
            return Response(
                {"detail": "You are already following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.profile.follow(user_to_follow)
        return Response(
            {"detail": "You are now following this user"}, status=status.HTTP_200_OK
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow"
    )
    def unfollow(self, request, pk=None):
        if request.user.profile.pk == int(pk):
            return Response(
                {"detail": "You cannot unfollow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_unfollow = get_object_or_404(Profile, pk=pk)
        if not Follow.objects.filter(
                follower=request.user.profile.user,
                followed=user_to_unfollow.user
        ).exists():
            return Response(
                {"detail": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.profile.unfollow(user_to_unfollow)
        return Response(
            {"detail": "Unfollowed successfully"}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="all-likes"
    )
    def all_likes(self, request, pk=None):
        profile = self.get_object()
        all_likes = Like.objects.filter(user=profile.user)
        serializer = LikeSerializer(all_likes, many=True)
        if profile == request.user.profile:
            return Response(serializer.data)
        return Response(
            {"detail": "You cannot see posts liked by other user"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user").prefetch_related("likes")
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.all()
        hashtag = self.request.query_params.get("hashtag", None)

        if hashtag:
            queryset = queryset.filter(content__icontains=f"{hashtag}")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "upload_media":
            return PostImageSerializer
        if self.action == "edit_comment":
            return CommentSerializer

        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST"],
        url_path="like"
    )
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        liked = Like.objects.filter(user=request.user, post=post).exists()

        if liked:
            return Response(
                {"detail": "You have already liked this post"},
                status=status.HTTP_200_OK,
            )
        Like.objects.create(user=request.user, post=post)
        return Response({"detail": "You liked this post"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST"],
        url_path="unlike"
    )
    def unlike(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        liked = Like.objects.filter(user=request.user, post=post).exists()
        if not liked:
            return Response(
                {"detail": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Like.objects.filter(user=request.user, post=post).delete()
        return Response(
            {"detail": "You unliked this post"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="add-comment"
    )
    def add_comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=post)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET"],
        url_path="comments"
    )
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = (
            Comment.objects.filter(post=post)
            .select_related("post", "user")
            .prefetch_related("post__user")
        )
        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET"],
        url_path="likes"
    )
    def likes(self, request, pk=None):
        post = self.get_object()
        likes = (
            Like.objects.filter(post=post)
            .select_related("post", "user")
            .prefetch_related("post__user")
        )
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET", "PUT", "DELETE"],
        url_path="comments/(?P<comment_pk>[^/.]+)",
    )
    def edit_comment(self, request, pk=None, comment_pk=None):
        comment = get_object_or_404(Comment, pk=comment_pk, post__id=pk)

        self.check_object_permissions(request, comment)

        if request.method == "GET":
            serializer = CommentSerializer(comment)
            return Response(serializer.data)

        elif request.method == "PUT":
            if request.user.profile != comment.user:
                return Response(
                    {"detail": "You do not have permission to edit this comment."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = CommentSerializer(comment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            if request.user != comment.user:
                return Response(
                    {"detail": "You do not have permission to delete this comment."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
