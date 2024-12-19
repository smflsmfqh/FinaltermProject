from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Image, Comment
from .serializers import PostSerializer, ImageSerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.conf import settings
from .forms import PostForm  # PostForm 임포트
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import uuid
from django.core.files.storage import FileSystemStorage
import sys
import os
import time
import cv2
import subprocess
import base64
import numpy as np


sys.path.append('/Users/ihaneul/projects/ForPythonanywhere/yolov5')

from changedetection import detect_person_from_webcam

@api_view(['POST'])
def startEmotionRecognition(request):
    """
    감정 인식 시작을 위한 함수입니다.
    - 이미지가 첨부된 경우: 이미지를 업로드하여 감정 분석을 수행합니다.
    - 이미지가 없는 경우: 웹캠을 통해 감정을 인식합니다.
    """
    # 이미지가 첨부된 경우
    image = request.FILES.get('image')
    if image:
        return handle_image_emotion_recognition(request, image)
    
    # 이미지가 첨부되지 않은 경우 (웹캠 사용)
    return handle_webcam_emotion_recognition()
    """if request.method == 'POST':
        
        image = request.FILES.get('image')  # 이미지 파일이 요청에 포함되었는지 확인
        
    
        if image:
            try:    # 이미지 업로드 처리
                fs = FileSystemStorage()
                saved_file_path = fs.save(image.name, image)  # 서버에 이미지 저장
                full_file_path = fs.path(saved_file_path)  # 저장된 이미지의 전체 경로
                print(f"Image saved at: {full_file_path}") 

                # 저장된 파일을 다시 읽어서 OpenCV로 디코딩
                with open(full_file_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_array = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                print(f"Image received and converted to frame. Size: {frame.shape}")

                # 디버깅: frame이 None인지 확인
                if frame is None:
                    print("Error: Image frame is None.")
                    return JsonResponse({'status': 'error', 'message': 'Failed to decode image.'}, status=400)

                # detect_person_from_webcam에 프레임 전달
                response = detect_person_from_webcam(frame=frame)  
                return response
            
            except Exception as e:
                print(f"Error processing image: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

                if response.status_code == 200:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Emotion recognition started successfully with image!',
                        'response': response.content.decode('utf-8')  # 응답 내용
                    }, status=200)
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error occurred: {response.text.decode("utf-8")}'  # 요청 오류 메시지
                    }, status=400)

        else:
            #print("No image provided, using webcam.")
            # 여기서 웹캠 처리를 진행
            #response = detect_person_from_webcam(request=request, frame=None)  # 웹캠에서 촬영 처리
            #return response  # 카메라 촬영에 대한 응답 반환
             curl_command = [
                    'curl', '-X', 'POST', 'http://127.0.0.1:8000/detect_emotion_and_recommend/',  # 요청을 보낼 URL
                    '-H', 'Content-Type: application/json',  # 요청 헤더
                    '-d', '{}'  # 요청 데이터
                ]

            # curl 명령어 실행
        result = subprocess.run(curl_command, capture_output=True, text=True)
            if result.returncode == 0:
                 # 성공적인 실행
                return JsonResponse({
                    'status': 'success',
                    'message': 'Emotion recognition started successfully!',
                    'response': result.stdout  # curl의 응답 내용

                }, status=200)
            else:
                # 오류 발생 시
                return JsonResponse({
                        'status': 'error',
                        'message': f'Error occurred: {result.stderr}'  # curl 에러 출력
                }, status=400)
  
"""
def handle_image_emotion_recognition(request, image):
    """
    이미지 감정 인식 처리 함수
    """
    try:
        # 이미지 저장
        fs = FileSystemStorage()
        saved_file_path = fs.save(image.name, image)
        full_file_path = fs.path(saved_file_path)

        print(f"Image saved at: {full_file_path}") 

        # OpenCV를 사용하여 이미지 파일을 읽고 처리
        with open(full_file_path, 'rb') as img_file:
            img_data = img_file.read()
            img_array = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        print(f"Image received and converted to frame. Size: {frame.shape}")

        if frame is None:
            return JsonResponse({'status': 'error', 'message': 'Failed to decode image.'}, status=400)

        # 이미지 프레임을 처리하여 감정 분석
        response = detect_person_from_webcam(frame=frame)  
        return response

    except Exception as e:
        print(f"Error processing image: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
def handle_webcam_emotion_recognition():
    
    """
    웹캠을 통해 감정 인식 처리 함수 (curl 사용)
    """
    print("No image provided, using webcam.")

    # 웹캠에서 실시간으로 감정 인식 수행
    response = detect_person_from_webcam(frame=None)
    return response

    """# curl 명령어로 웹캠 감정 인식 요청
    curl_command = [
        'curl', '-X', 'POST', 'http://127.0.0.1:8000/detect_emotion_and_recommend/',  # 요청을 보낼 URL
        '-H', 'Content-Type: application/json',  # 요청 헤더
        '-d', '{}'  # 요청 데이터 (빈 JSON)
    ]

    result = subprocess.run(curl_command, capture_output=True, text=True)

    if result.returncode == 0:
        return JsonResponse({
            'status': 'success',
            'message': 'Emotion recognition started successfully!',
            'response': result.stdout  # curl의 응답 내용
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error',
            'message': f'Error occurred: {result.stderr}'  # curl 에러 출력
        }, status=400)"""

def post_list(request):
    posts = Post.objects.all()
    for post in posts:
        print(post.id)
    return render(request, 'blog/post_list.html', {'posts': posts})

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        author = request.data.get('author')
        title = request.data.get('title')
        text = request.data.get('text')
        created_date = request.data.get('created_date')
        published_date = request.data.get('published_date')
        song_urls = request.data.get('song_urls')  # 추가된 부분
        #image = request.FILES.get('image')

        post = Post(
            author=author,
            title=title,
            text=text,
            created_date=created_date,
            published_date=published_date,
            song_urls=song_urls
            #image=image
        )

        post.save()

        images = request.FILES.getlist('images')  # 'images' 키로 여러 파일을 가져옵니다.
        print(f'Uploaded images: {images}')
        if images:
            for image in images:
                Image.objects.create(post=post, image=image)  # 각 이미지를 새로운 Image 모델로 저장

        return Response({"message": "Post created successfully"}, status=status.HTTP_201_CREATED)

class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# 추가된 뷰
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def js_test(request):
    return render(request, 'blog/js_test.html')


def photo_blog(request):
    posts = Post.objects.all().order_by('-created_date')  # 최신순으로 정렬
    return render(request, 'blog/photo_blog.html', {'posts': posts})

@api_view(['POST'])
def upload_image(request):
    image_file = request.FILES.get('image')  # 요청에서 이미지 파일을 가져옴
    if image_file:
        unique_filename = f"{uuid.uuid4()}.jpg"
        fs = FileSystemStorage()
        filename = fs.save(unique_filename, image_file)
        image_url = fs.url(filename)
        #image = Image.objects.create(image=image_file)  # 이미지 모델 인스턴스를 생성하고 저장
        # serializer = ImageSerializer(image)  # 직렬화
        return JsonResponse({'success': True, 'url': image_url})
    else:
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)

def analyze_emotion_from_image(image):
    """이미지를 사용하여 감정을 분석하는 함수"""
    # 이미지를 OpenCV 형식으로 변환
    img_array = np.frombuffer(image.read(), np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # 감정 분석을 위해 detect_person_from_webcam 호출
    return detect_person_from_webcam(frame=frame)  # 이미지 프레임 전달


@api_view(['POST'])
def detect_emotion_and_recommend(request):
    """
    사용자가 감정을 인식하고 노래를 추천하는 API 엔드포인트
    """
    try:
        if 'image' in request.FILES:
            # 이미지 파일이 포함된 경우
            image_file = request.FILES['image']
            emotion_result = analyze_emotion_from_image(image_file)

            return JsonResponse({
                'status': 'success',
                'message': 'Emotion detected successfully from uploaded image.',
                'data': emotion_result  # 감정 분석 결과 반환
            }, status=200)
        else:

            # 감정 인식 및 노래 추천
            emotion_result = detect_person_from_webcam(request=request, frame=None)  # 이 함수는 실시간으로 웹캠을 처리하므로, 여기서 HTTP 요청으로 대체된 실행이 일어남

            # 응답 반환 (성공적인 처리가 완료되었음을 알림)
            return JsonResponse({
                'status': 'success',
                'message': 'Emotion detected and song recommendations sent successfully.',
                'data': emotion_result
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@api_view(['POST'])
def comment_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.data.get('text')
    if text:
        comment = Comment.objects.create(post=post, text=text, author=request.user)
        return Response({
            'author': comment.author.username,
            'text': comment.text,
            'created_date': comment.created_date.isoformat(),
            'id': comment.id
        }, status=status.HTTP_201_CREATED)
    return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)

    """
def comment_list(request, post_id):
    post = Post.objects.get(id=post_id)
    print(f"Received post_id: {post_id}")  # post_id 값 출력
    print(f"Request data: {request.data}")  # 요청 데이터 확인

    # GET 요청: 해당 게시물에 대한 모든 댓글을 반환
    if request.method == 'GET':
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    # POST 요청: 새로운 댓글을 생성
    if request.method == 'POST':
        text = request.data.get('text')
        if not text:
           return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'text': text,
            'post': post.id,
            'author': request.user.id if request.user.is_authenticated else None
        }
        """
    
"""
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # 로그인한 사용자가 author로 저장
            return Response({
                'author': serializer.instance.author.username,
                'text': serializer.instance.text
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        """

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer