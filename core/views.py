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


@login_required
def home(request):
    boards = Board.objects.filter(user=request.user)
    return render(request, 'core/home.html', {'boards': boards})

@login_required
def board_detail(request, board_id):
    board = Board.objects.get(id=board_id, user=request.user)
    pins = Pin.objects.filter(board=board)
    return render(request, 'core/board_detail.html', {'board': board, 'pins': pins})

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


@login_required
def pin_detail(request, pin_id):
    pin = Pin.objects.get(id=pin_id)
    is_owner = (pin.board.user == request.user)

    # comments already working
    comments = Comment.objects.filter(pin=pin, parent__isnull=True)

    # ⭐ ADD THIS — get people who liked the pin
    likes = Like.objects.filter(pin=pin).select_related("user")

    return render(request, "core/pin_detail.html", {
        "pin": pin,
        "is_owner": is_owner,
        "comments": comments,

        # send like info to template
        "like_count": likes.count(),
        "is_liked": likes.filter(user=request.user).exists(),
        "likes_list": likes,   # 👈 IMPORTANT
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
    boards = Board.objects.filter(user=request.user)
    pins = Pin.objects.filter(board__user=request.user)
    saved_pins = SavedPin.objects.filter(user=request.user)

    return render(request, "core/profile.html", {
        "boards": boards,
        "pins": pins,
        "saved_pins": saved_pins
    })
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
