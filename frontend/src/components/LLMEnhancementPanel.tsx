import React from 'react';
import type { LLMEnhancementOutput, LLMTelemetry } from '../api/client';

interface LLMEnhancementPanelProps {
  llmEnhancement?: LLMEnhancementOutput;
  llmTelemetry?: LLMTelemetry;
}

export const LLMEnhancementPanel: React.FC<LLMEnhancementPanelProps> = ({
  llmEnhancement,
  llmTelemetry,
}) => {
  if (!llmEnhancement && !llmTelemetry) {
    return (
      <div id="section-llm-enhancement" className="card mb-6">
        <div className="card-header">
          <h2 className="text-lg font-bold text-gray-800">5. Controlled LLM Enhancement</h2>
          <p className="text-sm text-gray-500">
            Product Bible §21 • Semantic transformation rationales & executive migration narrative.
          </p>
        </div>
        <div className="card-body text-center py-6 text-gray-400">
          Awaiting workflow execution to display LLM explanation and telemetry.
        </div>
      </div>
    );
  }

  const isSuccess = llmTelemetry?.status === 'SUCCESS';
  const isFallback = llmTelemetry?.fallback_used;

  return (
    <div id="section-llm-enhancement" className="card mb-6 border-indigo-200 shadow-sm">
      <div className="card-header flex-between flex-wrap gap-2 bg-gradient-to-r from-indigo-50/50 to-purple-50/40">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge badge-primary font-mono text-2xs uppercase">
              Phase 2.3 • Product Bible §21
            </span>
            <h2 className="text-lg font-bold text-gray-800">
              5. Controlled LLM Enhancement & Migration Explainer
            </h2>
          </div>
          <p className="text-sm text-gray-500">
            Bounded semantic explanation layer with guaranteed deterministic fallback. Business authority remains 100% deterministic.
          </p>
        </div>

        {/* Telemetry Status Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          {llmTelemetry && (
            <>
              <span className="badge badge-secondary text-xs font-mono font-semibold">
                {llmTelemetry.provider.toUpperCase()}: {llmTelemetry.model}
              </span>
              <span
                className={`badge text-xs font-semibold ${
                  isSuccess
                    ? 'badge-success'
                    : isFallback
                    ? 'badge-warning'
                    : 'badge-secondary'
                }`}
              >
                Status: {llmTelemetry.status}
              </span>
              {llmTelemetry.latency_ms > 0 && (
                <span className="badge badge-neutral text-xs font-mono">
                  {llmTelemetry.latency_ms.toFixed(0)}ms
                </span>
              )}
              {isFallback && (
                <span className="badge badge-warning text-xs font-bold animate-pulse">
                  FALLBACK ACTIVE
                </span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="card-body space-y-5">
        {/* Fallback Notice Banner if Fallback Used */}
        {isFallback && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-900 flex items-start gap-2.5">
            <span className="text-amber-600 font-bold text-base">🛡️</span>
            <div>
              <span className="font-semibold">Deterministic Fallback Engaged: </span>
              {llmTelemetry?.error_message || 'LLM unavailable or output unverified.'}
              <span className="block text-xs text-amber-700 mt-0.5">
                The migration pipeline automatically reverted to deterministic template reasoning. Deterministic mapping authority remains 100% safe and unaffected.
              </span>
            </div>
          </div>
        )}

        {/* Executive Migration Narrative */}
        {llmEnhancement?.executive_summary && (
          <div>
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-500 mb-1.5 flex items-center gap-1.5">
              <span>📝</span> Executive Migration Summary
            </h3>
            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 leading-relaxed font-sans shadow-2xs">
              {llmEnhancement.executive_summary}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Risk Assessment */}
          {llmEnhancement?.risk_assessment && (
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-500 mb-1.5 flex items-center gap-1.5">
                <span>⚠️</span> Migration Risk Assessment
              </h3>
              <div
                className={`p-3 rounded-lg border text-sm font-medium ${
                  llmEnhancement.risk_assessment.toUpperCase().includes('HIGH')
                    ? 'bg-rose-50 border-rose-200 text-rose-900'
                    : llmEnhancement.risk_assessment.toUpperCase().includes('MODERATE')
                    ? 'bg-amber-50 border-amber-200 text-amber-900'
                    : 'bg-emerald-50 border-emerald-200 text-emerald-900'
                }`}
              >
                {llmEnhancement.risk_assessment}
              </div>
            </div>
          )}

          {/* Actionable Triage Steps */}
          <div>
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-500 mb-1.5 flex items-center gap-1.5">
              <span>🔍</span> Analyst Review Triage Actions
            </h3>
            {llmEnhancement?.suggested_review_actions &&
            llmEnhancement.suggested_review_actions.length > 0 ? (
              <ul className="space-y-1.5">
                {llmEnhancement.suggested_review_actions.map((act, idx) => (
                  <li
                    key={idx}
                    className="p-2.5 bg-slate-50 border border-slate-200 rounded text-xs text-slate-700 flex items-start gap-2"
                  >
                    <span className="text-indigo-600 font-bold">•</span>
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-3 bg-emerald-50/60 border border-emerald-200 rounded text-xs text-emerald-800 flex items-center gap-2">
                <span>✓</span> Zero analyst intervention required. All fields ready for automated ingestion.
              </div>
            )}
          </div>
        </div>

        {/* Technical Transformation Rationales */}
        {llmEnhancement?.transformation_rationales &&
          Object.keys(llmEnhancement.transformation_rationales).length > 0 && (
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-500 mb-1.5 flex items-center gap-1.5">
                <span>⚙️</span> Technical Transformation Rationales (Rule 3 Explanations)
              </h3>
              <div className="space-y-2">
                {Object.entries(llmEnhancement.transformation_rationales).map(
                  ([field, rationale]) => (
                    <div
                      key={field}
                      className="p-3 bg-blue-50/50 border border-blue-200 rounded-lg flex items-start justify-between gap-3 text-xs"
                    >
                      <span className="font-mono font-bold text-blue-900 bg-blue-100 px-2 py-0.5 rounded shrink-0">
                        {field}
                      </span>
                      <p className="text-blue-950 flex-1 leading-relaxed">{rationale}</p>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

        {/* Telemetry Trace Audit Bar */}
        {llmTelemetry && (
          <div className="pt-2 border-t border-slate-100 flex-between items-center text-2xs text-gray-400 font-mono flex-wrap gap-2">
            <div>
              Telemetry: Provider={llmTelemetry.provider} | Model={llmTelemetry.model} | Validated={String(llmTelemetry.validation_passed)} | Fallback={String(llmTelemetry.fallback_used)}
            </div>
            <div>
              Protected: Zero secrets in source or traces
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
