package com.example.moweb2;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {

    private static final int MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE = 1;
    private static final int PICK_IMAGE_REQUEST = 1;

    private RecyclerView recyclerView;
    private PostAdapter postAdapter;
    private ApiService apiService;

    private ImageView imgView;
    private TextView textView;
    private String siteUrl = "http://10.0.2.2:8000/";
    JSONObject post_json;
    String imageUrl = null;
    Bitmap bmImg = null;
    private Uri selectedImageUri;
    private CloadImage taskDownload;
    private PutPost taskUpload;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // UI 요소 연결
        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        imgView = findViewById(R.id.imgView);
        textView = findViewById(R.id.textView);

        Button syncButton = findViewById(R.id.syncButton);
        Button uploadButton = findViewById(R.id.uploadButton);
        Button cameraButton = findViewById(R.id.cameraButton);
        //Button downloadButton = findViewById(R.id.downloadButton);

        // Retrofit 설정
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(siteUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        apiService = retrofit.create(ApiService.class);

        // 권한 요청
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE);
        }

        // 버튼 리스너 설정
        syncButton.setOnClickListener(v -> fetchPosts());
        //downloadButton.setOnClickListener(this::onClickDownload);
        uploadButton.setOnClickListener(v -> openImagePicker());

        cameraButton.setOnClickListener(v -> {
            // CameraActivity로 전환
            Intent intent = new Intent(MainActivity.this, CameraActivity.class);
            startActivity(intent);  // CameraActivity 시작
        });
    }

    // 게시물 동기화
    private void fetchPosts() {
        Call<List<Post>> call = apiService.getPosts();
        call.enqueue(new Callback<List<Post>>() {
            @Override
            public void onResponse(Call<List<Post>> call, Response<List<Post>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<Post> posts = response.body();
                    postAdapter = new PostAdapter(posts);
                    recyclerView.setAdapter(postAdapter);
                    Toast.makeText(MainActivity.this, "동기화 완료", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MainActivity.this, "게시물 로드 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<Post>> call, Throwable t) {
                Toast.makeText(MainActivity.this, "서버 연결 실패", Toast.LENGTH_SHORT).show();
            }
        });
    }

    // 갤러리에서 이미지 선택을 위한 인텐트 실행
    private void openImagePicker() {
        Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent, PICK_IMAGE_REQUEST);
    }

    // 이미지 선택 후 결과 처리
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_IMAGE_REQUEST && resultCode == RESULT_OK && data != null && data.getData() != null) {
            selectedImageUri = data.getData();
            imgView.setImageURI(selectedImageUri);
            onClickUpload();
        }
    }

    // 이미지 업로드 버튼 클릭 시 호출
    public void onClickUpload() {
        if (selectedImageUri != null) {
            if (taskUpload == null || taskUpload.getStatus() == AsyncTask.Status.FINISHED) {
                taskUpload = new PutPost();
                taskUpload.execute(siteUrl + "/upload-image/");  // 업로드 엔드포인트 설정
            } else {
                Toast.makeText(this, "이미지 업로드 진행 중입니다.", Toast.LENGTH_SHORT).show();
            }
        } else {
            Toast.makeText(this, "이미지를 먼저 선택하세요", Toast.LENGTH_SHORT).show();
        }
    }

    // 이미지 다운로드 버튼 클릭 시 호출
    public void onClickDownload(View v) {
        // 현재 다운로드 작업이 진행 중인 경우 취소
        if (taskDownload != null && taskDownload.getStatus() == AsyncTask.Status.RUNNING) {
            taskDownload.cancel(true);
        }
        taskDownload = new CloadImage();
        taskDownload.execute(siteUrl + "/api_root/Post/");  // 이미지 경로 설정
        Toast.makeText(getApplicationContext(), "Download", Toast.LENGTH_LONG).show();
    }

    // 비동기 이미지 다운로드
    private class CloadImage extends AsyncTask<String, Integer, Bitmap> {
        @Override
        protected Bitmap doInBackground(String... urls) {
            try {
                URL url = new URL(urls[0]);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoInput(true);
                connection.connect();
                InputStream input = connection.getInputStream();
                return BitmapFactory.decodeStream(input);
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }

        @Override
        protected void onPostExecute(Bitmap result) {
            if (result != null) {
                imgView.setImageBitmap(result);
                textView.setText("다운로드 완료");
            } else {
                textView.setText("다운로드 실패");
            }
        }
    }

    // 비동기 이미지 업로드
    private class PutPost extends AsyncTask<String, Void, Boolean> {
        @Override
        protected Boolean doInBackground(String... urls) {
            try {
                InputStream inputStream = getContentResolver().openInputStream(selectedImageUri);
                Bitmap bitmap = BitmapFactory.decodeStream(inputStream);
                inputStream.close();

                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, byteArrayOutputStream);
                byte[] imageData = byteArrayOutputStream.toByteArray();

                URL url = new URL(urls[0]);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoOutput(true);
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=*****");

                // 요청 본문 생성
                OutputStream outputStream = connection.getOutputStream();
                PrintWriter writer = new PrintWriter(new OutputStreamWriter(outputStream, "UTF-8"));
                writer.append("--*****\r\n");
                writer.append("Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n");
                writer.append("Content-Type: image/jpeg\r\n\r\n");
                writer.flush();
                outputStream.write(imageData);
                outputStream.flush();
                writer.append("\r\n");
                writer.append("--*****--\r\n");
                writer.flush();
                writer.close();
                outputStream.close();

                int responseCode = connection.getResponseCode();
                connection.disconnect();
                return responseCode == HttpURLConnection.HTTP_OK;

            } catch (Exception e) {
                e.printStackTrace();
                return false;
            }
        }

        @Override
        protected void onPostExecute(Boolean success) {
            if (success) {
                Toast.makeText(MainActivity.this, "업로드 성공", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(MainActivity.this, "업로드 실패", Toast.LENGTH_SHORT).show();
            }
        }
    }
}
