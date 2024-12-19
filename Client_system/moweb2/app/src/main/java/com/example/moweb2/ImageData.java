package com.example.moweb2;

import java.io.File;

public class ImageData {
    private File imageFile;

    public ImageData(File imageFile) {
        this.imageFile = imageFile;
    }

    public File getImageFile() {
        return imageFile;
    }

    public void setImageFile(File imageFile) {
        this.imageFile = imageFile;
    }
}