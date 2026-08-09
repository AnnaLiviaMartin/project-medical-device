package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.XRayImage;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.repository.XRayImageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class XRayImageService {

    @Autowired
    private XRayImageRepository xRayImageRepository;

    public XRayImage save(XRayImage xRayImage) {
        return xRayImageRepository.save(xRayImage);
    }

    public XRayImage findById(Long id) {
        return xRayImageRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("No X-ray image found with ID " + id + "."));
    }
}
