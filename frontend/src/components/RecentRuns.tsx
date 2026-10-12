import React from 'react';
import type { AuditRecord } from '../api/client';

interface RecentRunsProps {
  records: AuditRecord[];
  isLoading: boolean;
  errorMessage: string | null;
  onRefresh: () => void;
  onOpenAudit: (record: AuditRecord) => void;
}

function statusLabel(status: string) {
  if (status === 'READY') return { label: 'Ready for review', tone: 'success' };
  if (status === 'NEEDS_REVIEW') return { label: 'Review required', tone: 'warning' };
  if (status === 'BLOCKED') return { label: 'Blocked', tone: 'danger' };
  return { label: 'Recorded', tone: 'neutral' };
}

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function tablePair(reference: string) {
  const withoutPrefix = reference.replace(/^Migration\s+/i, '');
  const [source, destination] = withoutPrefix.split(/\s+->\s+/);
  return { source: source || withoutPrefix, destination: destination || '' };
}

export const RecentRuns: React.FC<RecentRunsProps> = ({
  records,
  isLoading,
  errorMessage,
  onRefresh,
  onOpenAudit,
}) => (
  <section className="product-panel product-history-panel" aria-labelledby="recent-heading">
    <div className="product-panel-heading">
      <div>
        <h2 id="recent-heading">Recent assessments</h2>
        <p>Review earlier mapping recommendations recorded by this service.</p>
      </div>
      <button className="product-button product-button-secondary" type="button" onClick={onRefresh} disabled={isLoading}>
        {isLoading ? 'Refreshing…' : 'Refresh list'}
      </button>
    </div>

    {errorMessage && <p className="product-history-error" role="status">{errorMessage}</p>}

    {isLoading && records.length === 0 ? (
      <div className="product-empty-inline" role="status">Loading recent assessments…</div>
    ) : records.length === 0 ? (
      <div className="product-empty-state">
        <h3>No assessments recorded yet</h3>
        <p>Completed mapping assessments will appear here while the service is running.</p>
        <p className="product-field-help">The current audit store is session-based and may clear when the service restarts.</p>
      </div>
    ) : (
      <div className="product-history-list">
        {records.map((record) => {
          const status = statusLabel(record.final_recommendation_status);
          const pair = tablePair(record.request_reference);
          const reviewCount = Number(record.major_outputs?.review_items_count ?? 0);
          const fieldsAnalyzed = Number(record.major_outputs?.fields_analyzed ?? 0);
          return (
            <article className="product-history-item" key={record.workflow_id}>
              <div className="product-history-main">
                <p className="product-history-pair">
                  <span>{pair.source}</span>
                  {pair.destination && <><span aria-hidden="true">→</span><span>{pair.destination}</span></>}
                </p>
                <p className="product-history-date">{formatTime(record.timestamp)}</p>
                <p className="product-history-meta">
                  {fieldsAnalyzed > 0 ? `${fieldsAnalyzed} destination fields checked` : 'Assessment details recorded'}
                  {reviewCount > 0 ? ` · ${reviewCount} item${reviewCount === 1 ? '' : 's'} need review` : ''}
                </p>
              </div>
              <div className="product-history-actions">
                <span className={`product-status product-status-${status.tone}`}>{status.label}</span>
                <button className="product-button product-button-secondary" type="button" onClick={() => onOpenAudit(record)}>
                  Open audit details
                </button>
              </div>
            </article>
          );
        })}
      </div>
    )}
  </section>
);
