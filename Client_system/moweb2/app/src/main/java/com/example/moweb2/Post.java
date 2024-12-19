package com.example.moweb2;

import com.google.gson.annotations.SerializedName;
import java.util.List; // song_urls 불러올 수 있도록 추가
public class Post {

    @SerializedName("id")
    private int id;

    @SerializedName("title")
    private String title;

    @SerializedName("text")
    private String text;

    @SerializedName("created_date")
    private String createdDate;

    @SerializedName("image")
    private String image;

    @SerializedName("song_urls")  // song_urls 필드 추가
    private String songUrls;  // song_urls 필드

    // Getter 메서드들
    public int getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getText() {
        return text;
    }

    public String getCreatedDate() {
        return createdDate;
    }

    public String getImage() {
        return image;
    }

    public String getSongUrls() {  // getter 추가
        return songUrls;
    }
}
