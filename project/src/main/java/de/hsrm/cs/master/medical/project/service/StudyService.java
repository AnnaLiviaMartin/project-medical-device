package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.Study;
import de.hsrm.cs.master.medical.project.repository.StudyRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class StudyService {

    @Autowired
    private StudyRepository studyRepository;

    public Study save(Study study) {
        return studyRepository.save(study);
    }
}
