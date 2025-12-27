from django.db import models


from django.contrib.auth.models import User


class Board(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Pin(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='pins', null=True,blank=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='pins/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Pin(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='pins/')
    description = models.TextField(blank=True, null=True)   # ← add this
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

from django.contrib.auth.models import User

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.follower} → {self.following}"

class SavedPin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} saved {self.pin.title} to {self.board.name}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pin')  # user can like only once

    def __str__(self):
        return f"{self.user.username} liked {self.pin.title}"

class Comment(models.Model):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    # 👇 NEW FIELD for threaded replies
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_parent(self):
        return self.parent is None

    def __str__(self):
        return f"{self.user.username} — {self.text[:20]}"
