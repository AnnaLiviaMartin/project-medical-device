"use client";

import { useRef, useState, type ChangeEvent } from "react";
import styles from "./patientRecord.module.css";
import type { Attachment, Scan } from "./patientRecord.data";
import { uploadAttachment, uploadScan, deleteAttachment } from "./attachments.api";

type AttachmentSectionProps = {
  attachments?: Attachment[];
  patientId: string;
  entryId: string;
  onScanUploaded?: (scan: Scan) => void;
};

type UploadKind = "scan" | "document";

const MAX_FILE_SIZE_MB = 20;
const ACCEPTED_TYPES = ["application/pdf", "image/png", "image/jpeg"];

export default function AttachmentSection(props: AttachmentSectionProps) {
  const patientId = props.patientId;
  const entryId = props.entryId;
  const initialAttachments = props.attachments || [];

  const [items, setItems] = useState<Attachment[]>(initialAttachments);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingKind, setPendingKind] = useState<UploadKind | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function startUpload(kind: UploadKind) {
    setPendingKind(kind);
    inputRef.current?.click();
  }

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files && e.target.files[0];
    const kind = pendingKind;

    if (!file || !kind) {
      setPendingKind(null);
      return;
    }

    setError(null);

    if (ACCEPTED_TYPES.indexOf(file.type) === -1) {
      setError("Nur PDF oder Bilddateien (PNG/JPG) sind erlaubt.");
      e.target.value = "";
      setPendingKind(null);
      return;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError("Datei ist groesser als " + MAX_FILE_SIZE_MB + " MB.");
      e.target.value = "";
      setPendingKind(null);
      return;
    }

    setIsUploading(true);
    try {
      if (kind === "scan") {
        const scan = await uploadScan(patientId, entryId, file);
        if (props.onScanUploaded) {
          props.onScanUploaded(scan);
        }
      } else {
        const uploaded = await uploadAttachment(patientId, entryId, file);
        setItems((prev) => prev.concat([uploaded]));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload fehlgeschlagen.");
    } finally {
      setIsUploading(false);
      setPendingKind(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  async function handleDelete(attachmentId: string) {
    const prevItems = items;
    setItems((prev) => prev.filter((a) => a.id !== attachmentId));
    try {
      await deleteAttachment(patientId, entryId, attachmentId);
    } catch (err) {
      setItems(prevItems);
      setError(err instanceof Error ? err.message : "Loeschen fehlgeschlagen.");
    }
  }

  return (
    <div className={styles.attachmentSection}>
      <div className={styles.attachmentHeader}>
        <p className={styles.scanSectionLabel}>Attachments</p>
        <div className={styles.attachmentUploadChoices}>
          <button
            type="button"
            className={styles.attachmentUploadButton}
            onClick={() => startUpload("scan")}
            disabled={isUploading}
          >
            {isUploading && pendingKind === "scan"
              ? "Wird hochgeladen..."
              : "+ Röntgenaufnahme"}
          </button>
          <button
            type="button"
            className={styles.attachmentUploadButton}
            onClick={() => startUpload("document")}
            disabled={isUploading}
          >
            {isUploading && pendingKind === "document"
              ? "Wird hochgeladen..."
              : "+ Dokument/Bild"}
          </button>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(",")}
          onChange={handleFileChange}
          disabled={isUploading}
          hidden
        />
      </div>

      {error ? <p className={styles.attachmentError}>{error}</p> : null}

      {items.length === 0 ? (
        <p className={styles.attachmentEmpty}>Keine Anhaenge vorhanden.</p>
      ) : (
        <ul className={styles.attachmentList}>
          {items.map((item) => (
            <li key={item.id} className={styles.attachmentItem}>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.attachmentLink}
              >
                {item.fileName}
              </a>
              <span className={styles.attachmentMeta}>
                {(item.fileSize / 1024).toFixed(0)} KB
              </span>
              <button
                type="button"
                className={styles.attachmentDeleteButton}
                onClick={() => handleDelete(item.id)}
                aria-label={"Entfernen: " + item.fileName}
              >
                x
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}