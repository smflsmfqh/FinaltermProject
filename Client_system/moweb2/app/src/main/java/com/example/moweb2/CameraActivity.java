package com.example.moweb2;

import android.Manifest;
import androidx.core.app.ActivityCompat;
import android.content.pm.PackageManager;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Toast;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.core.CameraSelector;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LifecycleOwner;
import java.io.File;
import androidx.annotation.NonNull;
import androidx.camera.core.ImageCaptureException;
import java.util.List;
import com.google.common.util.concurrent.ListenableFuture;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CameraActivity extends AppCompatActivity {

    private Preview preview;
    private ImageCapture imageCapture;
    private CameraSelector cameraSelector;
    private PreviewView viewFinder;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);

        Log.d("CameraActivity", "CameraActivity started");

        viewFinder = findViewById(R.id.viewFinder);  // PreviewView 설정

        // 권한 요청
        requestPermissions();

        // CameraX 초기화
        startCamera();

        // 이미지 캡처 버튼 클릭 이벤트
        findViewById(R.id.captureButton).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                captureImage();
            }
        });
    }

    private void startCamera() {
        CameraSelector cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA;

        ListenableFuture<ProcessCameraProvider> cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                ProcessCameraProvider cameraProvider = cameraProviderFuture.get();

                // 카메라 프리뷰 설정
                preview = new Preview.Builder().build();
                preview.setSurfaceProvider(viewFinder.getSurfaceProvider());

                // ImageCapture 설정
                imageCapture = new ImageCapture.Builder().build();

                // 카메라 바인딩
                cameraProvider.bindToLifecycle((LifecycleOwner) this, cameraSelector, preview, imageCapture);

            } catch (Exception e) {
                Log.e("CameraX", "카메라 초기화 실패", e);
            }
        }, ContextCompat.getMainExecutor(this));
    }

    // 이미지 캡처 메서드
    private void captureImage() {
        File photoFile = new File(getExternalFilesDir(null), "photo.jpg");
        ImageCapture.OutputFileOptions options = new ImageCapture.OutputFileOptions.Builder(photoFile).build();

        imageCapture.takePicture(options, ContextCompat.getMainExecutor(this), new ImageCapture.OnImageSavedCallback() {
            @Override
            public void onImageSaved(@NonNull ImageCapture.OutputFileResults outputFileResults) {
                Log.d("CameraX", "사진 저장됨: " + outputFileResults.getSavedUri());

                // 이미지 업로드 후 감정 분석 요청
                uploadImageToServer(photoFile);
            }

            @Override
            public void onError(@NonNull ImageCaptureException exception) {
                Log.e("CameraX", "사진 저장 실패", exception);
            }
        });
    }

    // 서버로 이미지 업로드
    private void uploadImageToServer(File photoFile) {
        // 서버에 업로드할 이미지 데이터 준비
        ImageData imageData = new ImageData(photoFile);

        RetrofitClient.getApiService().uploadImage(imageData).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                if (response.isSuccessful()) {
                    // 서버에서 감정 분석 후 추천된 노래 요청
                    getEmotionRecommendation(imageData);
                } else {
                    Toast.makeText(CameraActivity.this, "이미지 업로드 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Log.e("Retrofit", "서버 연결 실패", t);
                Toast.makeText(CameraActivity.this, "서버 연결 실패", Toast.LENGTH_SHORT).show();
            }
        });
    }

    // 서버에서 감정 분석 요청 후 추천된 노래 받기
    private void getEmotionRecommendation(ImageData imageData) {
        RetrofitClient.getEmotionApiService().getEmotionRecommendation(imageData).enqueue(new Callback<EmotionResponse>() {
            @Override
            public void onResponse(Call<EmotionResponse> call, Response<EmotionResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    EmotionResponse emotionResponse = response.body();
                    // 감정 분석 후 추천된 노래 처리
                    List<String> recommendedSongs = emotionResponse.getRecommendedSongs();
                    Toast.makeText(CameraActivity.this, "추천된 노래: " + recommendedSongs, Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(CameraActivity.this, "감정 인식 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<EmotionResponse> call, Throwable t) {
                Log.e("Retrofit", "서버 연결 실패", t);
                Toast.makeText(CameraActivity.this, "서버 연결 실패", Toast.LENGTH_SHORT).show();
            }
        });
    }

    // 권한 요청 메서드
    private void requestPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, 1);
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 2);
        }
    }

    // 권한 요청 결과 처리
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == 1) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startCamera();
            } else {
                Log.e("CameraX", "카메라 권한이 거부되었습니다.");
            }
        }
    }
}
