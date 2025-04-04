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
from taggit.models import Tag
from django.urls import reverse
from .services.payment import PaymentService

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
    tag = request.GET.get('tag', '')
    beats = Beat.objects.all().order_by('-created_at')
    
    if query:
        beats = beats.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__name__in=[query])
        ).distinct()
    
    if tag:
        beats = beats.filter(tags__name__in=[tag]).distinct()
    
    # Get popular tags for the sidebar
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    return render(request, 'store/beats/beat_list.html', {
        'beats': beats,
        'popular_tags': popular_tags
    })

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
    
    # Get tags with counts for the main beat
    beat_tags = list(beat.tags.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times'))
    
    # Get similar beats based on tags, with their tags preloaded
    similar_beats = Beat.objects.filter(
        tags__name__in=beat.tags.names()
    ).exclude(
        id=beat.id
    ).prefetch_related('tags').distinct()[:5]
    
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
        'similar_beats': similar_beats,
        'beat_tags': beat_tags,  # Annotated tags with counts
    }
    
    return render(request, 'store/beats/beat_detail.html', context)

def genres(request):
    genres = Genre.objects.all()
    return render(request, 'store/genres.html', {'genres': genres})

@login_required
def beat_upload(request):
    genres = Genre.objects.all()
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    if request.method == 'POST':
        title = request.POST.get('title')
        audio_file = request.FILES.get('audio_file')
        price = request.POST.get('price')
        bpm = request.POST.get('bpm')
        key = request.POST.get('key')
        tags = request.POST.get('tags', '').split(',')
        genre_id = request.POST.get('genre')
        content_type = request.POST.get('content_type', 'beat')
        
        # Create form_data to preserve input on error
        form_data = {
            'title': title,
            'price': price,
            'bpm': bpm,
            'key': key,
            'tags': request.POST.get('tags', ''),
            'genre': genre_id,
            'genre_name': Genre.objects.filter(id=genre_id).values_list('name', flat=True).first() if genre_id else '',
            'content_type': content_type,
            'selected_type': content_type  # For the content type selector
        }
        
        if title and audio_file and price:
            try:
                # Convert price to Decimal and validate
                try:
                    price = Decimal(price)
                    if price < 0:
                        raise ValueError("Price cannot be negative")
                except (InvalidOperation, ValueError) as e:
                    messages.error(request, f"Invalid price format: {str(e)}")
                    return render(request, 'store/beats/beat_upload.html', {
                        'genres': genres,
                        'popular_tags': popular_tags,
                        'form_data': form_data
                    })

                # Validate genre_id
                if not genre_id or not genre_id.isdigit():
                    messages.error(request, "Please select a valid genre")
                    return render(request, 'store/beats/beat_upload.html', {
                        'genres': genres,
                        'popular_tags': popular_tags,
                        'form_data': form_data
                    })

                beat = Beat(
                    title=title,
                    audio_file=audio_file,
                    price=price,
                    producer=request.user,
                    bpm=int(bpm) if bpm else None,
                    key=key,
                    genre_id=genre_id,
                    type=content_type,
                    status='active'
                )
                if 'cover_image' in request.FILES:
                    beat.cover_image = request.FILES['cover_image']
                beat.save()
                
                # Add tags after saving
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        beat.tags.add(tag)
                
                messages.success(request, f'{content_type.title()} uploaded successfully!')
                return redirect('store:beat_detail', pk=beat.pk)
            except Exception as e:
                messages.error(request, f'Error uploading {content_type}: {str(e)}')
                return render(request, 'store/beats/beat_upload.html', {
                    'genres': genres,
                    'popular_tags': popular_tags,
                    'form_data': form_data
                })
        else:
            messages.error(request, 'Please provide title, audio file, and price.')
            return render(request, 'store/beats/beat_upload.html', {
                'genres': genres,
                'popular_tags': popular_tags,
                'form_data': form_data
            })
    
    return render(request, 'store/beats/beat_upload.html', {
        'genres': genres,
        'popular_tags': popular_tags,
        'form_data': {'selected_type': 'beat'}  # Default content type
    })

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
        return redirect('store:dashboard')
        
    return render(request, 'store/profile/edit_profile.html')

@login_required
def delete_beat(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('store:dashboard')
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
            return redirect('store:dashboard')
    else:
        form = BeatForm(instance=beat)
    
    return render(request, 'store/beats/beat_edit.html', {'form': form, 'beat': beat})

@login_required
def beat_delete(request, pk):
    beat = get_object_or_404(Beat, pk=pk, producer=request.user)
    
    if request.method == 'POST':
        beat.delete()
        messages.success(request, 'Beat deleted successfully!')
        return redirect('store:dashboard')
    
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
        'cover_image': beat.get_cover_image_url() if hasattr(beat, 'get_cover_image_url') else None,
        'price': str(beat.price) if beat.price else '0.00',
        'genre': beat.genre.name if beat.genre else None,
        'bpm': beat.bpm if hasattr(beat, 'bpm') else None,
        'key': beat.key if hasattr(beat, 'key') else None,
        'tags': [tag.name for tag in beat.tags.all()] if beat.tags.exists() else [],
        'type': beat.type if hasattr(beat, 'type') else 'beat',
        'created_at': beat.created_at.isoformat() if beat.created_at else None,
        'url': reverse('store:beat_detail', kwargs={'pk': beat.id}),
        'audio_file': beat.audio_file.url if beat.audio_file else None,
        'producer': beat.producer.username
    } for beat in beats]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'uploaded_beats': json.dumps(beats_data),
        'beats_count': beats.count(),
        'is_following': request.user.is_authenticated and profile.followers.filter(id=request.user.id).exists(),
        'follower_count': profile.get_follower_count(),
        'following_count': profile.get_following_count(),
        'genres': Genre.objects.all().order_by('name'),
        'total_beats': beats.count(),
        'total_loops': loops.count(),
        'total_soundkits': soundkits.count(),
        'total_presets': presets.count(),
    }
    return render(request, 'store/profile/profile.html', context)

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
            return redirect('store:profile', username=request.user.username)
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
    selected_tags = request.GET.getlist('tags')
    
    beats = Beat.objects.all()
    
    # Apply search query
    if query:
        beats = beats.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__name__in=[query])
        ).distinct()
    
    # Apply tag filter
    if selected_tags:
        beats = beats.filter(tags__name__in=selected_tags).distinct()
    
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
    
    # Get popular tags for filtering
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:15]
    
    context = {
        'beats': beats,
        'query': query,
        'sort': sort,
        'selected_genres': selected_genres,
        'selected_tags': selected_tags,
        'min_price': min_price,
        'max_price': max_price,
        'min_bpm': min_bpm,
        'max_bpm': max_bpm,
        'genres': Genre.objects.all().order_by('name'),
        'popular_tags': popular_tags
    }
    
    return render(request, 'store/search.html', context)

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    
    context = {
        'cart_items': cart.cartitem_set.all() if cart else [],
        'cart_total': sum(float(item.beat.price) for item in cart.cartitem_set.all()) if cart else 0
    }
    return render(request, 'store/checkout.html', context)

@login_required
@require_http_methods(["DELETE", "POST"])
def remove_from_cart(request, item_id):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return JsonResponse({
            'status': 'error',
            'message': 'Cart not found'
        }, status=404)

    try:
        cart_item = CartItem.objects.select_related('beat').get(id=item_id, cart=cart)
        beat_title = cart_item.beat.title
        beat_data = {
            'id': cart_item.beat.id,
            'title': beat_title
        }
        cart_item.delete()
        
        # Recalculate cart totals
        cart_count = cart.cartitem_set.count()
        cart_total = sum(float(item.beat.price) for item in cart.cartitem_set.all())
        
        if request.headers.get('HX-Request') or request.method == 'POST':
            return JsonResponse({
                'status': 'success',
                'message': f'{beat_title} removed from cart',
                'cart_count': cart_count,
                'cart_total': cart_total,
                'action': {
                    'label': 'Undo',
                    'beatId': beat_data['id']
                }
            })
        
        messages.success(request, f'{beat_title} removed from cart')
        return redirect('store:cart_view')
        
    except CartItem.DoesNotExist:
        if request.headers.get('HX-Request') or request.method == 'POST':
            return JsonResponse({
                'status': 'error',
                'message': 'Item not found in cart'
            }, status=404)
        
        messages.error(request, 'Item not found in cart')
        return redirect('store:cart_view')

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    context = {
        'cart_items': cart.cartitem_set.all() if cart else [],
        'cart_total': sum(float(item.beat.price) for item in cart.cartitem_set.all()) if cart else 0
    }
    return render(request, 'store/cart.html', context)

def explore_content(request):
    """
    Unified view for exploring and searching content (beats, loops, soundkits, presets).
    """
    content_type = request.GET.get('type', 'all')
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'relevance')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_bpm = request.GET.get('min_bpm')
    max_bpm = request.GET.get('max_bpm')
    
    # Base queryset
    content = Beat.objects.filter(status='active')
    
    # Apply content type filter if not 'all'
    if content_type != 'all' and content_type in dict(Beat.CONTENT_TYPES):
        content = content.filter(type=content_type)
    
    # Apply search query if present
    if query:
        content = content.filter(
            Q(title__icontains=query) |
            Q(producer__username__icontains=query) |
            Q(genre__name__icontains=query) |
            Q(tags__name__in=[query])
        ).distinct()
    
    # Apply price range filter
    if min_price:
        content = content.filter(price__gte=float(min_price))
    if max_price:
        content = content.filter(price__lte=float(max_price))
    
    # Apply BPM range filter
    if min_bpm:
        content = content.filter(bpm__gte=int(min_bpm))
    if max_bpm:
        content = content.filter(bpm__lte=int(max_bpm))
    
    # Apply sorting
    if sort == 'newest':
        content = content.order_by('-created_at')
    elif sort == 'price_low':
        content = content.order_by('price')
    elif sort == 'price_high':
        content = content.order_by('-price')
    elif sort == 'popular':
        content = content.order_by('-play_count')
    else:  # relevance or default
        content = content.order_by('-created_at')
    
    # Get popular tags for the specific content type or all content
    tag_filter = {'beat__type': content_type} if content_type != 'all' else {}
    popular_tags = Tag.objects.filter(**tag_filter).annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    # Prepare context
    context = {
        'content': content,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'min_bpm': min_bpm,
        'max_bpm': max_bpm,
        'popular_tags': popular_tags,
        'content_type': content_type,
        'page_title': 'Explore All Sounds' if content_type == 'all' else f'Explore {content_type.title()}s',
        'page_description': 'Discover the latest and greatest sounds from our community' if content_type == 'all' else f'Discover the latest and greatest {content_type}s from our community',
        'genres': Genre.objects.all().order_by('name')
    }
    
    return render(request, 'store/explore/content.html', context)

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

@login_required
def process_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        payment_method = data.get('payment_method')
        
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({
                'status': 'error',
                'message': 'Cart not found'
            }, status=404)
            
        cart_items = cart.cartitem_set.all()
        cart_total = sum(float(item.beat.price) for item in cart_items)
        
        if payment_method == 'stripe':
            # Setup Stripe session
            payment_data = PaymentService.setup_stripe_session(
                request, cart_items, cart_total
            )
            return JsonResponse({
                'status': 'success',
                'payment_type': 'stripe',
                'session_id': payment_data['session_id'],
                'public_key': payment_data['public_key']
            })
            
        elif payment_method == 'paypal':
            # Setup PayPal payment
            payment_data = PaymentService.setup_paypal_payment(
                request, cart_items, cart_total
            )
            return JsonResponse({
                'status': 'success',
                'payment_type': 'paypal',
                'approval_url': payment_data['approval_url'],
                'payment_id': payment_data['payment_id']
            })
            
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payment method'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def payment_success(request):
    # Handle successful payment
    return render(request, 'store/payment_success.html')

@login_required
def payment_cancel(request):
    # Handle cancelled payment
    return render(request, 'store/payment_cancel.html')

@login_required
def payment_error(request):
    # Handle payment error
    return render(request, 'store/payment_error.html')

def about(request):
    """Render the about page."""
    return render(request, 'store/about.html')

def producer_faq(request):
    """Render the producer FAQ page."""
    return render(request, 'store/producer_faq.html')

def submission_guidelines(request):
    """View for submission guidelines page."""
    return render(request, 'store/submission_guidelines.html')

def customer_faq(request):
    """View for customer FAQ page."""
    return render(request, 'store/customer_faq.html')

def licensing_info(request):
    """View for licensing information page."""
    return render(request, 'store/licensing_info.html')

def contact_support(request):
    """View for contact support page."""
    return render(request, 'store/contact_support.html')

def returns_policy(request):
    """View for returns and refunds policy page."""
    return render(request, 'store/returns_policy.html')

def terms_of_service(request):
    """View for terms of service page."""
    return render(request, 'store/terms_of_service.html')

def privacy_policy(request):
    """View for privacy policy page."""
    return render(request, 'store/privacy_policy.html')

def cookie_policy(request):
    """View for cookie policy page."""
    return render(request, 'store/cookie_policy.html')

