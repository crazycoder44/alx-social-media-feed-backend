from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Share


class PostModelTest(TestCase):
    """Test cases for the Post model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_post_creation(self):
        """Test creating a post"""
        post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        self.assertEqual(post.content, 'Test post content')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.likes_count, 0)
        self.assertEqual(post.comments_count, 0)
        self.assertEqual(post.shares_count, 0)
        self.assertIsNone(post.image_url)
    
    def test_post_with_image(self):
        """Test creating a post with an image URL"""
        post = Post.objects.create(
            author=self.user,
            content='Post with image',
            image_url='https://example.com/image.jpg'
        )
        self.assertEqual(post.image_url, 'https://example.com/image.jpg')
    
    def test_post_str_method(self):
        """Test the string representation of a post"""
        post = Post.objects.create(
            author=self.user,
            content='A' * 60  # Long content
        )
        self.assertEqual(str(post), f"{self.user.username}: {'A' * 50}")
    
    def test_post_ordering(self):
        """Test that posts are ordered by creation date descending"""
        post1 = Post.objects.create(author=self.user, content='First post')
        post2 = Post.objects.create(author=self.user, content='Second post')
        
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)  # Most recent first
        self.assertEqual(posts[1], post1)


class CommentModelTest(TestCase):
    """Test cases for the Comment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post'
        )
    
    def test_comment_creation(self):
        """Test creating a comment"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.content, 'Test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
    
    def test_comment_str_method(self):
        """Test the string representation of a comment"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(str(comment), f"{self.user.username} on post {self.post.id}")


class LikeModelTest(TestCase):
    """Test cases for the Like model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post'
        )
    
    def test_like_creation(self):
        """Test creating a like"""
        like = Like.objects.create(
            post=self.post,
            user=self.user
        )
        self.assertEqual(like.post, self.post)
        self.assertEqual(like.user, self.user)
    
    def test_like_unique_constraint(self):
        """Test that a user cannot like the same post twice"""
        Like.objects.create(post=self.post, user=self.user)
        
        # Attempting to create a duplicate like should raise an error
        with self.assertRaises(Exception):
            Like.objects.create(post=self.post, user=self.user)
    
    def test_like_str_method(self):
        """Test the string representation of a like"""
        like = Like.objects.create(
            post=self.post,
            user=self.user
        )
        self.assertEqual(str(like), f"{self.user.username} likes post {self.post.id}")


class ShareModelTest(TestCase):
    """Test cases for the Share model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post'
        )
    
    def test_share_creation(self):
        """Test creating a share"""
        share = Share.objects.create(
            post=self.post,
            user=self.user
        )
        self.assertEqual(share.post, self.post)
        self.assertEqual(share.user, self.user)
    
    def test_share_str_method(self):
        """Test the string representation of a share"""
        share = Share.objects.create(
            post=self.post,
            user=self.user
        )
        self.assertEqual(str(share), f"{self.user.username} shared post {self.post.id}")


class InteractionTest(TestCase):
    """Test cases for interactions between models"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post for interactions'
        )
    
    def test_post_with_multiple_comments(self):
        """Test adding multiple comments to a post"""
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='First comment'
        )
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.user2,
            content='Second comment'
        )
        
        self.assertEqual(self.post.comments.count(), 2)
        self.assertIn(comment1, self.post.comments.all())
        self.assertIn(comment2, self.post.comments.all())
    
    def test_post_with_multiple_likes(self):
        """Test adding multiple likes to a post"""
        like1 = Like.objects.create(post=self.post, user=self.user1)
        like2 = Like.objects.create(post=self.post, user=self.user2)
        
        self.assertEqual(self.post.likes.count(), 2)
        self.assertIn(like1, self.post.likes.all())
        self.assertIn(like2, self.post.likes.all())
    
    def test_user_multiple_posts(self):
        """Test user creating multiple posts"""
        post1 = Post.objects.create(author=self.user1, content='Post 1')
        post2 = Post.objects.create(author=self.user1, content='Post 2')
        
        self.assertEqual(self.user1.posts.count(), 3)  # Including setUp post
        self.assertIn(post1, self.user1.posts.all())
        self.assertIn(post2, self.user1.posts.all())
