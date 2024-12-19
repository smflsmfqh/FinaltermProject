package com.example.moweb2;

import java.util.List;

public class EmotionResponse {
    private List<String> recommendedSongs;  // 추천된 노래 목록

    public List<String> getRecommendedSongs() {
        return recommendedSongs;
    }

    public void setRecommendedSongs(List<String> recommendedSongs) {
        this.recommendedSongs = recommendedSongs;
    }
}