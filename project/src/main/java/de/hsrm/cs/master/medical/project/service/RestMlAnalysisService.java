package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.MlAnalysisResult;
import de.hsrm.cs.master.medical.project.exception.FileStorageException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Ruft den externen Python/FastAPI-Inferenz-Microservice (siehe /ml-service)
 * auf, der das echte PyTorch/DenseNet-Modell samt Grad-CAM ausfuehrt -
 * Umsetzung von Variante 1 aus dem Hinweis in {@link MlAnalysisService}.
 * <p>
 * Wird nur aktiviert, wenn "ml.analysis.provider=rest" gesetzt ist (siehe
 * application.properties). Ohne diese Einstellung bleibt weiterhin
 * {@link SimulatedMlAnalysisService} aktiv, damit das Backend auch ohne
 * laufenden ML-Service startet.
 */
@Service
@ConditionalOnProperty(name = "ml.analysis.provider", havingValue = "rest")
@Slf4j
public class RestMlAnalysisService implements MlAnalysisService {

    private final RestClient restClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public RestMlAnalysisService(@Value("${ml.service.url}") String mlServiceUrl, @Value("${ml.service.timeout-seconds:60}") long timeoutSeconds) {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(Duration.ofSeconds(10));
        requestFactory.setReadTimeout(Duration.ofSeconds(timeoutSeconds));

        this.restClient = RestClient.builder().baseUrl(mlServiceUrl).requestFactory(requestFactory).build();
    }

    @Override
    public MlAnalysisResult analyze(Path imagePath) {
        log.info("Real ML-Analysis for image: {}", imagePath);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(imagePath));

        String rawJson;
        try {
            rawJson = restClient.post().uri("/analyze").contentType(MediaType.MULTIPART_FORM_DATA).body(body).retrieve().body(String.class);
            log.info("ML-Service response: {}", rawJson);
        } catch (Exception ex) {
            throw new FileStorageException("ML-Inferenz-Service nicht erreichbar oder Analyse fehlgeschlagen " + "(ist der Service unter ml.service.url gestartet?): " + ex.getMessage(), ex);
        }

        return parseResponse(rawJson);
    }

    private MlAnalysisResult parseResponse(String rawJson) {
        try {
            JsonNode root = objectMapper.readTree(rawJson);

            String label = root.path("label").asString();
            double confidence = root.path("confidence").asDouble();
            double threshold = root.path("threshold").asDouble();
            Map<String, Double> scores = getScores(root);
            Map<String, BufferedImage> overlays = getOverlays(root);

            return new MlAnalysisResult(label, confidence, threshold, scores, overlays);
        } catch (IOException ex) {
            throw new FileStorageException("Antwort des ML-Service konnte nicht verarbeitet werden: " + ex.getMessage(), ex);
        }
    }

    private Map<String, Double> getScores (JsonNode root) {
        Map<String, Double> scores = new LinkedHashMap<>();
        for (Map.Entry<String, JsonNode> entry : root.path("scores").properties()) {
            scores.put(entry.getKey(), entry.getValue().asDouble());
        }

        return scores;
    }

    private Map<String, BufferedImage> getOverlays (JsonNode root) throws IOException {
        Map<String, BufferedImage> overlays = new LinkedHashMap<>();
        for (Map.Entry<String, JsonNode> entry : root.path("gradcam_images").properties()) {
            byte[] pngBytes = Base64.getDecoder().decode(entry.getValue().asText());
            BufferedImage image = ImageIO.read(new ByteArrayInputStream(pngBytes));
            overlays.put(entry.getKey(), image);
        }

        return overlays;
    }
}
