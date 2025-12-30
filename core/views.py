from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.models import User

from .models import (
    Board, Pin, SavedPin,
    Like, Comment,
    Follow, Profile,
    BoardFollow
)
from .forms import ProfileForm


@login_required
def personal_feed(request):
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list("following", flat=True)

    pins = Pin.objects.filter(
        board__user__in=following_users
    ).order_by("-id")

    return render(request, "core/personal_feed.html", {
        "pins": pins
    })


# ==========================
# HOME / DASHBOARD
# ==========================
@login_required
def home(request):
    boards = Board.objects.filter(user=request.user)
    return render(request, "core/home.html", {"boards": boards})


# ==========================
# BOARD DETAIL + INFINITE SCROLL
# ==========================
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    pins_qs = Pin.objects.filter(board=board).order_by("-id")

    paginator = Paginator(pins_qs, 12)
    page = request.GET.get("page", 1)
    pins_page = paginator.get_page(page)

    # HTMX load
    if request.headers.get("HX-Request"):
        return render(request, "core/pin_items.html", {"pins": pins_page})

    return render(request, "core/board_detail.html", {
        "board": board,
        "pins": pins_page,
        "has_next": pins_page.has_next(),
    })


# ==========================
# CREATE BOARD / PIN
# ==========================
@login_required
def create_board(request):
    if request.method == "POST":
        Board.create(
            name=request.POST["name"],
            user=request.user
        )
        return redirect("home")

    return render(request, "core/create_board.html")


@login_required
def create_pin(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)

    if request.method == "POST":
        Pin.objects.create(
            title=request.POST["title"],
            description=request.POST.get("description", ""),
            image=request.FILES["image"],
            board=board
        )
        return redirect("board_detail", board_id=board.id)

    return render(request, "core/create_pin.html", {"board": board})


# ==========================
# PIN DETAIL (Likes + Comments + Related Pins)
# ==========================
@login_required
def pin_detail(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    # increment views
    pin.views += 1
    pin.save(update_fields=["views"])

    is_owner = (pin.board.user == request.user)

    likes = Like.objects.filter(pin=pin)
    like_count = likes.count()
    liked_users = [like.user.username for like in likes]

    comments = Comment.objects.filter(pin=pin, parent__isnull=True)

    # ⭐ Related Pins
    related_pins = Pin.objects.exclude(id=pin.id)[:12]

    return render(request, "core/pin_detail.html", {
        "pin": pin,
        "is_owner": is_owner,
        "comments": comments,
        "like_count": like_count,
        "liked_users": liked_users,
        "is_liked": likes.filter(user=request.user).exists(),
        "related_pins": related_pins,
    })


# ==========================
# LIKE / UNLIKE PIN
# ==========================
@login_required
def toggle_like(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    like, created = Like.objects.get_or_create(user=request.user, pin=pin)
    if not created:
        like.delete()

    return redirect("pin_detail", pin_id=pin.id)


# ==========================
# COMMENTS + REPLIES
# ==========================
@login_required
def add_comment(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    Comment.objects.create(
        pin=pin,
        user=request.user,
        text=request.POST.get("comment_text"),
        parent_id=request.POST.get("parent_id") or None
    )

    return redirect("pin_detail", pin_id=pin.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user:
        comment.delete()

    return redirect("pin_detail", pin_id=comment.pin.id)


# ==========================
# EDIT & DELETE PIN
# ==========================
@login_required
def edit_pin(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id, board__user=request.user)

    if request.method == "POST":
        pin.title = request.POST["title"]
        pin.description = request.POST["description"]
        pin.save()
        return redirect("pin_detail", pin_id=pin.id)

    return render(request, "core/edit_pin.html", {"pin": pin})


@login_required
def delete_pin(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id, board__user=request.user)
    board_id = pin.board.id
    pin.delete()
    return redirect("board_detail", board_id=board_id)


# ==========================
# SAVE PIN TO BOARD
# ==========================
@login_required
def save_pin(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    if request.method == "POST":
        board_id = request.POST.get("board_id")
        board = get_object_or_404(Board, id=board_id, user=request.user)

        SavedPin.objects.get_or_create(
            user=request.user,
            pin=pin,
            board=board,
        )

        return redirect("profile")

    return redirect("pin_detail", pin_id=pin.id)


# ==========================
# PROFILE + EDIT PROFILE
# ==========================
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    boards = Board.objects.filter(user=request.user)
    pins = Pin.objects.filter(board__user=request.user)
    saved_pins = SavedPin.objects.filter(user=request.user)

    return render(request, "core/profile.html", {
        "profile": profile,
        "boards": boards,
        "pins": pins,
        "saved_pins": saved_pins
    })


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        profile.save()
        return redirect("profile")

    return render(request, "core/edit_profile.html", {"profile": profile})


# ==========================
# PUBLIC PROFILE + FOLLOW USER
# ==========================
def public_profile(request, username):
    user = get_object_or_404(User, username=username)

    boards = Board.objects.filter(user=user)
    pins = Pin.objects.filter(board__user=user)

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

    return render(request, "core/public_profile.html", {
        "profile_user": user,
        "boards": boards,
        "pins": pins,
        "is_following": is_following
    })


@login_required
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    existing = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    )

    if existing.exists():
        existing.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect("public_profile", username=username)


# ==========================
# BOARD FOLLOW / UNFOLLOW
# ==========================
@login_required
def toggle_board_follow(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    follow, created = BoardFollow.objects.get_or_create(
        user=request.user,
        board=board
    )

    if not created:
        follow.delete()

    return redirect("board_detail", board_id=board.id)


@login_required
def board_followers(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    followers = BoardFollow.objects.filter(board=board)

    return render(request, "core/board_followers.html", {
        "board": board,
        "followers": followers
    })


# ==========================
# EXPLORE FEED
# ==========================
def feed(request):
    paginator = Paginator(
        Pin.objects.all().order_by("-created_at"),
        10
    )

    page = request.GET.get("page", 1)
    pins_page = paginator.get_page(page)

    if request.GET.get("page"):
        return render(request, "core/pin_items.html", {"pins": pins_page})

    return render(request, "core/feed.html", {"pins": pins_page})


# ==========================
# SEARCH
# ==========================
@login_required
def search(request):
    query = request.GET.get("q", "")

    boards = Board.objects.filter(
        Q(name__icontains=query),
        user=request.user
    )

    pins = Pin.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        board__user=request.user
    )

    return render(request, "core/search.html", {
        "query": query,
        "boards": boards,
        "pins": pins
    })


@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user)

    return render(request, "core/followers_list.html", {
        "profile_user": user,
        "followers": followers
    })


@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user)

    return render(request, "core/following_list.html", {
        "profile_user": user,
        "following": following
    })
