package com.example.moweb2;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import java.util.List;

public class PostAdapter extends RecyclerView.Adapter<PostAdapter.PostViewHolder> {

    private List<Post> posts;

    public PostAdapter(List<Post> posts) {
        this.posts = posts;
    }

    @Override
    public PostViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_post, parent, false);
        return new PostViewHolder(view);
    }

    @Override
    public void onBindViewHolder(PostViewHolder holder, int position) {
        Post post = posts.get(position);
        holder.titleTextView.setText(post.getTitle());
        holder.textTextView.setText(post.getText());
        Glide.with(holder.imageView.getContext()).load(post.getImage()).into(holder.imageView);

        // 노래 추천 URL 처리 (여러 개의 song URLs 처리)
        String songUrls = post.getSongUrls(); // 이제 songUrls는 String 타입입니다.

        if (songUrls != null && !songUrls.isEmpty()) {
            holder.songUrlsTextView.setVisibility(View.VISIBLE);

            // 쉼표(,)로 구분된 여러 개의 URL을 분리하여 표시
            String[] songUrlArray = songUrls.split(","); // 쉼표로 구분된 URL들을 배열로 분리

            StringBuilder songUrlsString = new StringBuilder();
            for (String songUrl : songUrlArray) {
                songUrlsString.append(songUrl.trim()).append("\n"); // 각 URL을 줄바꿈으로 구분
            }

            holder.songUrlsTextView.setText(songUrlsString.toString());
        } else {
            holder.songUrlsTextView.setVisibility(View.GONE); // songUrls가 없으면 숨김
        }
    }

    @Override
    public int getItemCount() {
        return posts.size();
    }

    public void updatePosts(List<Post> newPosts) {
        this.posts = newPosts;
        notifyDataSetChanged();
    }

    static class PostViewHolder extends RecyclerView.ViewHolder {
        TextView titleTextView, textTextView, songUrlsTextView;
        ImageView imageView;

        PostViewHolder(View itemView) {
            super(itemView);
            titleTextView = itemView.findViewById(R.id.titleTextView);
            textTextView = itemView.findViewById(R.id.textTextView);
            imageView = itemView.findViewById(R.id.imageView);
            songUrlsTextView = itemView.findViewById(R.id.songUrlsTextView);  // songUrlsTextView 연결
        }
    }
}
