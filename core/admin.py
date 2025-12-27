from django.contrib import admin
from .models import Board, Pin
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

admin.site.register(Board, BoardAdmin)
admin.site.register(Pin)
# admin.site.register(Board)
# admin.site.register(Pin)
