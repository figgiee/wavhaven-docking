<<<<<<< HEAD
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

class Genre(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Beat(models.Model):
    producer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    audio_file = models.FileField(
        upload_to='beats/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp3', 'wav'])
        ]
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bpm = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)
    tags = models.CharField(max_length=500, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    cover_image = models.ImageField(upload_to='beat_covers/', null=True, blank=True)
    sales_count = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_cover_image_url(self):
        if self.cover_image:
            try:
                return self.cover_image.url
            except:
                pass
        return '/static/store/images/waveform.svg'

    def get_audio_url(self):
        if self.audio_file and self.audio_file.url:
            return self.audio_file.url
        return None

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
    genres = models.ManyToManyField(Genre, related_name='producers', blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    purchased_beats = models.ManyToManyField(Beat, related_name='buyers', blank=True)
    favorite_beats = models.ManyToManyField(Beat, related_name='favorited_by', blank=True)
    
    def __str__(self):
        return self.display_name or self.user.username
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})
    
    def get_avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except:
                pass
        return '/static/store/images/default_avatar.png'
    
    def get_follower_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.user.following.count()
    
    def is_following(self, user):
        return user.userprofile.followers.filter(id=self.user.id).exists()

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
    name = models.CharField(max_length=100)  # e.g., "Basic", "Premium", "Exclusive"
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
=======
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Genre(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Beat(models.Model):
    producer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    audio_file = models.FileField(
        upload_to='beats/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp3', 'wav'])
        ]
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bpm = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)
    tags = models.CharField(max_length=500, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    cover_image = models.ImageField(upload_to='beat_covers/', null=True, blank=True)
    sales_count = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_cover_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return '/static/store/images/default_cover.png'  # We'll create this default image

class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    purchased_beats = models.ManyToManyField(Beat, related_name='buyers')
    
    def __str__(self):
        return self.user.username

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
    name = models.CharField(max_length=100)  # e.g., "Basic", "Premium", "Exclusive"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
class BeatLicense(models.Model):
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE)
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
>>>>>>> 43e6d2dca8d245f001e712240bfadecec0527f1e
