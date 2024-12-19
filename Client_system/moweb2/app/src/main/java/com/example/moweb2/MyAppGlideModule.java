package com.example.moweb2;

import android.content.Context;

import com.bumptech.glide.GlideBuilder;
import com.bumptech.glide.annotation.GlideModule;
import com.bumptech.glide.module.AppGlideModule;

@GlideModule
public final class MyAppGlideModule extends AppGlideModule {
    // 이 클래스는 Glide가 앱에서 사용하는 설정을 자동으로 적용합니다.
    @Override
    public void applyOptions(Context context, GlideBuilder builder) {
        super.applyOptions(context, builder);
        // 추가적인 Glide 설정을 여기에 할 수 있습니다 (선택 사항)
    }
}
