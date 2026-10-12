import React from 'react';
import type { AuditRecord, Explanation } from '../api/client';

interface AuditTrailPanelProps {
  currentAudit: AuditRecord | null;
  historicalAudits: AuditRecord[];
  explanation: Explanation | null;
  onRefreshAudits: () => void;
}

export const AuditTrailPanel: React.FC<AuditTrailPanelProps> = ({
  currentAudit,
  historicalAudits,
  explanation,
  onRefreshAudits,
}) => {
  return (
    <div className="card">
      <div className="card-header flex-between">
        <div>
          <h2 className="text-lg font-bold text-gray-800">6. Audit Trail & Explainability</h2>
          <p className="text-sm text-gray-500">
            Immutable run-scoped audit log & rule explanations (Product Bible §15 & §16).
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary text-xs"
          onClick={onRefreshAudits}
        >
          ↻ Refresh Audit Store
        </button>
      </div>

      <div className="card-body">
        {/* Explanation Narrative */}
        {explanation && (
          <div className="mb-4 p-3 bg-slate-50 border border-slate-200 rounded">
            <h4 className="font-bold text-xs text-slate-800 uppercase mb-1">
              💬 Explanation & Rule Citations
            </h4>
            <p className="text-xs text-slate-700 mb-2 leading-relaxed font-medium">
              {explanation.summary}
            </p>

            <div className="grid grid-2 gap-2 mt-2">
              {explanation.rule_citations.map((rc) => (
                <div key={rc.rule_id} className="p-2 bg-white rounded border border-slate-200 text-xs">
                  <div className="flex-between font-bold text-slate-900 mb-0.5">
                    <span>{rc.rule_name}</span>
                    <span className="text-emerald-700">{rc.confidence}</span>
                  </div>
                  <p className="text-slate-600 text-2xs leading-snug">{rc.description}</p>
                </div>
              ))}
            </div>

            {explanation.limitations_or_warnings.length > 0 && (
              <div className="mt-3 text-2xs text-amber-800 bg-amber-50 p-2 rounded border border-amber-200">
                <strong>Limitations / Warnings Noted:</strong>
                <ul className="list-disc pl-4 mt-0.5">
                  {explanation.limitations_or_warnings.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Current Run Audit Card */}
        {currentAudit ? (
          <div className="audit-card mb-4 bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs shadow">
            <div className="flex-between mb-2 text-indigo-300 font-bold border-b border-slate-800 pb-2">
              <span>WORKFLOW ID: {currentAudit.workflow_id}</span>
              <span
                className={`px-2 py-0.5 rounded text-2xs ${
                  currentAudit.final_recommendation_status === 'READY'
                    ? 'bg-emerald-900 text-emerald-300'
                    : 'bg-amber-900 text-amber-300'
                }`}
              >
                {currentAudit.final_recommendation_status}
              </span>
            </div>

            <div className="grid grid-2 gap-3 text-2xs text-slate-300">
              <div>
                <span className="technical-dark-label block">Execution Timestamp:</span>
                <span>{currentAudit.timestamp}</span>
              </div>
              <div>
                <span className="technical-dark-label block">Request Reference:</span>
                <span>{currentAudit.request_reference}</span>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800 text-2xs">
              <span className="technical-dark-label block mb-1">Agent Sequence:</span>
              <div className="flex flex-wrap gap-1">
                {currentAudit.agent_execution_order.map((agent, i) => (
                  <span
                    key={i}
                    className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700"
                  >
                    {i + 1}. {agent}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800 text-2xs">
              <span className="technical-dark-label block mb-1">Triggered Decision Rules:</span>
              <div className="flex flex-wrap gap-1">
                {currentAudit.triggered_rules.map((rule, i) => (
                  <span
                    key={i}
                    className="bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded border border-indigo-800"
                  >
                    {rule}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-gray-400 text-xs">
            Run a migration to record an audit trace.
          </div>
        )}

        {/* Historical Runs in Memory */}
        {historicalAudits.length > 0 && (
          <div>
            <h4 className="font-bold text-xs text-gray-700 mb-2">
              In-Memory Audit Store History ({historicalAudits.length} runs)
            </h4>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {historicalAudits.map((rec) => (
                <div
                  key={rec.workflow_id}
                  className="flex-between p-2 rounded border border-gray-200 bg-white text-xs hover:bg-gray-50"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-gray-800 font-semibold text-2xs">
                      {rec.workflow_id}
                    </span>
                    <span className="text-gray-500 text-2xs">{rec.request_reference}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 text-2xs">
                      {new Date(rec.timestamp).toLocaleTimeString()}
                    </span>
                    <span
                      className={`badge text-2xs ${
                        rec.final_recommendation_status === 'READY'
                          ? 'badge-success'
                          : 'badge-warning'
                      }`}
                    >
                      {rec.final_recommendation_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
