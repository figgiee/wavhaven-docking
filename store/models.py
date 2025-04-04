from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from taggit.managers import TaggableManager
from django.db.models import Count
from taggit.models import Tag


class Genre(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Beat(models.Model):
    CONTENT_TYPES = [
        ('beat', 'Beat'),
        ('loop', 'Loop'),
        ('soundkit', 'Sound Kit'),
        ('preset', 'Preset'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    producer = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(
        upload_to='beats/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp3', 'wav']
            )
        ]
    )
    cover_image = models.ImageField(
        upload_to='beat_covers/',
        null=True,
        blank=True
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    bpm = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=50, blank=True)
    tags = TaggableManager(blank=True)
    type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='beat')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    play_count = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('beat_detail', kwargs={'pk': self.pk})
    
    def get_cover_image_url(self):
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                pass
        return '/static/store/images/default_cover.png'

    def get_audio_url(self):
        if self.audio_file and self.audio_file.url:
            return self.audio_file.url
        return None

    def get_similar_beats(self, limit=5):
        """Get beats that share tags with this beat.
        
        Args:
            limit: Maximum number of similar beats to return.
            
        Returns:
            QuerySet of Beat objects that share tags with this beat.
        """
        return Beat.objects.filter(
            tags__name__in=self.tags.names()
        ).exclude(
            id=self.id
        ).distinct()[:limit]
    
    def get_tag_list(self):
        """Get a list of tag names.
        
        Returns:
            List of strings representing tag names.
        """
        return list(self.tags.names())
    
    def get_tag_cloud(self):
        """Get tag usage statistics for this beat's tags.
        
        Returns:
            List of dictionaries containing tag name and usage count.
        """
        return Tag.objects.filter(
            name__in=self.tags.names()
        ).annotate(
            count=Count('taggit_taggeditem_items')
        ).values('name', 'count')
    
    @staticmethod
    def get_popular_tags(limit=10):
        """Get the most popular tags across all beats.
        
        Args:
            limit: Maximum number of tags to return.
            
        Returns:
            QuerySet of Tag objects with their usage count.
        """
        return Tag.objects.annotate(
            count=Count('taggit_taggeditem_items')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def search_by_tags(tags, exclude_ids=None):
        """Search for beats by tags.
        
        Args:
            tags: List of tag names to search for.
            exclude_ids: Optional list of beat IDs to exclude.
            
        Returns:
            QuerySet of Beat objects that match the tags.
        """
        queryset = Beat.objects.filter(tags__name__in=tags).distinct()
        if exclude_ids:
            queryset = queryset.exclude(id__in=exclude_ids)
        return queryset


class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    soundcloud_link = models.URLField(blank=True)
    bandcamp_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)
    spotify_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    genres = models.ManyToManyField(
        Genre,
        related_name='producers',
        blank=True
    )
    followers = models.ManyToManyField(
        User,
        related_name='following',
        blank=True
    )
    purchased_beats = models.ManyToManyField(
        Beat,
        related_name='buyers',
        blank=True
    )
    favorite_beats = models.ManyToManyField(
        Beat,
        related_name='favorited_by',
        blank=True
    )
    
    def __str__(self):
        return self.display_name or self.user.username
    
    def get_absolute_url(self):
        return reverse(
            'profile',
            kwargs={'username': self.user.username}
        )
    
    def get_avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        return '/static/store/images/default_avatar.png'
    
    def get_follower_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.user.following.count()
    
    def is_following(self, user):
        return user.userprofile.followers.filter(
            id=self.user.id
        ).exists()


# Signal to create UserProfile automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


class License(models.Model):
    """Model for different types of beat licenses (Basic, Premium, Exclusive)."""
    name = models.CharField(
        max_length=100,
        help_text="License type (e.g. Basic, Premium, Exclusive)"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()


class BeatLicense(models.Model):
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE)
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Comment(models.Model):
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    upvotes = models.ManyToManyField(User, related_name='upvoted_comments', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.beat.title}'

    def get_upvote_count(self):
        return self.upvotes.count()

    def is_upvoted_by(self, user):
        return self.upvotes.filter(id=user.id).exists()

    def is_reply(self):
        return self.parent is not None
