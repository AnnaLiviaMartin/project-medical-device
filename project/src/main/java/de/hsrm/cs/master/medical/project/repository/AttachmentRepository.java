package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.Attachment;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface AttachmentRepository extends JpaRepository<Attachment, Long> {
    List<Attachment> findByHistoryEntryIdOrderByUploadedAtDesc(Long historyEntryId);
}
