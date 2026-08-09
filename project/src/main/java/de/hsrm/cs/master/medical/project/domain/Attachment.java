package de.hsrm.cs.master.medical.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "attachments")
@Getter
@Setter
public class Attachment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "history_entry_id", nullable = false)
    private HistoryEntry historyEntry;

    /** Relativer Pfad unterhalb des Upload-Verzeichnisses, z. B. "attachments/uuid_befund.pdf". */
    @Column(nullable = false)
    private String storedPath;

    @Column(nullable = false)
    private String originalFilename;

    @Column(nullable = false)
    private long fileSize;

    @Column(nullable = false, updatable = false)
    private LocalDateTime uploadedAt = LocalDateTime.now();
}
