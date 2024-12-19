from django.contrib import admin
from .models import Post, Image, Comment

class PostAdmin(admin.ModelAdmin):
    fields = ('author', 'title', 'text', 'created_date', 'published_date', 'image') 
    list_display = ('id', 'author', 'title', 'created_date', 'published_date') 

admin.site.register(Post, PostAdmin)
