from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """
    Model representing a social media post.
    
    Attributes:
        author (User): The user who created the post
        content (str): The text content of the post
        image_url (str): Optional URL to an image
        created_at (datetime): Timestamp when post was created
        updated_at (datetime): Timestamp when post was last updated
        likes_count (int): Cached count of likes
        comments_count (int): Cached count of comments
        shares_count (int): Cached count of shares
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class Comment(models.Model):
    """
    Model representing a comment on a post.
    
    Attributes:
        post (Post): The post this comment belongs to
        author (User): The user who wrote the comment
        content (str): The text content of the comment
        created_at (datetime): Timestamp when comment was created
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username} on post {self.post.id}"


class Like(models.Model):
    """
    Model representing a like on a post.
    
    Attributes:
        post (Post): The post that was liked
        user (User): The user who liked the post
        created_at (datetime): Timestamp when like was created
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'user']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class Share(models.Model):
    """
    Model representing a share of a post.
    
    Attributes:
        post (Post): The post that was shared
        user (User): The user who shared the post
        created_at (datetime): Timestamp when share was created
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} shared post {self.post.id}"
