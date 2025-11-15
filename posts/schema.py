import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Share


# GraphQL Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = '__all__'


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = '__all__'


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = '__all__'


class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = '__all__'


# Query Resolvers
class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType, limit=graphene.Int(), offset=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    user_posts = graphene.List(PostType, user_id=graphene.Int(required=True))
    post_comments = graphene.List(CommentType, post_id=graphene.Int(required=True))
    post_likes = graphene.List(LikeType, post_id=graphene.Int(required=True))
    all_users = graphene.List(UserType)
    
    def resolve_all_posts(self, info, limit=10, offset=0):
        """Fetch all posts with pagination and optimized queries"""
        return Post.objects.select_related('author').prefetch_related(
            'comments__author',
            'likes__user',
            'shares__user'
        ).all()[offset:offset+limit]
    
    def resolve_post(self, info, id):
        """Fetch a single post by ID with optimized queries"""
        try:
            return Post.objects.select_related('author').prefetch_related(
                'comments__author',
                'likes__user',
                'shares__user'
            ).get(pk=id)
        except Post.DoesNotExist:
            return None
    
    def resolve_user_posts(self, info, user_id):
        """Fetch all posts by a specific user with optimizations"""
        return Post.objects.filter(author_id=user_id).select_related(
            'author'
        ).prefetch_related('comments__author', 'likes__user')
    
    def resolve_post_comments(self, info, post_id):
        """Fetch all comments for a specific post"""
        return Comment.objects.filter(post_id=post_id).select_related('author', 'post')
    
    def resolve_post_likes(self, info, post_id):
        """Fetch all likes for a specific post"""
        return Like.objects.filter(post_id=post_id).select_related('user', 'post')
    
    def resolve_all_users(self, info):
        """Fetch all users"""
        return User.objects.all()


# Mutation Resolvers
class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        image_url = graphene.String()
    
    post = graphene.Field(PostType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, content, image_url=None):
        user = info.context.user
        if not user.is_authenticated:
            return CreatePost(success=False, message="Authentication required", post=None)
        
        post = Post.objects.create(
            author=user,
            content=content,
            image_url=image_url
        )
        return CreatePost(post=post, success=True, message="Post created successfully")


class UpdatePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
        content = graphene.String()
        image_url = graphene.String()
    
    post = graphene.Field(PostType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, post_id, content=None, image_url=None):
        user = info.context.user
        if not user.is_authenticated:
            return UpdatePost(success=False, message="Authentication required", post=None)
        
        try:
            post = Post.objects.get(pk=post_id)
            if post.author != user:
                return UpdatePost(success=False, message="Not authorized to update this post", post=None)
            
            if content:
                post.content = content
            if image_url is not None:
                post.image_url = image_url
            post.save()
            
            return UpdatePost(post=post, success=True, message="Post updated successfully")
        except Post.DoesNotExist:
            return UpdatePost(success=False, message="Post not found", post=None)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            return DeletePost(success=False, message="Authentication required")
        
        try:
            post = Post.objects.get(pk=post_id)
            if post.author != user:
                return DeletePost(success=False, message="Not authorized to delete this post")
            
            post.delete()
            return DeletePost(success=True, message="Post deleted successfully")
        except Post.DoesNotExist:
            return DeletePost(success=False, message="Post not found")


class CreateComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
        content = graphene.String(required=True)
    
    comment = graphene.Field(CommentType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, post_id, content):
        user = info.context.user
        if not user.is_authenticated:
            return CreateComment(success=False, message="Authentication required", comment=None)
        
        try:
            post = Post.objects.get(pk=post_id)
            comment = Comment.objects.create(
                post=post,
                author=user,
                content=content
            )
            post.comments_count += 1
            post.save()
            return CreateComment(comment=comment, success=True, message="Comment added successfully")
        except Post.DoesNotExist:
            return CreateComment(success=False, message="Post not found", comment=None)


class DeleteComment(graphene.Mutation):
    class Arguments:
        comment_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, comment_id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteComment(success=False, message="Authentication required")
        
        try:
            comment = Comment.objects.get(pk=comment_id)
            if comment.author != user:
                return DeleteComment(success=False, message="Not authorized to delete this comment")
            
            post = comment.post
            comment.delete()
            post.comments_count = max(0, post.comments_count - 1)
            post.save()
            return DeleteComment(success=True, message="Comment deleted successfully")
        except Comment.DoesNotExist:
            return DeleteComment(success=False, message="Comment not found")


class LikePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    like = graphene.Field(LikeType)
    
    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            return LikePost(success=False, message="Authentication required", like=None)
        
        try:
            post = Post.objects.get(pk=post_id)
            like, created = Like.objects.get_or_create(post=post, user=user)
            
            if created:
                post.likes_count += 1
                post.save()
                return LikePost(success=True, message="Post liked successfully", like=like)
            else:
                like.delete()
                post.likes_count = max(0, post.likes_count - 1)
                post.save()
                return LikePost(success=True, message="Post unliked successfully", like=None)
        except Post.DoesNotExist:
            return LikePost(success=False, message="Post not found", like=None)


class SharePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)
    
    share = graphene.Field(ShareType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            return SharePost(success=False, message="Authentication required", share=None)
        
        try:
            post = Post.objects.get(pk=post_id)
            share = Share.objects.create(post=post, user=user)
            post.shares_count += 1
            post.save()
            return SharePost(share=share, success=True, message="Post shared successfully")
        except Post.DoesNotExist:
            return SharePost(success=False, message="Post not found", share=None)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
