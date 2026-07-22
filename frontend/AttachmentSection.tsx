"use client";

import { useRef, useState } from "react";
import styles from "./patientRecord.module.css";
import type { Attachment } from "./patientRecord.data";
import { uploadAttachment, deleteAttachment } from "./attachments.api";

type AttachmentSectionProps = {
  attachments?: Attachment[];
  patientId: string;
  entryId: string;
};

const MAX_FILE_SIZE_MB = 20;
const ACCEPTED_TYPES = ["application/pdf", "image/png", "image/jpeg"];

export default function AttachmentSection(props: AttachmentSectionProps) {
  const patientId = props.patientId;
  const entryId = props.entryId;
  const initialAttachments = props.attachments || [];

  const [items, setItems] = useState(initialAttachments);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleFileChange(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) {
      return;
    }

    setError(null);

    if (ACCEPTED_TYPES.indexOf(file.type) === -1) {
      setError("Nur PDF oder Bilddateien (PNG/JPG) sind erlaubt.");
      e.target.value = "";
      return;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError("Datei ist groesser als " + MAX_FILE_SIZE_MB + " MB.");
      e.target.value = "";
      return;
    }

    setIsUploading(true);
    try {
      const uploaded = await uploadAttachment(patientId, entryId, file);
      setItems(function (prev) {
        return prev.concat([uploaded]);
      });
    } catch (err) {
      setError(err && err.message ? err.message : "Upload fehlgeschlagen.");
    } finally {
      setIsUploading(false);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  async function handleDelete(attachmentId) {
    const prevItems = items;
    setItems(function (prev) {
      return prev.filter(function (a) {
        return a.id !== attachmentId;
      });
    });
    try {
      await deleteAttachment(patientId, entryId, attachmentId);
    } catch (err) {
      setItems(prevItems);
      setError(err && err.message ? err.message : "Loeschen fehlgeschlagen.");
    }
  }

  return (
    <div className={styles.attachmentSection}>
      <div className={styles.attachmentHeader}>
        <p className={styles.scanSectionLabel}>Attachments</p>
        <label className={styles.attachmentUploadButton}>
          {isUploading ? "Wird hochgeladen..." : "+ Datei anhaengen"}
          <input ref={inputRef} type="file" accept={ACCEPTED_TYPES.join(",")} onChange={handleFileChange} disabled={isUploading} hidden />
        </label>
      </div>

      {error ? <p className={styles.attachmentError}>{error}</p> : null}

      {items.length === 0 ? (
        <p className={styles.attachmentEmpty}>Keine Anhaenge vorhanden.</p>
      ) : (
        <ul className={styles.attachmentList}>
          {items.map(function (item) {
            return (
              <li key={item.id} className={styles.attachmentItem}>
                <a href={item.url} target="_blank" rel="noopener noreferrer" className={styles.attachmentLink}>{item.fileName}</a>
                <span className={styles.attachmentMeta}>{(item.fileSize / 1024).toFixed(0)} KB</span>
                <button type="button" className={styles.attachmentDeleteButton} onClick={function () { handleDelete(item.id); }} aria-label={"Entfernen: " + item.fileName}>x</button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
