"use client";

import { useState } from "react";
import styles from "./patientRecord.module.css";
import type { HistoryEntry, Scan } from "./patientRecord.data";
import ScanLinkList from "./ScanLinkList";
import AttachmentSection from "./AttachmentSection";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type PatientHistoryTimelineProps = {
  history: HistoryEntry[];
  patientId: string;
};

function todayISO() {
  const now = new Date();
  const offset = now.getTimezoneOffset();
  const local = new Date(now.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 10);
}

export default function PatientHistoryTimeline({
  history,
  patientId,
}: PatientHistoryTimelineProps) {
  const [entries, setEntries] = useState<HistoryEntry[]>(history);
  const [showForm, setShowForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDate, setNewDate] = useState(todayISO());
  const [newDoctor, setNewDoctor] = useState("");
  const [newDepartment, setNewDepartment] = useState("");
  const [newNote, setNewNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  function handleScanUploaded(entryId: string, scan: Scan) {
    setEntries(function (prev) {
      return prev.map(function (entry) {
        if (entry.id !== entryId) {
          return entry;
        }
        return { ...entry, scans: (entry.scans || []).concat([scan]) };
      });
    });
  }

  function openForm() {
    setNewTitle("");
    setNewDate(todayISO());
    setNewDoctor("");
    setNewDepartment("");
    setNewNote("");
    setError(null);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setError(null);
  }

  async function handleAddEvent(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!newTitle.trim() || !newDate) {
      setError("Please provide a name and a date.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${BASE_URL}/api/history/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient: Number(patientId),
          date: newDate,
          title: newTitle.trim(),
          category: "Visit",
          doctor: newDoctor.trim(),
          department: newDepartment.trim(),
          description: newNote.trim(),
        }),
      });

      if (!res.ok) {
        const errorBody = await res.json().catch(() => null);
        const message = errorBody
          ? Object.entries(errorBody)
              .map(([field, msgs]) =>
                `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
              )
              .join(" | ")
          : `Error creating entry: ${res.status}`;
        throw new Error(message);
      }

      const created = await res.json();
      const createdEntry: HistoryEntry = {
        ...created,
        id: String(created.id),
        scans: created.scans ?? [],
        attachments: created.attachments ?? [],
      };

      setEntries((prev) =>
        [...prev, createdEntry].sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
        )
      );
      setShowForm(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Event konnte nicht erstellt werden."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function requestDelete(entryId: string) {
    setDeleteError(null);
    setPendingDeleteId(entryId);
  }

  function cancelDelete() {
    setPendingDeleteId(null);
    setDeleteError(null);
  }

  async function confirmDelete() {
    if (!pendingDeleteId) return;
    const entryId = pendingDeleteId;

    setDeletingId(entryId);
    setDeleteError(null);
    try {
      const res = await fetch(`${BASE_URL}/api/history/${entryId}/`, {
        method: "DELETE",
      });

      if (!res.ok && res.status !== 204) {
        throw new Error(`Error deleting entry: ${res.status}`);
      }

      setEntries((prev) => prev.filter((entry) => entry.id !== entryId));
      setPendingDeleteId(null);
    } catch (err) {
      setDeleteError(
        err instanceof Error ? err.message : "Event konnte nicht gelöscht werden."
      );
    } finally {
      setDeletingId(null);
    }
  }

  const pendingEntry = entries.find((entry) => entry.id === pendingDeleteId) ?? null;

  return (
    <div className={styles.panel}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.sectionLabel}>Clinical History</p>
          <h2 className={styles.sectionTitle}>Treatment Timeline</h2>
        </div>
        <div className={styles.headerActions}>
          <span className={styles.countBadge}>{entries.length} entries</span>
          {!showForm ? (
            <button
              type="button"
              className={styles.addButton}
              onClick={openForm}
            >
              + Add Event
            </button>
          ) : null}
        </div>
      </div>

      {showForm ? (
        <form className={styles.addEventForm} onSubmit={handleAddEvent}>
          {error ? <p className={styles.errorBanner}>{error}</p> : null}

          <div className={styles.inlineAddRow}>
            <input
              className={styles.input}
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Event name (e.g. Follow-up Visit)"
            />
            <input
              type="date"
              className={styles.input}
              value={newDate}
              max={todayISO()}
              onChange={(e) => setNewDate(e.target.value)}
            />
            <input
              className={styles.input}
              value={newDoctor}
              onChange={(e) => setNewDoctor(e.target.value)}
              placeholder="Doctor (e.g. Dr. Klein)"
            />
            <input
              className={styles.input}
              value={newDepartment}
              onChange={(e) => setNewDepartment(e.target.value)}
              placeholder="Department (e.g. Cardiology)"
            />
          </div>

          <textarea
            className={styles.textarea}
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Note (optional details about this event...)"
            rows={3}
          />

          <div className={styles.formActions}>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={closeForm}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.addButton}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      ) : null}

      <div className={styles.timeline}>
        {entries.length === 0 ? (
          <div className={styles.emptyState}>
            No history entries are available for this patient.
          </div>
        ) : (
          entries.map((entry) => (
            <article key={entry.id} className={styles.timelineItem}>
              <div className={styles.timelineRail}>
                <span className={styles.timelineDot} />
                <span className={styles.timelineLine} />
              </div>

              <div className={styles.timelineCard}>
                <div className={styles.timelineHeader}>
                  <div>
                    <p className={styles.timelineDate}>{entry.date}</p>
                    <h3 className={styles.timelineTitle}>{entry.title}</h3>
                  </div>
                  <div className={styles.timelineHeaderActions}>
                    <span className={styles.typeBadge}>{entry.category}</span>
                    <button
                      type="button"
                      className={styles.deleteButton}
                      onClick={() => requestDelete(entry.id)}
                      disabled={deletingId === entry.id}
                      aria-label="Delete event"
                    >
                      {deletingId === entry.id ? "..." : "Delete"}
                    </button>
                  </div>
                </div>

                <p className={styles.timelineText}>{entry.description}</p>

                <div className={styles.metaRow}>
                  <MetaChip label="Doctor" value={entry.doctor} />
                  <MetaChip label="Department" value={entry.department} />
                </div>

                <div className={styles.scanSection}>
                  <p className={styles.scanSectionLabel}>Linked Scans</p>
                  <ScanLinkList
                    scans={entry.scans}
                    patientId={patientId}
                    entryId={entry.id}
                  />
                </div>

                <AttachmentSection
                  attachments={entry.attachments}
                  patientId={patientId}
                  entryId={entry.id}
                  onScanUploaded={(scan) => handleScanUploaded(entry.id, scan)}
                />
              </div>
            </article>
          ))
        )}
      </div>

      {pendingDeleteId ? (
        <div className={styles.modalOverlay} onClick={cancelDelete}>
          <div
            className={styles.modalCard}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className={styles.modalTitle}>Delete timeline event?</h3>
            <p className={styles.modalText}>
              {pendingEntry
                ? `"${pendingEntry.title}" from ${pendingEntry.date} will be permanently deleted. This cannot be undone.`
                : "This event will be permanently deleted. This cannot be undone."}
            </p>
            {deleteError ? (
              <p className={styles.errorBanner}>{deleteError}</p>
            ) : null}
            <div className={styles.formActions}>
              <button
                type="button"
                className={styles.cancelButton}
                onClick={cancelDelete}
                disabled={deletingId === pendingDeleteId}
              >
                Cancel
              </button>
              <button
                type="button"
                className={styles.confirmDeleteButton}
                onClick={confirmDelete}
                disabled={deletingId === pendingDeleteId}
              >
                {deletingId === pendingDeleteId ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function MetaChip({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metaChip}>
      <span className={styles.metaChipLabel}>{label}</span>
      <span className={styles.metaChipValue}>{value}</span>
    </div>
  );
}