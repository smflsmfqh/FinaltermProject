import os
import cv2
import pathlib
import requests
import base64
from datetime import datetime
import torch
import numpy as np
import pandas as pd
from google.cloud import vision
from google.cloud.vision import ImageAnnotatorClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.http import JsonResponse


import time

YOUTUBE_API_KEY = 'AIzaSyAIn9x0zxIcvPuMvTk_hwkZaHlQbTnBbNE'

# Google Vision API에 이미지를 base64로 인코딩하는 함수
def encode_image(face_image):
    face_image = cv2.resize(face_image, (400, 400))
    _, encoded_image = cv2.imencode('.jpg', face_image)
    return base64.b64encode(encoded_image).decode('utf-8')

def analyze_emotion_from_webcam(face_image):
    """Google Cloud Vision API를 사용하여 감정을 분석"""
    # Vision API 클라이언트 설정
    client = ImageAnnotatorClient()

    # 이미지를 base64로 인코딩
    image_data = encode_image(face_image)
    vision_image = vision.Image(content=image_data)

    response = client.face_detection(image=vision_image)
    faces = response.face_annotations

    if not faces:
        return "No face detected"

    # 감정 분석: 얼굴에서 감정을 분석하고 가장 강한 감정을 반환
    emotions = []
    for face in faces:
        joy = face.joy_likelihood
        sorrow = face.sorrow_likelihood
        anger = face.anger_likelihood
        surprise = face.surprise_likelihood
        emotions.append((joy, sorrow, anger, surprise))

    # 가장 강한 감정 선택
    max_emotion = max(emotions, key=lambda x: (x[0], x[1], x[2], x[3]))

    if max_emotion[0] > 3:
        return 'Happy'
    elif max_emotion[1] > 3:
        return 'Sad'
    elif max_emotion[2] > 3:
        return 'Anger'
    elif max_emotion[3] > 3:
        return 'Surprise'
    else:
        return 'Neutral'

# youtube playlist
def youtube_search(query):
    """YouTube API를 사용하여 감정에 맞는 노래 추천"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    retries = 3  # 최대 재시도 횟수
    for attempt in range(retries):
        try:
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=1  # 최대 1개의 결과를 반환
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                videos.append({'title': video_title, 'url': video_url})
            
            return videos
        
        except HttpError as err:
            print(f"Attempt {attempt + 1} failed: {err}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프 (2, 4, 8 초 대기)
            else:
                return []
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
    

# Change Detection 클래스
class ChangeDetection:
    HOST = 'http://127.0.0.1:8000'
    username = 'haneullee'
    password = 'jk970901'
    token = ''
    title = ''
    text = ''
    song_urls = []

    def __init__(self, names):
        # 이전 결과를 저장하는 리스트 초기화
        self.result_prev = [0 for _ in range(len(names))]
        
        # 토큰을 요청하여 저장
        res = requests.post(
            f"{self.HOST}/api/token/",
            data={'username': self.username, 'password': self.password}
        )
        if res.status_code == 200:  # 로그인 성공
            self.token = res.json().get('access')
            if self.token is None:
                print("Token is None. Check the response: ", res.json())
        else:  # 로그인 실패
            print(f"Failed to obtain token. Status code: {res.status_code}, Response: {res.text}")
            raise ValueError("Failed to obtain JWT token")
        print("Token obtained: ", self.token)

    def add(self, names, detected_current, save_dir, image, current_emotion, previous_emotion, song_urls=None):
        self.title = ''
        self.text = ''
        change_flag = 0  # 변화 감지 플래그

        if previous_emotion is None:  # 첫 번째 감정 인식 시
            change_flag = 1
            self.title = "First Emotion Detected"
            self.text = f"Emotion detected: {current_emotion}"

        elif previous_emotion != current_emotion:  # 감정 변화 감지
            change_flag = 1
            self.title = "Emotion Changed"
            self.text = f"Emotion changed from {previous_emotion} to {current_emotion}"

        # 노래 추천 URL을 텍스트에 포함
        if song_urls:
            self.song_urls = song_urls
        
        if change_flag == 1:
            self.send(save_dir, image)

    def send(self, save_dir, image):
        # 현재 시각 정보 가져오기
        now = datetime.now()
        today = datetime.now()

        # 이미지 저장 경로 생성
        save_path = pathlib.Path(os.getcwd()) / save_dir / 'detected' / str(today.year) / str(today.month) / str(today.day)
        save_path.mkdir(parents=True, exist_ok=True)

        # 이미지 파일명 설정
        full_path = save_path / '{0}-{1}-{2}-{3}.jpg'.format(today.hour, today.minute, today.second, today.microsecond)

        # 이미지 리사이즈 및 저장
        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(full_path), dst)

        # 인증 헤더 생성
        headers = {
            'Authorization': 'JWT ' + self.token,
            'Accept': 'application/json'
        }

        song_urls_str = ', '.join([song['url'] for song in self.song_urls]) if self.song_urls else ""

        # POST 요청에 보낼 데이터 구성
        data = {
            'author': 1,
            'title': self.title,
            'text': self.text,
            'created_date': now.isoformat(),
            'published_date': now.isoformat(),
            'song_urls': song_urls_str,
        }
        print("Sending data:", data)  # 데이터 확인
        file = {'image': open(full_path, 'rb')}

        # 서버에 POST 요청 전송
        res = requests.post(f"{self.HOST}/api_root/Post/", data=data, files=file, headers=headers)
        print("Response status code:", res.status_code)
        print("Response content:", res.content)  # 응답 출력

        # 파일 닫기
        file['image'].close()

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # yolov5s 모델 사용 (경량 모델)

def detect_person_from_webcam(request=None):

    if request is None: # http 요청 없을 시 그냥 종료
        return 
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JsonResponse({'status': 'error', 'message': 'Failed to open webcam'}, status=400)
    previous_emotion = None
    current_emotion = None

    timeout = 10
    start_time = time.time()

    # 객체 및 감정 변화 감지
    change_detector = ChangeDetection(["person"])  # 예시로 "person" 클래스만 사용

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from webcam.")
            break

        # YOLOv5로 객체 탐지
        results = model(frame)

        xywh = results.xywh[0].cpu().numpy()
        df = pd.DataFrame(xywh, columns=['x', 'y', 'w', 'h', 'confidence', 'class'])
        # 결과에서 'person' 클래스만 필터링
        persons = df[df['class'] == 0]

        # 사람 객체가 발견되면 감정 분석 수행
        for index, row in persons.iterrows():
            x1, y1, x2, y2 = int(row['x'] - row['w'] / 2), int(row['y'] - row['h'] / 2), \
                              int(row['x'] + row['w'] / 2), int(row['y'] + row['h'] / 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 사람을 초록색 박스로 표시
            cv2.putText(frame, f'Person {index+1}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 감정 분석 실행
            face_image = frame[y1:y2, x1:x2]
            current_emotion = analyze_emotion_from_webcam(face_image)

            if previous_emotion is None:  # 첫 번째 감정 인식 시
                print("First emotion detected!")
                songs = youtube_search(f"{current_emotion} music")
                change_detector.add(["person"], [1], "path_to_save_image", frame, current_emotion, previous_emotion, songs)
                print("Recommended songs for the first emotion:")
                for song in songs:
                    print(f"Title: {song['title']}, URL: {song['url']}")
            elif previous_emotion != current_emotion:  # 감정이 변화하면
                print("Emotion has changed!")
                songs = youtube_search(f"{current_emotion} music")
                change_detector.add(["person"], [1], "path_to_save_image", frame, current_emotion, previous_emotion, songs)  # 감정 변화 시 이미지 업로드
                print(f"Recommended songs for {current_emotion}:")
                for song in songs:
                    print(f"Title: {song['title']}, URL: {song['url']}")

            previous_emotion = current_emotion
   


        if time.time() - start_time > timeout:
            print("Webcam timed out. Exiting.")
            break

        #cv2.imshow('Webcam - Press q to quit', frame)

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
        
        
    cap.release()
    cv2.destroyAllWindows()

# 실시간 감정 분석 및 사람 객체 탐지 실행
#detect_person_from_webcam()
