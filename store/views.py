from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from decimal import Decimal, InvalidOperation

def genres_processor(request):
    return {
        'genres': Genre.objects.all().order_by('name')
    }

def cart_processor(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_items = cart.cartitem_set.all()
            cart_total = sum(float(item.beat.price) for item in cart_items)
            return {
                'cart_total': cart_total,
                'cart_items_count': cart_items.count()
            }
    return {
        'cart_total': 0,
        'cart_items_count': 0
    }

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

def beat_detail(request, pk):
    beat = get_object_or_404(Beat, pk=pk)
    comments = (
        beat.comments.filter(parent=None)
        .select_related('user', 'user__userprofile')
        .prefetch_related(
            'upvotes',
            'replies',
            'replies__user',
            'replies__user__userprofile',
            'replies__upvotes'
        )
    )
    
    # Prepare upvote data for the template
    comment_upvotes = {}
    if request.user.is_authenticated:
        for comment in comments:
            comment_upvotes[comment.id] = comment.is_upvoted_by(request.user)
            for reply in comment.replies.all():
                comment_upvotes[reply.id] = reply.is_upvoted_by(request.user)
    
    context = {
        'beat': beat,
        'comments': comments,
        'comment_upvotes': comment_upvotes,
    }
    return render(request, 'store/beats/beat_detail.html', context)

def genres(request):
    genres = Genre.objects.all()
    return render(request, 'store/genres.html', {'genres': genres})

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
            try:
                # Convert price to Decimal and validate
                try:
                    price = Decimal(price)
                    if price < 0:
                        raise ValueError("Price cannot be negative")
                except (InvalidOperation, ValueError) as e:
                    messages.error(request, f"Invalid price format: {str(e)}")
                    genres = Genre.objects.all()
                    return render(request, 'store/beats/beat_upload.html', {'genres': genres})

                beat = Beat(
                    title=title,
                    audio_file=audio_file,
                    price=price,
                    producer=request.user,
                    bpm=int(bpm) if bpm else None,
                    key=key,
                    tags=tags,
                    genre_id=genre_id,
                    status='active'
                )
                if 'cover_image' in request.FILES:
                    beat.cover_image = request.FILES['cover_image']
                beat.save()
                messages.success(request, 'Beat uploaded successfully!')
                return redirect('store:beat_detail', pk=beat.pk)
            except Exception as e:
                messages.error(request, f'Error uploading beat: {str(e)}')
                genres = Genre.objects.all()
                return render(request, 'store/beats/beat_upload.html', {'genres': genres})
        else:
            messages.error(request, 'Please provide title, audio file, and price.')
    
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
            messages.success(
                request,
                f'Genre "{genre_name}" created successfully!'
            )
        return redirect('manage_genres')
        
    genres = Genre.objects.all().order_by('name')
    return render(request, 'store/manage_genres.html', {'genres': genres})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('store:landing_page')
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
@require_http_methods(["POST"])
def favorite_beat(request, beat_id):
    try:
        beat = get_object_or_404(Beat, id=beat_id)
        user_profile = request.user.userprofile
        
        if user_profile.favorite_beats.filter(id=beat_id).exists():
            user_profile.favorite_beats.remove(beat)
            is_favorite = False
            message = "Beat removed from favorites"
        else:
            user_profile.favorite_beats.add(beat)
            is_favorite = True
            message = "Beat added to favorites"
            
        return JsonResponse({
            'status': 'success',
            'message': message,
            'is_favorite': is_favorite
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def check_favorite(request, beat_id):
    try:
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
    data = json.loads(request.body)
    beat_id = data.get('beat_id')
    
    if not beat_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Beat ID is required'
        })
        
    try:
        beat = Beat.objects.get(pk=beat_id)
        cart = Cart.objects.filter(user=request.user).first()
        
        # Create cart if it doesn't exist
        if not cart:
            cart = Cart.objects.create(user=request.user)
            
        # Check if item is already in cart
        if CartItem.objects.filter(cart=cart, beat=beat).exists():
            return JsonResponse({
                'status': 'error',
                'reason': 'already_in_cart',
                'message': 'This item is already in your cart'
            })
            
        # Add item to cart
        CartItem.objects.create(cart=cart, beat=beat)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Added to cart',
            'cart_count': cart.cartitem_set.count()
        })
        
    except Beat.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Beat not found'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

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
    
    # Get all content types
    beats = Beat.objects.filter(producer=user).order_by('-created_at')
    loops = Beat.objects.filter(producer=user, type='loop').order_by('-created_at')
    soundkits = Beat.objects.filter(producer=user, type='soundkit').order_by('-created_at')
    presets = Beat.objects.filter(producer=user, type='preset').order_by('-created_at')
    
    # Convert querysets to lists of dictionaries for JSON serialization
    beats_data = [{
        'id': beat.id,
        'title': beat.title,
        'cover_image': beat.get_cover_image_url(),
        'price': str(beat.price),
        'genre': beat.genre.name if beat.genre else 'Uncategorized',
        'bpm': beat.bpm,
        'key': beat.key,
        'tags': beat.tags,
        'type': beat.type,
        'created_at': beat.created_at.isoformat()
    } for beat in beats]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'uploaded_beats': beats_data,
        'is_following': request.user.is_authenticated and profile.followers.filter(id=request.user.id).exists(),
        'follower_count': profile.get_follower_count(),
        'following_count': profile.get_following_count(),
        'genres': Genre.objects.all().order_by('name'),
        'total_beats': beats.count(),
        'total_loops': loops.count(),
        'total_soundkits': soundkits.count(),
        'total_presets': presets.count(),
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
@require_http_methods(["POST"])
def add_comment(request, beat_id):
    try:
        beat = get_object_or_404(Beat, id=beat_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Comment content is required'
            }, status=400)
            
        comment = Comment.objects.create(
            beat=beat,
            user=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comment added successfully',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': comment.user.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'upvote_count': 0
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Only allow the comment author to delete it
    if comment.user != request.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('store:beat_detail', pk=comment.beat.id)
    
    comment.delete()
    messages.success(request, 'Comment deleted successfully.')
    return redirect('store:beat_detail', pk=comment.beat.id)

@login_required
@require_http_methods(["POST"])
def upvote_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.upvotes.filter(id=request.user.id).exists():
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
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

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

def producer_list(request):
    producers = User.objects.filter(beat__isnull=False).distinct()
    return render(request, 'store/producers.html', {'producers': producers})

def search(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'relevance')
    selected_genres = request.GET.getlist('genre')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_bpm = request.GET.get('min_bpm')
    max_bpm = request.GET.get('max_bpm')
    
    beats = Beat.objects.all()
    
    # Apply search query
    if query:
        beats = beats.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()
    
    # Apply genre filter
    if selected_genres:
        beats = beats.filter(genre__id__in=selected_genres)
    
    # Apply price range filter
    if min_price:
        beats = beats.filter(price__gte=float(min_price))
    if max_price:
        beats = beats.filter(price__lte=float(max_price))
    
    # Apply BPM range filter
    if min_bpm:
        beats = beats.filter(bpm__gte=int(min_bpm))
    if max_bpm:
        beats = beats.filter(bpm__lte=int(max_bpm))
    
    # Apply sorting
    if sort == 'newest':
        beats = beats.order_by('-created_at')
    elif sort == 'price_low':
        beats = beats.order_by('price')
    elif sort == 'price_high':
        beats = beats.order_by('-price')
    elif sort == 'popular':
        beats = beats.order_by('-play_count')
    # For 'relevance', we keep the default ordering from the search query
    
    context = {
        'beats': beats,
        'query': query,
        'sort': sort,
        'selected_genres': selected_genres,
        'min_price': min_price,
        'max_price': max_price,
        'min_bpm': min_bpm,
        'max_bpm': max_bpm,
        'genres': Genre.objects.all().order_by('name')
    }
    
    return render(request, 'store/search.html', context)

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.cartitem_set.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('beat_list')
        
    context = {
        'cart_items': cart.cartitem_set.all(),
        'cart_total': sum(float(item.beat.price) for item in cart.cartitem_set.all())
    }
    return render(request, 'store/checkout.html', context)

@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
        
        cart_count = cart.cartitem_set.count()
        cart_total = float(sum(item.beat.price for item in cart.cartitem_set.all()))
        
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'status': 'success',
                'cart_count': cart_count,
                'cart_total': cart_total
            })
        
        # Dispatch cart update event
        response = redirect(request.META.get('HTTP_REFERER', 'store:beat_list'))
        response['HX-Trigger'] = json.dumps({
            'cart-updated': {
                'count': cart_count
            }
        })
        return response
        
    except Exception as e:
        messages.error(request, 'Error removing item from cart')
        return redirect('store:beat_list')

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    context = {
        'cart_items': cart.cartitem_set.all() if cart else [],
        'cart_total': sum(float(item.beat.price) for item in cart.cartitem_set.all()) if cart else 0
    }
    return render(request, 'store/cart.html', context)

def explore_beats(request):
    beats = Beat.objects.all().order_by('-created_at')
    return render(request, 'store/explore/beats.html', {
        'beats': beats,
        'page_title': 'Explore Beats',
        'page_description': 'Discover the latest and greatest beats from our community'
    })

def explore_loops(request):
    return render(request, 'store/explore/loops.html', {
        'page_title': 'Explore Loops',
        'page_description': 'Find the perfect loops for your next track'
    })

def explore_soundkits(request):
    return render(request, 'store/explore/soundkits.html', {
        'page_title': 'Explore Soundkits',
        'page_description': 'Premium sound kits from top producers'
    })

def explore_presets(request):
    return render(request, 'store/explore/presets.html', {
        'page_title': 'Explore Presets',
        'page_description': 'Professional presets for your favorite synths and plugins'
    })

def trending(request):
    # Get featured beats (top 3 beats marked as featured)
    featured_beats = Beat.objects.filter(is_featured=True).order_by('-created_at')[:3]
    
    # Get trending beats based on play count, excluding featured beats
    trending_beats = Beat.objects.exclude(
        id__in=featured_beats.values_list('id', flat=True)
    ).order_by('-play_count', '-created_at')
    
    # Pagination for trending beats
    page = request.GET.get('page', 1)
    paginator = Paginator(trending_beats, 12)  # Show 12 beats per page
    
    try:
        trending_beats = paginator.page(page)
    except PageNotAnInteger:
        trending_beats = paginator.page(1)
    except EmptyPage:
        trending_beats = paginator.page(paginator.num_pages)
    
    context = {
        'featured_beats': featured_beats,
        'trending_beats': trending_beats,
        'page_title': 'Trending',
        'page_description': 'What\'s hot right now on WAVhaven'
    }
    
    return render(request, 'store/explore/trending.html', context)

def genre_view(request, genre_name):
    genre = get_object_or_404(Genre, name__iexact=genre_name)
    beats = Beat.objects.filter(genre=genre).order_by('-created_at')
    return render(request, 'store/genres/genre.html', {
        'genre': genre,
        'beats': beats,
        'page_title': f'{genre.name} Beats',
        'page_description': f'The best {genre.name} beats from our community'
    })

def landing_page(request):
    # Get random featured beats that have audio files
    featured_beats = Beat.objects.filter(
        audio_file__isnull=False
    ).order_by('?')[:6]  # Random selection of 6 beats
    
    # Get producers who have uploaded beats, ordered by number of beats
    featured_producers = User.objects.annotate(
        beats_count=models.Count('beat'),
        followers_count=models.Count('userprofile__followers'),
        sales_count=models.Sum('beat__sales_count')
    ).filter(
        beats_count__gt=0
    ).order_by('-beats_count')[:6]

    context = {
        'featured_beats': featured_beats,
        'featured_producers': featured_producers,
    }
    
    return render(request, 'store/landing_page.html', context)

@login_required
def favorites_view(request):
    user_profile = request.user.userprofile
    # Get only valid favorites where the beat still exists and has a valid primary key
    favorites = user_profile.favorite_beats.select_related(
        'producer',
        'genre'
    ).filter(
        pk__isnull=False
    ).order_by('-id')
    
    # Clean up any invalid favorites
    user_profile.favorite_beats.remove(
        *user_profile.favorite_beats.filter(pk__isnull=True)
    )
    
    genres = Genre.objects.all().order_by('name')
    
    context = {
        'favorites': favorites,
        'genres': genres,
    }
    
    return render(request, 'store/favorites.html', context)

