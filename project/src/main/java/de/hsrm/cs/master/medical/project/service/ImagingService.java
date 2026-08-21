package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.exception.FileStorageException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.awt.image.BufferedImage;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

@Service
@Transactional
public class ImagingService {

    protected static final List<String> ALLOWED_EXTENSIONS = List.of(".png", ".jpg", ".jpeg", ".dcm");
    // TODO auslagern in application.properties
    // TODO clean up methods
    private static final String XRAY_SUBDIR = "xray_images";
    private static final String GRADCAM_SUBDIR = "gradcam";
    @Autowired
    private XRayImageService xRayImageService;

    @Autowired
    private PredictionService predictionService;

    @Autowired
    private HistoryEntryService historyEntryService;

    @Autowired
    private FileStorageService fileStorageService;

    @Autowired
    private MlAnalysisService mlAnalysisService;

    @Autowired
    private StudyService studyService;

    @Autowired
    private ImageConversionService imageConversionService;

    public void assertSupportedImageType(MultipartFile file) {
        String name = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().toLowerCase(Locale.ROOT);
        boolean allowed = ALLOWED_EXTENSIONS.stream().anyMatch(name::endsWith);
        if (!allowed) {
            throw new FileStorageException("Unsupported file type. Please upload a PNG or JPEG image (DICOM conversion is not supported in this version).");
        }
    }

    public void uploadScan(Long patientId, Long entryId, MultipartFile file) {
        assertSupportedImageType(file);

        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename() == null ? "file" : file.getOriginalFilename());
        byte[] pngBytes = imageConversionService.convertToPng(file);

        HistoryEntry entry = historyEntryService.getOrThrowForPatient(patientId, entryId);

        Study study = entry.getStudy();
        if (study == null) {
            study = new Study();
            study.setPatient(entry.getPatient());
            study = studyService.save(study);
            entry.setStudy(study);
            historyEntryService.save(entry);
        }

        String storedPath = fileStorageService.store(pngBytes, XRAY_SUBDIR, originalFilename);

        XRayImage image = new XRayImage();
        image.setStudy(study);
        image.setStoredPath(storedPath);
        image.setPredictionStatus(PredictionStatus.RUNNING);
        image = xRayImageService.save(image);

        runAnalysis(image);
    }

    private void runAnalysis(XRayImage image) {
        try {
            Path absolutePath = fileStorageService.resolve(image.getStoredPath());
            MlAnalysisResult result = mlAnalysisService.analyze(absolutePath);

            Prediction prediction = predictionService.findByXrayImageId(image.getId()).orElseGet(Prediction::new);
            prediction.setXrayImage(image);
            prediction.setLabel(result.label());
            prediction.setConfidence(result.confidence());
            prediction.setThreshold(result.threshold());
            prediction.setScores(result.scores());

            Map<String, String> gradCamPaths = new java.util.LinkedHashMap<>();
            for (Map.Entry<String, BufferedImage> overlay : result.gradCamOverlaysByPathology().entrySet()) {
                String filename = UUID.randomUUID() + "_" + overlay.getKey().replace(" ", "_");
                String path = fileStorageService.storeGeneratedPng(overlay.getValue(), GRADCAM_SUBDIR, filename);
                gradCamPaths.put(overlay.getKey(), path);
            }
            prediction.setGradCamPaths(gradCamPaths);

            predictionService.save(prediction);

            image.setPredictionStatus(PredictionStatus.DONE);
            xRayImageService.save(image);
        } catch (Exception ex) {
            image.setPredictionStatus(PredictionStatus.FAILED);
            xRayImageService.save(image);
            throw new FileStorageException("Analysis failed: " + ex.getMessage(), ex);
        }
    }
}
