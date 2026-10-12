import React, { useState } from 'react';
import type { FieldRecommendation, WorkflowContext } from '../api/client';

interface BusinessRecommendationProps {
  workflowContext: WorkflowContext;
  onStartAnother: () => void;
  onOpenTechnicalDetails?: () => void;
}

const decisionLabels: Record<FieldRecommendation['decision'], string> = {
  DIRECT_MAP: 'Direct match',
  TRANSFORM: 'Data conversion',
  DEFAULT: 'Use default',
  UNMAPPED: 'No source match',
  REVIEW: 'Review required',
};

const decisionDescriptions: Record<FieldRecommendation['decision'], string> = {
  DIRECT_MAP: 'A source field can map directly to this destination field.',
  TRANSFORM: 'A data conversion is recommended before this value is used.',
  DEFAULT: 'A default value is recommended for this destination field.',
  UNMAPPED: 'No matching source field was identified.',
  REVIEW: 'An analyst needs to resolve this field before using the plan.',
};

function statusPresentation(status: string) {
  if (status === 'READY') {
    return {
      label: 'Ready for analyst review',
      tone: 'success',
      next: 'Review the field matches and proposed data changes before using this plan in a migration.',
    };
  }
  if (status === 'NEEDS_REVIEW') {
    return {
      label: 'Analyst review required',
      tone: 'warning',
      next: 'Resolve the flagged fields or relationship details, then run the assessment again.',
    };
  }
  return {
    label: 'Resolve blockers',
    tone: 'danger',
    next: 'Correct the blocking schema or relationship issues, then run the assessment again.',
  };
}

function csvValue(value: unknown) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`;
}

function readableChange(value: string) {
  return value
    .replaceAll('_', ' ')
    .replace(/\btype cast\b/gi, 'data type conversion')
    .replace(/\bdate format\b/gi, 'date formatting')
    .toLowerCase();
}

function businessSummary(context: WorkflowContext) {
  const recommendation = context.final_recommendation;
  if (!recommendation) return '';

  const total = recommendation.field_recommendations.length;
  const reviewCount = recommendation.summary_counts.REVIEW;

  if (recommendation.overall_status === 'READY') {
    return `The assessment prepared recommendations for all ${total} destination fields. Review the suggested matches and any proposed data changes before using the plan.`;
  }
  if (recommendation.overall_status === 'NEEDS_REVIEW') {
    return `The assessment flagged ${reviewCount} ${reviewCount === 1 ? 'field' : 'fields'} for analyst review. Confirm the required source data and record relationships before using the plan.`;
  }
  return 'The assessment found required data or relationship gaps. Resolve the issues listed below before using the plan.';
}

function readableRuleCitation(citation: { rule_id: string; description: string }) {
  const ruleId = citation.rule_id.toUpperCase();
  if (ruleId.includes('RULE_1')) {
    return {
      title: 'Matching field names',
      description: 'The source and destination field names match, and their data types are compatible.',
    };
  }
  if (ruleId.includes('RULE_2')) {
    return {
      title: 'Recognized CRM field name',
      description: 'A recognized alternate field name matches the destination, and the data types are compatible.',
    };
  }
  if (ruleId.includes('RULE_3')) {
    return {
      title: 'Suggested data conversion',
      description: 'A data conversion is proposed to make the source value fit the destination field.',
    };
  }
  if (ruleId.includes('RULE_4')) {
    return {
      title: 'Required destination information',
      description: 'A required destination field needs a source value or an approved default.',
    };
  }
  if (ruleId.includes('RULE_5')) {
    return {
      title: 'Record relationship needs confirmation',
      description: 'A required link between CRM records could not be confirmed from the supplied schema.',
    };
  }
  return {
    title: 'Assessment evidence',
    description: 'A field mapping check contributed to this recommendation.',
  };
}

function readableConcern(value: string) {
  if (/mandatory relational link|required.*relationship|foreign key/i.test(value)) {
    return 'A required relationship between records needs confirmation. Identify the source field that links these records before using the plan.';
  }
  if (/mandatory target field|required target field|no mapped source field|no source match/i.test(value)) {
    const fieldName = value.match(/(?:target field|destination field) ['"]?([^'"\s:]+)['"]?/i)?.[1];
    return `A required destination field${fieldName ? `, ${fieldName},` : ''} has no matching source value or approved default. Supply the value or define an approved default before proceeding.`;
  }
  const unmapped = value.match(/unmapped source fields?:\s*(.+?)(?:\s+exist|\s+have|$)/i)?.[1];
  if (unmapped) {
    return `These source fields have no destination match: ${unmapped}. Confirm whether they can be omitted or need a destination field.`;
  }
  return value
    .replace(/deterministic match verified/gi, 'field match confirmed')
    .replace(/deterministic/gi, 'automated')
    .replace(/normalized column name/gi, 'field name')
    .replace(/foreign key/gi, 'record relationship')
    .replace(/schema default/gi, 'destination default value')
    .replace(/target field/gi, 'destination field');
}

function readableChangeDetails(details: string, fieldName: string) {
  const defaultValue = details.match(/schema default:\s*['"]?([^.'"]+)['"]?/i)?.[1];
  if (defaultValue) {
    return `Fill ${fieldName} with the destination default value “${defaultValue}”.`;
  }
  return details
    .replace(/populate target field/gi, 'Fill the destination field')
    .replace(/no transformation applicable \(unmapped target field\)/gi, 'No data change is proposed for this field.')
    .replace(/schema default/gi, 'destination default value')
    .replace(/type cast/gi, 'data type conversion')
    .replace(/\btarget field\b/gi, 'destination field');
}

function readableFieldEvidence(field: FieldRecommendation) {
  const evidence = field.evidence;
  if (field.rule_id.includes('RULE_1') && field.source_field) {
    const type = evidence.match(/compatible type ['"]([^'"]+)['"]/i)?.[1];
    return `The source and destination field names match${type ? `, and their ${type} data types are compatible` : ' and their data types are compatible'}.`;
  }
  if (field.rule_id.includes('RULE_2') && field.source_field) {
    return `The source field ${field.source_field} is a recognized alternate name for ${field.destination_field}, with a compatible data type.`;
  }
  if (field.decision === 'DEFAULT') {
    const defaultValue = evidence.match(/schema default:\s*['"]?([^.'"]+)['"]?/i)?.[1];
    return defaultValue ? `The destination default value ${defaultValue} is recommended.` : 'The destination default value is recommended.';
  }
  if (field.decision === 'REVIEW') return readableConcern(evidence);
  return evidence
    .replace(/deterministic match verified/gi, 'field match confirmed')
    .replace(/exact normalized name match/gi, 'matching field names')
    .replace(/compatible type/gi, 'compatible data type');
}

function downloadWorksheet(context: WorkflowContext) {
  const recommendation = context.final_recommendation;
  if (!recommendation) return;

  const rows = [
    ['Destination field', 'Source field', 'Recommendation', 'Confidence', 'Evidence', 'Proposed change', 'Needs analyst review'],
    ...recommendation.field_recommendations.map((field) => [
      field.destination_field,
      field.source_field ?? '',
      decisionLabels[field.decision] ?? field.decision,
      `${Math.round(field.confidence_score)}%`,
      field.evidence,
      field.transformation ?? '',
      field.requires_human_review ? 'Yes' : 'No',
    ]),
  ];
  const csv = `\uFEFF${rows.map((row) => row.map(csvValue).join(',')).join('\r\n')}`;
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  const safeId = context.workflow_id.replace(/[^a-zA-Z0-9_-]/g, '-');
  link.href = url;
  link.download = `mapping-worksheet-${safeId}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

export const BusinessRecommendation: React.FC<BusinessRecommendationProps> = ({
  workflowContext,
  onStartAnother,
  onOpenTechnicalDetails,
}) => {
  const [downloadMessage, setDownloadMessage] = useState('');
  const recommendation = workflowContext.final_recommendation;
  if (!recommendation) return null;

  const status = statusPresentation(recommendation.overall_status);
  const summary = businessSummary(workflowContext);
  const counts = recommendation.summary_counts;
  const unresolvedSourceCount = recommendation.field_recommendations.filter(
    (field) => !field.source_field && field.decision !== 'DEFAULT',
  ).length;
  const activeChanges = (workflowContext.transformation_plan ?? []).filter(
    (item) => !['NO_OP', 'NONE'].includes(item.action_type.toUpperCase()),
  );
  const validation = workflowContext.validation_results;

  const handleDownload = () => {
    downloadWorksheet(workflowContext);
    setDownloadMessage('Mapping worksheet downloaded.');
  };

  return (
    <section className="product-result" id="section-mapping-table" aria-labelledby="recommendation-heading">
      <div className="product-result-heading">
        <div>
          <p className="product-kicker">Assessment result</p>
          <h2 id="recommendation-heading">Mapping recommendation</h2>
          <p className="product-result-summary">{summary}</p>
        </div>
        <span className={`product-status product-status-${status.tone}`}>
          <span className="product-status-dot" aria-hidden="true" />
          {status.label}
        </span>
      </div>

      <div className="product-result-overview">
        <section className={`product-next-step product-next-step-${status.tone}`} aria-labelledby="next-step-heading">
          <div>
            <h3 id="next-step-heading">Recommended next step</h3>
            <p>{status.next}</p>
            <p className="product-boundary-note">This plan supports review. It does not change CRM records or run a migration.</p>
          </div>
          <div className="product-result-actions">
            <button className="product-button product-button-primary" type="button" onClick={handleDownload}>
              Download mapping worksheet
            </button>
            <button className="product-button product-button-secondary" type="button" onClick={onStartAnother}>
              Start another assessment
            </button>
            {onOpenTechnicalDetails && (
              <button
                className="product-button product-button-secondary product-button-technical"
                type="button"
                onClick={onOpenTechnicalDetails}
                title="Open the Explainability & Audit drawer to inspect the 10-node LangGraph trace, routing, and telemetry"
              >
                🔬 Explainability &amp; Audit
              </button>
            )}
            {downloadMessage && <span className="product-download-status" role="status">{downloadMessage}</span>}
          </div>
        </section>

        <section className="product-counts" aria-label="Mapping summary">
          <div className="product-counts-heading">
            <h3>Field summary</h3>
            <span>{recommendation.field_recommendations.length} destination fields</span>
          </div>
          <dl className="product-count-grid">
            <div><dt>Direct match</dt><dd>{counts.DIRECT_MAP}</dd></div>
            <div><dt>Data conversion</dt><dd>{counts.TRANSFORM}</dd></div>
            <div><dt>Default</dt><dd>{counts.DEFAULT}</dd></div>
            <div><dt>Analyst review</dt><dd>{counts.REVIEW}</dd></div>
            <div><dt>No source match</dt><dd>{unresolvedSourceCount}</dd></div>
          </dl>
        </section>
      </div>

      <section className="product-why" aria-labelledby="why-heading">
        <div>
          <h3 id="why-heading">Why this recommendation</h3>
          <p>{summary}</p>
        </div>
        {workflowContext.explanation?.rule_citations?.length ? (
          <ul className="product-evidence-list">
            {workflowContext.explanation.rule_citations.map((citation) => (
              (() => {
                const readable = readableRuleCitation(citation);
                return (
                  <li key={citation.rule_id}>
                    <strong>{readable.title}</strong>
                    <span>{readable.description}</span>
                  </li>
                );
              })()
            ))}
          </ul>
        ) : null}
        {workflowContext.explanation?.limitations_or_warnings?.length ? (
          <div className="product-caution">
            <strong>Limitations to keep in mind</strong>
            <ul>
              {workflowContext.explanation.limitations_or_warnings.map((warning, index) => (
                <li key={`${index}-${warning}`}>{readableConcern(warning)}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      {recommendation.review_items.length > 0 && (
        <section className="product-review-items" aria-labelledby="review-items-heading">
          <div>
            <h3 id="review-items-heading">Items that need attention</h3>
            <p>Resolve these before relying on the mapping plan.</p>
          </div>
          <ul>
            {recommendation.review_items.map((item, index) => <li key={`${index}-${item}`}>{readableConcern(item)}</li>)}
          </ul>
        </section>
      )}

      <section className="product-panel product-mapping-panel" aria-labelledby="field-mappings-heading">
        <div className="product-panel-heading">
          <div>
            <h3 id="field-mappings-heading">Field-by-field evidence</h3>
            <p>Review each suggested source, destination, confidence, and reason.</p>
          </div>
          <span className="product-soft-label">{recommendation.field_recommendations.length} fields assessed</span>
        </div>
        <div className="product-table-wrap" role="region" aria-label="Field mapping recommendations" tabIndex={0}>
          <table className="product-table">
            <thead>
              <tr>
                <th scope="col">Destination field</th>
                <th scope="col">Source field</th>
                <th scope="col">Recommendation</th>
                <th scope="col">Confidence</th>
                <th scope="col">Evidence and notes</th>
              </tr>
            </thead>
            <tbody>
              {recommendation.field_recommendations.map((field) => (
                <tr key={field.destination_field} className={field.requires_human_review ? 'product-row-review' : undefined}>
                  <th scope="row">{field.destination_field}</th>
                  <td>{field.source_field || <span className="product-muted">No source match</span>}</td>
                  <td>
                    <span className={`product-decision product-decision-${field.decision.toLowerCase()}`}>
                      {decisionLabels[field.decision] ?? field.decision}
                    </span>
                    <span className="product-cell-help">{decisionDescriptions[field.decision]}</span>
                  </td>
                  <td>
                    <div className="product-confidence">
                      <span>{Math.round(field.confidence_score)}%</span>
                      <span className="product-confidence-track" aria-hidden="true">
                        <span style={{ width: `${Math.max(0, Math.min(100, field.confidence_score))}%` }} />
                      </span>
                    </div>
                  </td>
                  <td>
                    <span>{readableFieldEvidence(field)}</span>
                    {field.transformation && <span className="product-cell-help">Proposed change: {readableChange(field.transformation)}</span>}
                    {field.validation_notes && <span className="product-cell-help">Validation: {readableConcern(field.validation_notes)}</span>}
                    {field.requires_human_review && <span className="product-review-flag">Analyst review required</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="product-detail-grid">
        <section className="product-panel product-detail-panel" aria-labelledby="changes-heading">
          <div className="product-panel-heading">
            <div>
              <h3 id="changes-heading">Recommended data changes</h3>
              <p>Conversions and default values to review.</p>
            </div>
            <span className="product-soft-label">{activeChanges.length} proposed</span>
          </div>
          {activeChanges.length === 0 ? (
            <p className="product-empty-inline">No conversions or default values were proposed for this schema pair.</p>
          ) : (
            <ul className="product-change-list">
              {activeChanges.map((item) => (
                <li key={`${item.destination_field}-${item.action_type}`}>
                  <div className="product-change-title">
                    <strong>{item.destination_field}</strong>
                    <span>{item.action_type === 'TYPE_CAST' ? 'Convert data type' : item.action_type === 'DEFAULT_VALUE' ? 'Use default value' : readableChange(item.action_type)}</span>
                  </div>
                  {item.source_field && <p className="product-change-source">From {item.source_field}</p>}
                  <p>{readableChangeDetails(item.details, item.destination_field)}</p>
                  {(item.sample_before !== undefined || item.sample_after !== undefined) && (
                    <div className="product-sample-pair">
                      <div><span>Current example</span><code>{item.sample_before === null ? 'null' : String(item.sample_before ?? '—')}</code></div>
                      <div><span>Example after change</span><code>{item.sample_after === null ? 'null' : String(item.sample_after ?? '—')}</code></div>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="product-panel product-detail-panel" aria-labelledby="validation-heading">
          <div className="product-panel-heading">
            <div>
              <h3 id="validation-heading">Validation checks</h3>
              <p>Required fields, compatible types, and relationships.</p>
            </div>
            {validation && (
              <span className={`product-status product-status-${validation.all_valid ? 'success' : 'danger'}`}>
                {validation.all_valid ? 'Checks passed' : 'Issues found'}
              </span>
            )}
          </div>
          {!validation ? (
            <p className="product-empty-inline">No validation summary is available for this assessment.</p>
          ) : (
            <>
              {validation.blocking_issues.length > 0 && (
                <div className="product-validation-group product-validation-blocking">
                  <strong>Blocking issues</strong>
                  <ul>{validation.blocking_issues.map((issue, index) => <li key={`${index}-${issue}`}>{readableConcern(issue)}</li>)}</ul>
                </div>
              )}
              {validation.warning_issues.length > 0 && (
                <div className="product-validation-group product-validation-warning">
                  <strong>Warnings</strong>
                  <ul>{validation.warning_issues.map((issue, index) => <li key={`${index}-${issue}`}>{readableConcern(issue)}</li>)}</ul>
                </div>
              )}
              <ul className="product-check-list">
                {validation.items.map((item, index) => (
                  <li key={`${item.field_name}-${index}`}>
                    <span className={`product-check-symbol product-check-${item.status.toLowerCase()}`} aria-hidden="true">
                      {item.status === 'PASS' ? '✓' : item.status === 'FAIL' ? '!' : '•'}
                    </span>
                    <div><strong>{item.field_name}</strong><span>{readableConcern(item.message)}</span></div>
                    <span className="product-check-status">{item.status === 'PASS' ? 'Passed' : item.status === 'FAIL' ? 'Failed' : 'Warning'}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>
    </section>
  );
};
