<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Beat, Genre, User, UserProfile, Cart, CartItem, Comment
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import RegisterForm, BeatForm, UserForm, UserProfileForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def genres_processor(request):
    return {
        'genres': Genre.objects.all().order_by('name')
    }

# No decorator here - should be accessible to everyone
def beat_list(request):
    query = request.GET.get('q', '')
    beats = Beat.objects.all().order_by('-created_at')
    
    if query:
        beats = beats.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()
    
    return render(request, 'store/beats/beat_list.html', {'beats': beats})

# No decorator here - should be accessible to everyone
def beat_detail(request, pk):
    beat = get_object_or_404(Beat, pk=pk)
    comments = beat.comments.filter(parent=None).select_related('user', 'user__userprofile').prefetch_related('upvotes')
    context = {
        'beat': beat,
        'comments': comments,
    }
    return render(request, 'store/beats/beat_detail.html', context)

def genres(request):
    genres = Genre.objects.all()
    return render(request, 'store/genres.html', {'genres': genres})

# Only this view requires login
@login_required
def beat_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        audio_file = request.FILES.get('audio_file')
        price = request.POST.get('price')
        bpm = request.POST.get('bpm')
        key = request.POST.get('key')
        tags = request.POST.get('tags')
        genre_id = request.POST.get('genre')
        
        if title and audio_file and price:
            beat = Beat(
                title=title,
                audio_file=audio_file,
                price=price,
                producer=request.user,
                bpm=bpm,
                key=key,
                tags=tags,
                genre_id=genre_id
            )
            if 'cover_image' in request.FILES:
                beat.cover_image = request.FILES['cover_image']
            beat.save()
            messages.success(request, 'Beat uploaded successfully!')
            return redirect('beat_detail', pk=beat.pk)
        
    genres = Genre.objects.all()
    return render(request, 'store/beats/beat_upload.html', {'genres': genres})

@login_required
def manage_genres(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage genres.')
        return redirect('beat_list')
        
    if request.method == 'POST':
        genre_name = request.POST.get('genre_name')
        if genre_name:
            Genre.objects.create(name=genre_name)
            messages.success(request, f'Genre "{genre_name}" created successfully!')
        return redirect('manage_genres')
        
    genres = Genre.objects.all().order_by('name')
    return render(request, 'store/manage_genres.html', {'genres': genres})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('beat_list')
    else:
        form = RegisterForm()
    return render(request, 'store/auth/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    beats = Beat.objects.filter(producer=user)
    
    context = {
        'beats': beats,
        'beats_count': beats.count(),
        'total_sales': 0,  # Placeholder until sales system is implemented
        'total_plays': 0,  # Placeholder until play tracking is implemented
        'recent_activities': []  # Placeholder for activity tracking
    }
    
    return render(request, 'store/profile/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Update profile
        profile = request.user.userprofile
        profile.bio = request.POST.get('bio', '')
        profile.website = request.POST.get('website', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        
        # Update user
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')
        
    return render(request, 'store/profile/edit_profile.html')

@login_required
def delete_beat(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('dashboard')
    return render(request, 'store/beats/delete_beat_confirm.html', {'beat': beat})

def logout_view(request):
    logout(request)
    return redirect('beat_list')

@login_required
def beat_edit(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    
    if request.method == 'POST':
        form = BeatForm(request.POST, request.FILES, instance=beat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beat updated successfully!')
            return redirect('dashboard')
    else:
        form = BeatForm(instance=beat)
    
    return render(request, 'store/beats/beat_edit.html', {'form': form, 'beat': beat})

@login_required
def beat_delete(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'store/beats/beat_delete.html', {'beat': beat})

@login_required
@require_http_methods(["POST", "DELETE"])
def favorite_beat(request, beat_id):
    try:
        beat = get_object_or_404(Beat, id=beat_id)
        user_profile = request.user.userprofile
        
        if request.method == "POST":
            user_profile.favorite_beats.add(beat)
            message = "Beat added to favorites"
        else:  # DELETE
            user_profile.favorite_beats.remove(beat)
            message = "Beat removed from favorites"
            
        return JsonResponse({
            'status': 'success',
            'message': message,
            'is_favorite': request.method == "POST"
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def check_favorite(request, beat_id):
    try:
        beat = get_object_or_404(Beat, id=beat_id)
        is_favorite = request.user.userprofile.favorite_beats.filter(id=beat_id).exists()
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        beat_id = data.get('beat_id')
        beat = get_object_or_404(Beat, id=beat_id)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        if not CartItem.objects.filter(cart=cart, beat=beat).exists():
            CartItem.objects.create(cart=cart, beat=beat)
            message = "Beat added to cart"
        else:
            message = "Beat is already in cart"
            
        return JsonResponse({
            'status': 'success',
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def check_cart(request, beat_id):
    try:
        beat = get_object_or_404(Beat, id=beat_id)
        cart = Cart.objects.filter(user=request.user).first()
        in_cart = cart and CartItem.objects.filter(cart=cart, beat=beat).exists()
        return JsonResponse({
            'status': 'success',
            'in_cart': in_cart
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.userprofile
    uploaded_beats = Beat.objects.filter(producer=user).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'profile': profile,
        'uploaded_beats': uploaded_beats,
        'is_following': request.user.is_authenticated and profile.followers.filter(id=request.user.id).exists(),
        'follower_count': profile.get_follower_count(),
        'following_count': profile.get_following_count(),
    }
    return render(request, 'store/profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.userprofile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'store/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
@require_http_methods(["POST"])
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'You cannot follow yourself'
        }, status=400)
    
    user_to_follow.userprofile.followers.add(request.user)
    return JsonResponse({
        'status': 'success',
        'follower_count': user_to_follow.userprofile.get_follower_count()
    })

@login_required
@require_http_methods(["POST"])
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    user_to_unfollow.userprofile.followers.remove(request.user)
    return JsonResponse({
        'status': 'success',
        'follower_count': user_to_unfollow.userprofile.get_follower_count()
    })

@login_required
def add_comment(request, beat_id):
    if request.method == 'POST':
        beat = get_object_or_404(Beat, id=beat_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = Comment.objects.create(
                beat=beat,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'username': comment.user.username,
                        'user_id': comment.user.id,
                        'avatar_url': comment.user.userprofile.get_avatar_url(),
                        'created_at': 'Just now',
                        'upvote_count': 0,
                        'is_reply': comment.is_reply()
                    }
                })
                
        return redirect('beat_detail', pk=beat_id)
    return redirect('beat_detail', pk=beat_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Only allow comment owner to delete
    if request.user == comment.user:
        beat_id = comment.beat.id
        comment.delete()
        return redirect('beat_detail', pk=beat_id)
    
    return redirect('beat_detail', pk=comment.beat.id)

@login_required
@require_http_methods(["POST"])
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.is_upvoted_by(request.user):
        comment.upvotes.remove(request.user)
        action = 'removed'
    else:
        comment.upvotes.add(request.user)
        action = 'added'
        
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvote_count': comment.get_upvote_count()
    })

@login_required
def get_comment_replies(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    replies = comment.replies.all()
    
    reply_data = [{
        'id': reply.id,
        'content': reply.content,
        'username': reply.user.username,
        'created_at': reply.created_at.strftime('%B %d, %Y %I:%M %p'),
        'avatar_url': reply.user.userprofile.get_avatar_url(),
        'upvote_count': reply.get_upvote_count(),
        'is_upvoted': reply.is_upvoted_by(request.user)
    } for reply in replies]
    
    return JsonResponse({
        'status': 'success',
        'replies': reply_data
    })



=======
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Beat, Genre, User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import RegisterForm, BeatForm

# No decorator here - should be accessible to everyone
def beat_list(request):
    query = request.GET.get('q', '')
    beats = Beat.objects.all().order_by('-created_at')
    
    if query:
        beats = beats.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()
    
    return render(request, 'store/beat_list.html', {'beats': beats})

# No decorator here - should be accessible to everyone
def beat_detail(request, pk):
    beat = get_object_or_404(Beat, pk=pk)
    return render(request, 'store/beat_detail.html', {'beat': beat})

def genres(request):
    genres = Genre.objects.all()
    return render(request, 'store/genres.html', {'genres': genres})

# Only this view requires login
@login_required
def beat_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        audio_file = request.FILES.get('audio_file')
        price = request.POST.get('price')
        bpm = request.POST.get('bpm')
        key = request.POST.get('key')
        tags = request.POST.get('tags')
        genre_id = request.POST.get('genre')
        
        if title and audio_file and price:
            beat = Beat(
                title=title,
                audio_file=audio_file,
                price=price,
                producer=request.user,
                bpm=bpm,
                key=key,
                tags=tags,
                genre_id=genre_id
            )
            if 'cover_image' in request.FILES:
                beat.cover_image = request.FILES['cover_image']
            beat.save()
            messages.success(request, 'Beat uploaded successfully!')
            return redirect('beat_detail', pk=beat.pk)
        
    genres = Genre.objects.all()
    return render(request, 'store/beat_upload.html', {'genres': genres})

@login_required
def manage_genres(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage genres.')
        return redirect('beat_list')
        
    if request.method == 'POST':
        genre_name = request.POST.get('genre_name')
        if genre_name:
            Genre.objects.create(name=genre_name)
            messages.success(request, f'Genre "{genre_name}" created successfully!')
        return redirect('manage_genres')
        
    genres = Genre.objects.all().order_by('name')
    return render(request, 'store/manage_genres.html', {'genres': genres})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('beat_list')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    beats = Beat.objects.filter(producer=user)
    
    context = {
        'beats': beats,
        'beats_count': beats.count(),
        'total_sales': 0,  # Placeholder until sales system is implemented
        'total_plays': 0,  # Placeholder until play tracking is implemented
        'recent_activities': []  # Placeholder for activity tracking
    }
    
    return render(request, 'store/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Update profile
        profile = request.user.userprofile
        profile.bio = request.POST.get('bio', '')
        profile.website = request.POST.get('website', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        
        # Update user
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')
        
    return render(request, 'store/edit_profile.html')

@login_required
def delete_beat(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('dashboard')
    return render(request, 'store/delete_beat_confirm.html', {'beat': beat})

def logout_view(request):
    logout(request)
    return redirect('beat_list')

@login_required
def beat_edit(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    
    if request.method == 'POST':
        form = BeatForm(request.POST, request.FILES, instance=beat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beat updated successfully!')
            return redirect('dashboard')
    else:
        form = BeatForm(instance=beat)
    
    return render(request, 'store/beat_edit.html', {'form': form, 'beat': beat})

@login_required
def beat_delete(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'store/beat_delete.html', {'beat': beat})



>>>>>>> 43e6d2dca8d245f001e712240bfadecec0527f1e
