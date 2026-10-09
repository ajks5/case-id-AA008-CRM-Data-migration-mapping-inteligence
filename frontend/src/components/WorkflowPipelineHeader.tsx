import React from 'react';
import type { WorkflowContext } from '../api/client';

interface WorkflowPipelineHeaderProps {
  workflowContext: WorkflowContext | null;
  activeView: 'full' | 'context' | 'mapping';
  onViewChange: (view: 'full' | 'context' | 'mapping') => void;
  onScrollToSection: (sectionId: string) => void;
}

export const WorkflowPipelineHeader: React.FC<WorkflowPipelineHeaderProps> = ({
  workflowContext,
  activeView,
  onViewChange,
  onScrollToSection,
}) => {
  const isExecuted = !!workflowContext;
  const agentCount = workflowContext?.agent_outputs?.length || 0;
  const selectedRoute = workflowContext?.selected_route;
  const routingStatus = workflowContext?.routing_status;
  const overallStatus = workflowContext?.final_recommendation?.overall_status;

  const pipelineSteps = [
    {
      id: 'step-input',
      title: '1. Business Input',
      subtitle: 'Source & Destination Schemas',
      status: isExecuted ? 'COMPLETED' : 'READY',
      targetId: 'section-schema-selector',
    },
    {
      id: 'step-builder',
      title: '2. Context Builder',
      subtitle: 'Normalizes & Initializes Context',
      status: isExecuted ? 'COMPLETED' : 'WAITING',
      targetId: 'section-shared-context',
    },
    {
      id: 'step-context',
      title: '3. Shared Context',
      subtitle: 'Run-Scoped Workflow Context',
      status: isExecuted ? 'ACTIVE' : 'WAITING',
      targetId: 'section-shared-context',
    },
    {
      id: 'step-agents',
      title: '4. Domain Agents (1–5)',
      subtitle: `${agentCount}/5 Agents Executed`,
      status: agentCount === 5 ? 'COMPLETED' : isExecuted ? 'RUNNING' : 'WAITING',
      targetId: 'section-agent-timeline',
    },
    {
      id: 'step-rules',
      title: '5. Deterministic Rules',
      subtitle: 'Rules 1–5 Evaluated',
      status: isExecuted ? 'COMPLETED' : 'WAITING',
      targetId: 'section-mapping-table',
    },
    {
      id: 'step-decision',
      title: '6. Decision Agent',
      subtitle: overallStatus || 'Awaiting Decision',
      status: overallStatus ? 'COMPLETED' : 'WAITING',
      targetId: 'section-mapping-table',
    },
    {
      id: 'step-route',
      title: '7. LangGraph Route',
      subtitle: selectedRoute ? `${selectedRoute} (${routingStatus})` : 'Branch Evaluation',
      status: selectedRoute ? 'COMPLETED' : 'WAITING',
      targetId: 'section-agent-timeline',
    },
    {
      id: 'step-llm',
      title: '8. Controlled LLM',
      subtitle: workflowContext?.llm_telemetry ? `${workflowContext.llm_telemetry.provider.toUpperCase()} (${workflowContext.llm_telemetry.status})` : 'Product Bible §21',
      status: workflowContext?.llm_telemetry ? 'COMPLETED' : 'WAITING',
      targetId: 'section-llm-enhancement',
    },
    {
      id: 'step-explanation',
      title: '9. Explanation',
      subtitle: 'Factual Rule Citations',
      status: workflowContext?.explanation ? 'COMPLETED' : 'WAITING',
      targetId: 'section-audit-trail',
    },
    {
      id: 'step-audit',
      title: '10. Audit Trail',
      subtitle: workflowContext?.audit_reference ? `Ref: ${workflowContext.audit_reference.slice(0, 15)}...` : 'Immutable Run Store',
      status: workflowContext?.audit_reference ? 'COMPLETED' : 'WAITING',
      targetId: 'section-audit-trail',
    },
  ];

  return (
    <div className="card mb-6 border-indigo-100 shadow-sm">
      <div className="card-header bg-dark-header text-white flex-between flex-wrap gap-3 py-3 px-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-2xs font-bold uppercase tracking-wider bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
              Phase 2.3 Controlled LLM Enhancement
            </span>
            <span className="text-xs text-indigo-200">
              LangGraph Branching • Product Bible §21 LLM Explainer • Deterministic Authority Intact
            </span>
          </div>

          <h2 className="text-sm font-bold text-white mt-1">
            End-to-End Workflow Pipeline & Context State
          </h2>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center bg-slate-800/80 p-1 rounded-lg border border-slate-700 text-xs">
          <button
            type="button"
            className={`px-3 py-1 rounded font-medium transition-all ${
              activeView === 'full'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
            onClick={() => onViewChange('full')}
          >
            🌐 Complete Workflow View
          </button>
          <button
            type="button"
            className={`px-3 py-1 rounded font-medium transition-all ${
              activeView === 'context'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
            onClick={() => onViewChange('context')}
          >
            🔬 Shared Context Inspector
          </button>
          <button
            type="button"
            className={`px-3 py-1 rounded font-medium transition-all ${
              activeView === 'mapping'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
            onClick={() => onViewChange('mapping')}
          >
            📋 Business Mapping View
          </button>
        </div>
      </div>

      {/* Interactive Step Visualizer */}
      <div className="card-body py-4 px-4 bg-slate-50/50">
        <div className="workflow-flow-grid">
          {pipelineSteps.map((step, idx) => {
            const isCompleted = step.status === 'COMPLETED';
            const isActive = step.status === 'ACTIVE';

            return (
              <div
                key={step.id}
                className={`flow-node cursor-pointer transition-all ${
                  isCompleted
                    ? 'flow-node-completed'
                    : isActive
                    ? 'flow-node-active'
                    : 'flow-node-waiting'
                }`}
                onClick={() => onScrollToSection(step.targetId)}
                title={`Click to inspect ${step.title}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-2xs font-mono font-bold text-slate-500">
                    STAGE {idx + 1}
                  </span>
                  <span
                    className={`inline-block w-2 h-2 rounded-full ${
                      isCompleted
                        ? 'bg-emerald-500 ring-2 ring-emerald-200'
                        : isActive
                        ? 'bg-indigo-500 ring-2 ring-indigo-200 animate-pulse'
                        : 'bg-slate-300'
                    }`}
                  />
                </div>
                <div className="font-bold text-xs text-slate-800 leading-tight mb-0.5 truncate">
                  {step.title}
                </div>
                <div className="text-2xs text-slate-500 truncate">{step.subtitle}</div>
              </div>
            );
          })}
        </div>

        {/* Informational Scope Tag */}
        <div className="mt-3 pt-3 border-t border-slate-200 flex-between flex-wrap gap-2 text-2xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">🔒 Context Boundary:</span>
            <span>
              All states are held in the <strong>run-scoped shared workflow context</strong> during execution. No permanent or long-term AI memory is used.
            </span>
          </div>
          {workflowContext && (
            <div className="font-mono text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
              Run ID: <strong>{workflowContext.workflow_id}</strong>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
