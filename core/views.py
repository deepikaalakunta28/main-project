from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Board, Pin,SavedPin
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .models import Follow
from .models import SavedPin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Like
from .models import Comment
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from . import views
from django.db.models import Q

@login_required
def home(request):
    boards = Board.objects.filter(user=request.user)
    return render(request, 'core/home.html', {'boards': boards})

@login_required
def board_detail(request, board_id):
    board = Board.objects.get(id=board_id)
    pins = Pin.objects.filter(board=board)

    # check if user follows this board
    is_following_board = BoardFollow.objects.filter(
        board=board,
        user=request.user,
    ).exists()

    return render(request, "core/board_detail.html", {
        "board": board,
        "pins": pins,
        "is_following_board": is_following_board
    })


@login_required
def create_board(request):
    if request.method == "POST":
        name = request.POST['name']
        Board.objects.create(name=name, user=request.user)
        return redirect('home')

    return render(request, 'core/create_board.html')
@login_required
def create_pin(request, board_id):
    board = Board.objects.get(id=board_id, user=request.user)

    if request.method == "POST":
        title = request.POST['title']
        image = request.FILES['image']

        Pin.objects.create(
            title=title,
            image=image,
            board=board
        )

        return redirect('board_detail', board_id=board.id)

    return render(request, 'core/create_pin.html', {'board': board})


from .models import Pin, Like, Comment

@login_required
def pin_detail(request, pin_id):
    pin = Pin.objects.get(id=pin_id)

    is_owner = (pin.board.user == request.user)

    # LIKE DATA
    likes = Like.objects.filter(pin=pin)
    like_count = likes.count()
    liked_users = [like.user.username for like in likes]

    # COMMENTS
    comments = Comment.objects.filter(pin=pin, parent__isnull=True)

    return render(request, "core/pin_detail.html", {
        "pin": pin,
        "is_owner": is_owner,
        "comments": comments,
        "like_count": like_count,
        "liked_users": liked_users,
        "is_liked": likes.filter(user=request.user).exists(),
    })



@login_required
def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)

    if comment.user == request.user:
        comment.delete()

    return redirect('pin_detail', pin_id=comment.pin.id)


@login_required
def create_pin(request, board_id):
    board = Board.objects.get(id=board_id, user=request.user)

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST.get("description", "")
        image = request.FILES["image"]

        Pin.objects.create(
            title=title,
            description=description,
            image=image,
            board=board
        )

        return redirect("board_detail", board_id=board.id)

    return render(request, "core/create_pin.html", {"board": board})
@login_required
def edit_pin(request, pin_id):
    pin = Pin.objects.get(id=pin_id, board__user=request.user)

    if request.method == "POST":
        pin.title = request.POST["title"]
        pin.description = request.POST["description"]
        pin.save()
        return redirect("pin_detail", pin_id=pin.id)

    return render(request, "core/edit_pin.html", {"pin": pin})


@login_required
def delete_pin(request, pin_id):
    pin = Pin.objects.get(id=pin_id, board__user=request.user)
    board_id = pin.board.id
    pin.delete()
    return redirect("board_detail", board_id=board_id)
# @login_required
# def profile(request):
#     boards = Board.objects.filter(user=request.user)
#     pins = Pin.objects.filter(board__user=request.user)

#     return render(request, 'core/profile.html', {
#         'boards': boards,
#         'pins': pins
#     })

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    boards = Board.objects.filter(user=request.user)
    pins = Pin.objects.filter(board__user=request.user)
    saved_pins = SavedPin.objects.filter(user=request.user)

    return render(request, "core/profile.html", {
        "profile": profile,
        "boards": boards,
        "pins": pins,
        "saved_pins": saved_pins
    })

# def profile(request):
#     boards = Board.objects.filter(user=request.user)
#     pins = Pin.objects.filter(board__user=request.user)
#     saved_pins = SavedPin.objects.filter(user=request.user)

#     return render(request, "core/profile.html", {
#         "boards": boards,
#         "pins": pins,
#         "saved_pins": saved_pins
#     })
def public_profile(request, username):
    user = User.objects.get(username=username)
    boards = Board.objects.filter(user=user)
    pins = Pin.objects.filter(board__user=user)

    # check follow status
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

    return render(request, 'core/public_profile.html', {
        'profile_user': user,
        'boards': boards,
        'pins': pins,
        'is_following': is_following
    })
# def public_profile(request, username):
#     user = User.objects.get(username=username)
#     boards = Board.objects.filter(user=user)
#     pins = Pin.objects.filter(board__user=user)

#     return render(request, 'core/public_profile.html', {
#         'profile_user': user,
#         'boards': boards,
#         'pins': pins
#     })
@login_required
def feed(request):
    pins = Pin.objects.all().order_by('-id')   # latest first
    return render(request, 'core/feed.html', {'pins': pins})



@login_required
def toggle_follow(request, username):
    user_to_follow = User.objects.get(username=username)
    existing = Follow.objects.filter(follower=request.user, following=user_to_follow)

    if existing.exists():
        existing.delete()
    else:
        Follow.objects.create(follower=request.user, following=user_to_follow)

    return redirect('public_profile', username=username)


@login_required
def personal_feed(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    pins = Pin.objects.filter(board__user__in=following_users).order_by('-id')
    return render(request, 'core/personal_feed.html', {'pins': pins})


@login_required
def save_pin(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    if request.method == "POST":
        board_id = request.POST.get("board_id")

        board = get_object_or_404(Board, id=board_id, user=request.user)

        SavedPin.objects.create(
            user=request.user,
            pin=pin,
            board=board
        )

        return redirect("profile")

    return redirect("pin_detail", pin_id=pin.id)

@login_required
def toggle_like(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        pin=pin
    )

    if not created:
        like.delete()  # unlike

    return redirect('pin_detail', pin_id=pin.id)


@login_required
def add_comment(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    text = request.POST.get("comment_text")
    parent_id = request.POST.get("parent_id")

    if text:
        Comment.objects.create(
            pin=pin,
            user=request.user,
            text=text,
            parent_id=parent_id if parent_id else None
        )

    return redirect('pin_detail', pin_id=pin.id)




@login_required
def search(request):
    query = request.GET.get("q", "")

    boards = Board.objects.filter(
        Q(name__icontains=query),
        user=request.user
    )

    pins = Pin.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query),
        board__user=request.user
    )

    return render(request, "core/search.html", {
        "query": query,
        "boards": boards,
        "pins": pins,
    })

from .forms import ProfileForm
from .models import Profile
from django.contrib.auth.decorators import login_required
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        profile.save()
        return redirect("profile")

    return render(request, "core/edit_profile.html", {"profile": profile})





from django.contrib.auth.models import User
from .models import Follow

@login_required
def followers_list(request, username):
    user = User.objects.get(username=username)
    followers = Follow.objects.filter(following=user)

    return render(request, "core/followers_list.html", {
        "profile_user": user,
        "followers": followers
    })


@login_required
def following_list(request, username):
    user = User.objects.get(username=username)
    following = Follow.objects.filter(follower=user)

    return render(request, "core/following_list.html", {
        "profile_user": user,
        "following": following
    })


from .models import BoardFollow

@login_required
def toggle_board_follow(request, board_id):
    board = Board.objects.get(id=board_id)

    follow, created = BoardFollow.objects.get_or_create(
        user=request.user,
        board=board
    )

    if not created:   # already following → unfollow
        follow.delete()

    return redirect('board_detail', board_id=board.id)


from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

@login_required
def board_followers(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    followers = BoardFollow.objects.filter(board=board)

    return render(request, "core/board_followers.html", {
        "board": board,
        "followers": followers
    })


from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string

def load_more_pins(request):
    page = int(request.GET.get("page", 1))
    mode = request.GET.get("mode", "explore")   # home / board / explore
    board_id = request.GET.get("board_id", None)

    if mode == "board" and board_id:
        pins = Pin.objects.filter(board_id=board_id).order_by("-created_at")
    elif mode == "home":
        pins = Pin.objects.filter(board__user=request.user).order_by("-created_at")
    else:
        pins = Pin.objects.all().order_by("-created_at")

    paginator = Paginator(pins, 12)   # 12 pins per load
    page_obj = paginator.get_page(page)

    html = render_to_string("core/pin_items.html", {"pins": page_obj}, request=request)

    return JsonResponse({
        "has_next": page_obj.has_next(),
        "html": html
    })
