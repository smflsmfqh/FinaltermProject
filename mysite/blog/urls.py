from django.urls import path, include
from rest_framework import routers
from .views import PostView, post_list, BlogImages, post_detail, post_new, post_edit, js_test, upload_image, PostViewSet
from . import views
from django.contrib import admin
from .admin import PostAdmin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register('Post', PostViewSet)

urlpatterns = [
    path('photo_blog/', views.photo_blog, name='photo_blog'),
    path('', post_list, name='post_list'),
    path('post/<int:pk>/', post_detail, name='post_detail'),  # 게시물 상세보기 URL
    path('post/new/', post_new, name='post_new'),  # 새 게시물 작성 URL
    path('post/<int:pk>/edit/', post_edit, name='post_edit'),  # 게시물 수정 URL
    path('js_test/', js_test, name='js_test'),  # 자바스크립트 테스트 URL
    path('api_root/', include(router.urls)),
    path('upload-image/', upload_image, name='upload_image'),  # 이미지 업로드 URL
    path('post/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('detect_emotion_and_recommend/', views.detect_emotion_and_recommend, name='detect_emotion_and_recommend'),
    path('admin/blog/post/<int:object_id>/change/', admin.site.admin_view(PostAdmin.change_view), name='blog_post_change'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('start-emotion-recognition/', views.startEmotionRecognition, name='start_emotion_recognition'),
    
]
