package com.example.moweb2;

import java.util.List;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;
import retrofit2.http.GET;
import retrofit2.http.Url;

public interface ApiService {
    @GET("api_root/Post/")
    Call<List<Post>> getPosts();
    @POST
    Call<EmotionResponse> getEmotionData(@Url String url, @Body ImageData imageData);


}