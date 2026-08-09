package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.exception.FileStorageException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

/**
 * Kapselt den Dateizugriff auf das Upload-Verzeichnis. Dateien
 * werden unter einem zufaelligen Praefix gespeichert, um Namenskollisionen
 * zu vermeiden - der urspruengliche Dateiname bleibt separat in der
 * jeweiligen Entity (originalFilename) erhalten.
 */
@Service
public class FileStorageService {

    private Path uploadRoot;

    @Value("${upload_dir}")
    private String uploadDir;

    private void init() {
        this.uploadRoot = Path.of(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(uploadRoot);
        } catch (IOException e) {
            throw new FileStorageException("Could not initialize upload directory: " + uploadRoot, e);
        }
    }

    /**
     * Speichert eine hochgeladene Datei unterhalb von {@code subdir} und gibt den
     * relativen Pfad (subdir/gespeicherter-name) zurueck - genau dieser Pfad wird
     * in der Entity abgelegt und spaeter unter /media/{relativePath} ausgeliefert.
     */
    public String store(MultipartFile file, String subdir) {
        if (file == null || file.isEmpty()) {
            throw new FileStorageException("No file was submitted.");
        }

        String originalFilename = StringUtils.cleanPath(
                file.getOriginalFilename() == null ? "file" : file.getOriginalFilename()
        );
        String extension = "";
        int dotIndex = originalFilename.lastIndexOf('.');
        if (dotIndex >= 0) {
            extension = originalFilename.substring(dotIndex);
        }

        String storedName = UUID.randomUUID() + extension;

        try {
            init();
            Path targetDir = uploadRoot.resolve(subdir).normalize();
            Files.createDirectories(targetDir);
            Path targetPath = targetDir.resolve(storedName);
            Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
            return subdir + "/" + storedName;
        } catch (IOException e) {
            throw new FileStorageException("File could not be saved: " + originalFilename, e);
        }
    }

    public Path resolve(String relativePath) {
        init();
        return uploadRoot.resolve(relativePath).normalize();
    }

    public String storeGeneratedPng(BufferedImage image, String subdir, String filenameWithoutExtension) {
        try {
            init();
            Path targetDir = uploadRoot.resolve(subdir).normalize();
            Files.createDirectories(targetDir);
            String storedName = filenameWithoutExtension + ".png";
            Path targetPath = targetDir.resolve(storedName);
            ImageIO.write(image, "png", targetPath.toFile());
            return subdir + "/" + storedName;
        } catch (IOException e) {
            throw new FileStorageException("Generated image could not be saved.", e);
        }
    }

    public void delete(String relativePath) {
        if (relativePath == null || relativePath.isBlank()) {
            return;
        }
        try {
            Files.deleteIfExists(resolve(relativePath));
        } catch (IOException e) {
            throw new FileStorageException("File could not be deleted: " + relativePath, e);
        }
    }
}
