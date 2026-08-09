package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Service
@Transactional
public class AttachmentService {

    // TODO use Interface
    // TODO auslagern in application.properties
    private static final String SUBDIR = "attachments";

    @Autowired
    private AttachmentRepository attachmentRepository;

    @Autowired
    private HistoryEntryService historyEntryService;

    @Autowired
    private FileStorageService fileStorageService;

    @Transactional(readOnly = true)
    public List<Attachment> findByHistoryEntry(Long entryId) {
        return attachmentRepository.findByHistoryEntryIdOrderByUploadedAtDesc(entryId);
    }

    public Attachment upload(Long patientId, Long entryId, MultipartFile file) {
        HistoryEntry entry = historyEntryService.getOrThrowForPatient(patientId, entryId);
        String storedPath = fileStorageService.store(file, SUBDIR);

        Attachment attachment = create(entry, storedPath, file);

        return attachmentRepository.save(attachment);
    }

    private Attachment create(HistoryEntry entry, String storedPath, MultipartFile file) {
        Attachment attachment = new Attachment();
        attachment.setHistoryEntry(entry);
        attachment.setStoredPath(storedPath);
        attachment.setOriginalFilename(file.getOriginalFilename());
        attachment.setFileSize(file.getSize());

        return attachment;
    }

    public void delete(Long patientId, Long entryId, Long attachmentId) {
        // Sicherstellen, dass der Eintrag tatsaechlich zu diesem Patienten gehoert.
        historyEntryService.getOrThrowForPatient(patientId, entryId);

        Attachment attachment = attachmentRepository.findById(attachmentId)
                .orElseThrow(() -> new ResourceNotFoundException("No attachment found with ID " + attachmentId + "."));

        if (!attachment.getHistoryEntry().getId().equals(entryId)) {
            throw new ResourceNotFoundException("No attachment found with ID " + attachmentId + " for this history entry.");
        }

        fileStorageService.delete(attachment.getStoredPath());
        attachmentRepository.delete(attachment);
    }
}
