"use client";

import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import styles from "./patientRecord.module.css";
import type { Attachment, Scan } from "./patientRecord.data";
import { uploadAttachment, deleteAttachment } from "./attachments.api";
import { uploadXrayScan } from "./scans.api";

type AttachmentSectionProps = {
  attachments?: Attachment[];
  patientId: string;
  entryId: string;
  onScanUploaded?: (scan: Scan) => void;
};

const MAX_FILE_SIZE_MB = 20;
const ATTACHMENT_ACCEPTED_TYPES = ["application/pdf", "image/png", "image/jpeg"];
const XRAY_ACCEPTED_TYPES = ["image/png", "image/jpeg"];

export default function AttachmentSection(props: AttachmentSectionProps) {
  const patientId = props.patientId;
  const entryId = props.entryId;
  const initialAttachments = props.attachments || [];

  const [items, setItems] = useState<Attachment[]>(initialAttachments);
  const [isUploadingAttachment, setIsUploadingAttachment] = useState(false);
  const [isUploadingXray, setIsUploadingXray] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [xraySuccess, setXraySuccess] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const attachmentInputRef = useRef<HTMLInputElement>(null);
  const xrayInputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(function () {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return function () {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  function openAttachmentPicker() {
    setIsMenuOpen(false);
    if (attachmentInputRef.current) {
      attachmentInputRef.current.click();
    }
  }

  function openXrayPicker() {
    setIsMenuOpen(false);
    if (xrayInputRef.current) {
      xrayInputRef.current.click();
    }
  }

  async function handleAttachmentFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files && e.target.files[0];
    if (!file) {
      return;
    }

    setError(null);
    setXraySuccess(null);

    if (ATTACHMENT_ACCEPTED_TYPES.indexOf(file.type) === -1) {
      setError("Nur PDF oder Bilddateien (PNG/JPG) sind erlaubt.");
      e.target.value = "";
      return;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError("Datei ist groesser als " + MAX_FILE_SIZE_MB + " MB.");
      e.target.value = "";
      return;
    }

    setIsUploadingAttachment(true);
    try {
      const uploaded = await uploadAttachment(patientId, entryId, file);
      setItems(function (prev) {
        return prev.concat([uploaded]);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload fehlgeschlagen.");
    } finally {
      setIsUploadingAttachment(false);
      if (attachmentInputRef.current) {
        attachmentInputRef.current.value = "";
      }
    }
  }

  async function handleXrayFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files && e.target.files[0];
    if (!file) {
      return;
    }

    setError(null);
    setXraySuccess(null);

    if (XRAY_ACCEPTED_TYPES.indexOf(file.type) === -1) {
      setError("Roentgenaufnahmen muessen als PNG oder JPG vorliegen.");
      e.target.value = "";
      return;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError("Datei ist groesser als " + MAX_FILE_SIZE_MB + " MB.");
      e.target.value = "";
      return;
    }

    setIsUploadingXray(true);
    try {
      const scan = await uploadXrayScan(patientId, entryId, file);
      setXraySuccess(
        "Roentgenaufnahme hochgeladen und an die KI zur Analyse uebergeben."
      );
      if (props.onScanUploaded) {
        props.onScanUploaded(scan);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Roentgenaufnahme-Upload fehlgeschlagen."
      );
    } finally {
      setIsUploadingXray(false);
      if (xrayInputRef.current) {
        xrayInputRef.current.value = "";
      }
    }
  }

  async function handleDelete(attachmentId: string) {
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
      setError(err instanceof Error ? err.message : "Loeschen fehlgeschlagen.");
    }
  }

  const isUploading = isUploadingAttachment || isUploadingXray;

  return (
    <div className={styles.attachmentSection}>
      <div className={styles.attachmentHeader}>
        <p className={styles.scanSectionLabel}>Attachments</p>

        <div className={styles.attachmentAddWrapper} ref={menuRef}>
          <button
            type="button"
            className={styles.attachmentUploadButton}
            onClick={function () {
              setIsMenuOpen(function (open) {
                return !open;
              });
            }}
            disabled={isUploading}
          >
            {isUploadingAttachment
              ? "Anhang wird hochgeladen..."
              : isUploadingXray
              ? "Roentgenaufnahme wird hochgeladen..."
              : "+ Add Attachment"}
          </button>

          {isMenuOpen ? (
            <div className={styles.attachmentDropdown}>
              <button
                type="button"
                className={styles.attachmentDropdownItem}
                onClick={openAttachmentPicker}
              >
                Anhang (PDF, Bild)
              </button>
              <button
                type="button"
                className={styles.attachmentDropdownItemXray}
                onClick={openXrayPicker}
              >
                Roentgenaufnahme (fuer KI-Analyse)
              </button>
            </div>
          ) : null}
        </div>

        <input
          ref={attachmentInputRef}
          type="file"
          accept={ATTACHMENT_ACCEPTED_TYPES.join(",")}
          onChange={handleAttachmentFileChange}
          hidden
        />
        <input
          ref={xrayInputRef}
          type="file"
          accept={XRAY_ACCEPTED_TYPES.join(",")}
          onChange={handleXrayFileChange}
          hidden
        />
      </div>

      {error ? <p className={styles.attachmentError}>{error}</p> : null}
      {xraySuccess ? (
        <p className={styles.attachmentXraySuccessMessage}>{xraySuccess}</p>
      ) : null}

      {items.length === 0 ? (
        <p className={styles.attachmentEmpty}>Keine Anhaenge vorhanden.</p>
      ) : (
        <ul className={styles.attachmentList}>
          {items.map(function (item) {
            return (
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
                  onClick={function () {
                    handleDelete(item.id);
                  }}
                  aria-label={"Entfernen: " + item.fileName}
                >
                  x
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
