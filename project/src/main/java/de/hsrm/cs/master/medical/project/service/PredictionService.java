package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.Prediction;
import de.hsrm.cs.master.medical.project.repository.PredictionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@Transactional
public class PredictionService {

    @Autowired
    private PredictionRepository predictionRepository;

    public Prediction save(Prediction prediction) {
        return this.predictionRepository.save(prediction);
    }

    public Optional<Prediction> findByXrayImageId(Long xrayImageId) {
        return this.predictionRepository.findByXrayImageId(xrayImageId);
    }
}
