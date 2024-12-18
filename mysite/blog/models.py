from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='blog_image/%Y/%m/%d/', null=True, blank=True , default='path/to/default/image.jpg')
    song_urls = models.TextField(blank=True, null=True) 

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class Image(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_image/%Y/%m/%d/', null=True, blank=True , default='path/to/default/image.png')

    def __str__(self):
        return f"Image for {self.post.title}"
    
"""기타 정의되지 않은 편의 기능"""
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)  # 게시물에 대한 외래키
    author = models.CharField(max_length=100, default="Anonymous")
    text = models.TextField()  # 댓글 내용
    created_date = models.DateTimeField(default=timezone.now)  # 댓글 작성일

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

