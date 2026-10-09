import React from 'react';
import type { MigrationRecommendation } from '../api/client';

interface MappingTableProps {
  recommendation: MigrationRecommendation | null;
  workflowId: string;
}

export const MappingTable: React.FC<MappingTableProps> = ({
  recommendation,
  workflowId,
}) => {
  if (!recommendation) {
    return (
      <div id="section-mapping-table" className="card mb-6">
        <div className="card-header">
          <h2 className="text-lg font-bold text-gray-800">5. Decision Agent: Field Mapping Recommendations</h2>
          <p className="text-sm text-gray-500">Awaiting workflow execution.</p>
        </div>
        <div className="card-body text-center py-8 text-gray-400">
          Run the migration pipeline to view per-field mapping decisions produced by the Migration Decision Agent.
        </div>
      </div>
    );
  }

  const { overall_status, summary_counts, field_recommendations, review_items, triggered_rules } =
    recommendation;

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'DIRECT_MAP':
        return <span className="badge badge-success font-bold">DIRECT_MAP</span>;
      case 'TRANSFORM':
        return <span className="badge badge-info font-bold">TRANSFORM</span>;
      case 'DEFAULT':
        return <span className="badge badge-purple font-bold">DEFAULT</span>;
      case 'REVIEW':
        return <span className="badge badge-error font-bold">REVIEW</span>;
      case 'UNMAPPED':
        return <span className="badge badge-neutral font-bold">UNMAPPED</span>;
      default:
        return <span className="badge">{decision}</span>;
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'bg-emerald-500';
    if (score >= 70) return 'bg-blue-500';
    if (score >= 50) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div id="section-mapping-table" className="card mb-6 border-slate-200 shadow-sm">
      <div className="card-header flex-between flex-wrap gap-2">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <span className="badge badge-primary font-mono text-2xs uppercase">Product Bible §6 & §13</span>
            <h2 className="text-lg font-bold text-gray-800">5. Decision Agent: Per-Field Recommendations</h2>
            <span
              className={`badge font-bold px-2.5 py-1 text-xs ${
                overall_status === 'READY'
                  ? 'badge-success'
                  : overall_status === 'NEEDS_REVIEW'
                  ? 'badge-warning'
                  : 'badge-error'
              }`}
            >
              FINAL DECISION: {overall_status}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1 font-mono">
            Synthesized by <strong>Migration Decision Agent</strong> • Workflow Run: {workflowId}
          </p>
        </div>

        {/* Counter Pills */}
        <div className="flex flex-wrap gap-1.5 text-xs font-semibold">
          <span className="stat-pill stat-pill-green">
            Direct: {summary_counts.DIRECT_MAP}
          </span>
          <span className="stat-pill stat-pill-blue">
            Transform: {summary_counts.TRANSFORM}
          </span>
          <span className="stat-pill stat-pill-purple">
            Default: {summary_counts.DEFAULT}
          </span>
          <span className="stat-pill stat-pill-red">
            Review: {summary_counts.REVIEW}
          </span>
          <span className="stat-pill stat-pill-gray">
            Unmapped: {summary_counts.UNMAPPED}
          </span>
        </div>
      </div>

      {/* Triggered Rules Banner */}
      <div className="px-5 py-2.5 bg-slate-50 border-b border-slate-200 flex-between flex-wrap gap-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">⚖️ Triggered Deterministic Rules:</span>
          <div className="flex flex-wrap gap-1">
            {triggered_rules.map((rule) => (
              <span key={rule} className="font-mono text-3xs px-2 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded font-semibold">
                {rule}
              </span>
            ))}
          </div>
        </div>
        <span className="text-2xs text-slate-500">
          Applied by Migration Decision Agent
        </span>
      </div>

      {review_items && review_items.length > 0 && (
        <div className="mx-4 mt-3 p-3 bg-amber-50 border-l-4 border-amber-500 rounded-r text-xs text-amber-900">
          <strong className="block mb-1 text-amber-800">⚠️ Flagged Items Requiring Human Review (Rules 4 & 5):</strong>
          <ul className="list-disc pl-4 space-y-0.5">
            {review_items.map((item, idx) => (
              <li key={idx} className="font-medium">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card-body p-0">
        <div className="table-responsive">
          <table className="mapping-table">
            <thead>
              <tr>
                <th style={{ width: '22%' }}>Target Destination Field</th>
                <th style={{ width: '22%' }}>Mapped Source Field</th>
                <th style={{ width: '14%' }}>Decision</th>
                <th style={{ width: '14%' }}>Confidence</th>
                <th style={{ width: '28%' }}>Deterministic Rule & Evidence</th>
              </tr>
            </thead>
            <tbody>
              {field_recommendations.map((rec) => (
                <tr
                  key={rec.destination_field}
                  className={rec.requires_human_review ? 'row-review-flagged' : ''}
                >
                  <td className="font-bold text-gray-900 font-mono text-xs">
                    {rec.destination_field}
                  </td>
                  <td className="font-mono text-xs">
                    {rec.source_field ? (
                      <span className="text-indigo-600 font-semibold">{rec.source_field}</span>
                    ) : (
                      <span className="text-gray-400 italic">None (Unmapped)</span>
                    )}
                  </td>
                  <td>{getDecisionBadge(rec.decision)}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="confidence-meter-bg">
                        <div
                          className={`confidence-meter-fill ${getConfidenceColor(
                            rec.confidence_score
                          )}`}
                          style={{ width: `${rec.confidence_score}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-bold text-gray-700">
                        {rec.confidence_score}%
                      </span>
                    </div>
                  </td>
                  <td className="text-xs">
                    <div className="text-gray-800 leading-snug">{rec.evidence}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="badge badge-neutral text-3xs font-mono">
                        Rule: {rec.rule_id}
                      </span>
                      {rec.transformation && (
                        <span className="badge badge-info text-3xs font-mono">
                          Transform: {rec.transformation}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
