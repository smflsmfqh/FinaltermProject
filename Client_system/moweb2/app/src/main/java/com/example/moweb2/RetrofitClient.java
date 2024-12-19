package com.example.moweb2;

import retrofit2.Call;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import retrofit2.http.Body;
import retrofit2.http.POST;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import java.util.List; // List를 임포트합니다.

public class RetrofitClient {

    private static Retrofit retrofit = null;

    public static ApiService getApiService() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl("http://10.0.2.2:8000/") // 로컬 서버 주소
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(ApiService.class);
    }

    // 이미지 업로드 API 정의 (ImageData 모델 사용)
    public interface ApiService {
        @POST("upload-image/")  // 서버에 이미지를 업로드하는 경로
        Call<Void> uploadImage(@Body ImageData imageData);  // ImageData를 전송
    }

    // 감정 분석 요청 후 노래 추천을 받는 API 정의 (EmotionResponse 모델 사용)
    public interface EmotionApiService {
        @POST("detect_emotion_and_recommend/")  // 서버에서 감정 분석 후 추천된 노래 받기
        Call<EmotionResponse> getEmotionRecommendation(@Body ImageData imageData);  // 이미지 데이터를 서버로 전송하고 감정 분석 후 추천된 노래 리스트 받기
    }
    // 감정 분석 API 서비스 호출
    public static EmotionApiService getEmotionApiService() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl("http://10.0.2.2:8000/") // 로컬 서버 주소
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(EmotionApiService.class);
    }
}