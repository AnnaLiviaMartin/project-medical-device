import styles from "./patientRecord.module.css";
import type { HistoryEntry } from "./patientRecord.data";
import ScanLinkList from "./ScanLinkList";

type PatientHistoryTimelineProps = {
  history: HistoryEntry[];
  patientId: string;
};

export default function PatientHistoryTimeline({
  history,
  patientId,
}: PatientHistoryTimelineProps) {
  return (
    <div className={styles.panel}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.sectionLabel}>Clinical History</p>
          <h2 className={styles.sectionTitle}>Treatment Timeline</h2>
        </div>
        <span className={styles.countBadge}>{history.length} entries</span>
      </div>

      <div className={styles.timeline}>
        {history.length === 0 ? (
          <div className={styles.emptyState}>
            No history entries are available for this patient.
          </div>
        ) : (
          history.map((entry) => (
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
                  <span className={styles.typeBadge}>{entry.category}</span>
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
              </div>
            </article>
          ))
        )}
      </div>
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