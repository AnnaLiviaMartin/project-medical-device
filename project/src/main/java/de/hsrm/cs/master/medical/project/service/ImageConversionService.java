package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.exception.FileStorageException;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import javax.imageio.ImageReader;
import javax.imageio.stream.ImageInputStream;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Iterator;
import java.util.Locale;

@Service
public class ImageConversionService {

    /**
     * Konvertiert PNG, JPG/JPEG oder DICOM immer in ein PNG.
     * PNG: wird unverändert zurückgegeben.
     * JPG/JPEG: wird in PNG konvertiert.
     * DICOM: wird über den DICOM ImageIO Reader in PNG konvertiert.
     */
    public byte[] convertToPng(MultipartFile file) {

        if (file == null || file.isEmpty()) {
            throw new FileStorageException("No image was submitted.");
        }

        String filename = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().toLowerCase(Locale.ROOT);

        try {
            if (isDcm(file)) {
                return convertDicomToPng(file);
            }

            if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) {
                return convertJpegToPng(file);
            }

            if (filename.endsWith(".png")) {
                validatePng(file);
                return file.getBytes();
            }

            throw new FileStorageException("Unsupported image format. " + "Only PNG, JPG, JPEG and DICOM are supported.");

        } catch (IOException e) {
            throw new FileStorageException("Could not convert image to PNG.", e);
        }
    }

    public boolean isDcm(MultipartFile file) {
        try {
            byte[] bytes = file.getBytes();

            if (bytes.length < 132) {
                return false;
            }

            return bytes[128] == 'D' && bytes[129] == 'I' && bytes[130] == 'C' && bytes[131] == 'M';

        } catch (IOException e) {
            throw new FileStorageException("Could not inspect uploaded file.", e);
        }
    }

    private byte[] convertJpegToPng(MultipartFile file) throws IOException {
        BufferedImage image = ImageIO.read(file.getInputStream());

        if (image == null) {
            throw new FileStorageException("Uploaded JPEG could not be decoded.");
        }

        BufferedImage rgbImage = toRgb(image);
        return encodePng(rgbImage);
    }

    private byte[] convertDicomToPng(MultipartFile file) throws IOException {
        byte[] dcmBytes = file.getBytes();

        BufferedImage image = readDicomImage(dcmBytes);

        if (image == null) {
            throw new FileStorageException("DICOM does not contain a readable image.");
        }

        BufferedImage rgbImage = toRgb(image);
        return encodePng(rgbImage);
    }

    private BufferedImage readDicomImage(byte[] bytes) throws IOException {
        try (InputStream inputStream = new ByteArrayInputStream(bytes);
             ImageInputStream imageInputStream = ImageIO.createImageInputStream(inputStream)) {

            if (imageInputStream == null) {
                throw new IOException("Could not create DICOM ImageInputStream.");
            }

            Iterator<ImageReader> readers = ImageIO.getImageReadersByFormatName("DICOM");

            if (!readers.hasNext()) {
                throw new IOException("No DICOM ImageIO reader found. " + "Make sure dcm4che-imageio is configured.");
            }

            ImageReader reader = readers.next();

            try {
                reader.setInput(imageInputStream);
                return reader.read(0);
            } finally {
                reader.dispose();
            }
        }
    }

    private BufferedImage toRgb(BufferedImage source) {
        BufferedImage rgb = new BufferedImage(source.getWidth(), source.getHeight(), BufferedImage.TYPE_INT_RGB);
        Graphics2D graphics = rgb.createGraphics();

        try {
            graphics.drawImage(source, 0, 0, null);
        } finally {
            graphics.dispose();
        }

        return rgb;
    }

    private byte[] encodePng(BufferedImage image) throws IOException {
        ByteArrayOutputStream output = new ByteArrayOutputStream();

        boolean success = ImageIO.write(image, "png", output);

        if (!success) {
            throw new IOException("No PNG ImageIO writer available.");
        }

        return output.toByteArray();
    }

    private void validatePng(MultipartFile file) throws IOException {
        BufferedImage image = ImageIO.read(file.getInputStream());

        if (image == null) {
            throw new FileStorageException("Uploaded PNG could not be decoded.");
        }
    }
}