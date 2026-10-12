import React, { useEffect, useRef, useState } from 'react';
import type { AuditRecord, WorkflowContext } from '../api/client';
import { AgentTimeline } from './AgentTimeline';
import { AuditTrailPanel } from './AuditTrailPanel';
import { LLMEnhancementPanel } from './LLMEnhancementPanel';
import { MappingTable } from './MappingTable';
import { SharedWorkflowContextPanel } from './SharedWorkflowContextPanel';
import { TransformationPlanPanel } from './TransformationPlanPanel';
import { ValidationSummaryPanel } from './ValidationSummaryPanel';
import { WorkflowPipelineHeader } from './WorkflowPipelineHeader';

export interface TechnicalAuditDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  workflowContext: WorkflowContext | null;
  currentAudit: AuditRecord | null;
  historicalAudits: AuditRecord[];
  onRefreshAudits: () => Promise<void>;
  onRunSampleAssessment?: () => void;
  technicalError?: string | null;
  auditError?: string | null;
  initialView?: 'full' | 'context' | 'mapping';
}

function preferredScrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
}

export const TechnicalAuditDrawer: React.FC<TechnicalAuditDrawerProps> = ({
  isOpen,
  onClose,
  workflowContext,
  currentAudit,
  historicalAudits,
  onRefreshAudits,
  onRunSampleAssessment,
  technicalError,
  auditError,
  initialView = 'full',
}) => {
  const [userSelectedView, setUserSelectedView] = useState<'full' | 'context' | 'mapping' | null>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const drawerBodyRef = useRef<HTMLDivElement>(null);

  const activeView = userSelectedView ?? initialView ?? 'full';
  const setActiveView = (view: 'full' | 'context' | 'mapping') => setUserSelectedView(view);

  // Handle escape key to close drawer
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent background body scrolling when drawer is open
  useEffect(() => {
    if (isOpen) {
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const scrollToSection = (sectionId: string) => {
    const targetElement =
      document.getElementById(`drawer-${sectionId}`) ||
      document.getElementById(sectionId);

    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: preferredScrollBehavior(),
        block: 'start',
      });
    }
  };

  const overallStatus =
    workflowContext?.final_recommendation?.overall_status ||
    currentAudit?.final_recommendation_status;

  const route = workflowContext?.selected_route;
  const routingStatus = workflowContext?.routing_status;
  const llmTelemetry = workflowContext?.llm_telemetry;

  return (
    <div
      className="product-drawer-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="technical-drawer-title"
    >
      {/* Backdrop */}
      <div
        className="product-drawer-backdrop"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Container */}
      <div
        className={`product-drawer-container ${isMaximized ? 'is-maximized' : ''}`}
      >
        {/* Drawer Header */}
        <header className="product-drawer-header">
          <div className="product-drawer-title-group">
            <div className="product-drawer-kicker-row">
              <span className="product-case-id">AA008</span>
              <span className="product-drawer-kicker">
                Explainability, Audit &amp; Technical Details
              </span>
              <span className="product-drawer-arch-pill">
                LangGraph StateGraph
              </span>
            </div>
            <h2 id="technical-drawer-title" className="product-drawer-title">
              Agentic AI Internals &amp; Execution Trace
            </h2>
            <p className="product-drawer-subtitle">
              Inspect the 10-node state machine, deterministic rules, routing logic,
              controlled LLM telemetry, and audit trail.
            </p>
          </div>

          {/* Telemetry quick badges */}
          <div className="product-drawer-badges">
            {workflowContext ? (
              <>
                <div className="product-drawer-badge" title="Active Run ID">
                  <span className="badge-label">Run ID</span>
                  <span className="badge-value font-mono">{workflowContext.workflow_id}</span>
                </div>

                {route && (
                  <div className="product-drawer-badge badge-route" title="Conditional Graph Route">
                    <span className="badge-label">Route</span>
                    <span className="badge-value">{route}</span>
                  </div>
                )}

                {routingStatus && (
                  <div className="product-drawer-badge" title="Routing Status">
                    <span className="badge-label">Branch Status</span>
                    <span className="badge-value">{routingStatus}</span>
                  </div>
                )}

                {overallStatus && (
                  <div
                    className={`product-drawer-badge ${
                      overallStatus === 'READY'
                        ? 'badge-success'
                        : 'badge-warning'
                    }`}
                    title="Overall Migration Readiness"
                  >
                    <span className="badge-label">Status</span>
                    <span className="badge-value font-bold">{overallStatus}</span>
                  </div>
                )}

                {llmTelemetry && (
                  <div className="product-drawer-badge badge-llm" title="LLM Provider Telemetry">
                    <span className="badge-label">LLM</span>
                    <span className="badge-value">
                      {llmTelemetry.provider.toUpperCase()} ({llmTelemetry.status}) · {llmTelemetry.latency_ms}ms
                    </span>
                  </div>
                )}
              </>
            ) : currentAudit ? (
              <>
                <div className="product-drawer-badge" title="Historical Audit Record">
                  <span className="badge-label">Audit ID</span>
                  <span className="badge-value font-mono">{currentAudit.workflow_id}</span>
                </div>
                {overallStatus && (
                  <div
                    className={`product-drawer-badge ${
                      overallStatus === 'READY'
                        ? 'badge-success'
                        : 'badge-warning'
                    }`}
                  >
                    <span className="badge-label">Status</span>
                    <span className="badge-value font-bold">{overallStatus}</span>
                  </div>
                )}
              </>
            ) : null}
          </div>

          {/* Header Controls */}
          <div className="product-drawer-controls">
            <button
              type="button"
              className="product-drawer-btn"
              onClick={() => setIsMaximized(!isMaximized)}
              title={isMaximized ? 'Dock to side drawer width' : 'Maximize to full width page'}
              aria-label={isMaximized ? 'Dock width' : 'Maximize width'}
            >
              {isMaximized ? '❐ Dock' : '⛶ Fullscreen'}
            </button>
            <button
              type="button"
              className="product-drawer-close"
              onClick={onClose}
              aria-label="Close technical drawer"
            >
              ✕
            </button>
          </div>
        </header>

        {/* View Switcher & Quick Navigation Bar */}
        <div className="product-drawer-toolbar">
          <div className="product-drawer-nav">
            <button
              type="button"
              className={`product-drawer-tab ${activeView === 'full' ? 'is-active' : ''}`}
              onClick={() => setActiveView('full')}
            >
              🌐 Complete Workflow View
            </button>
            <button
              type="button"
              className={`product-drawer-tab ${activeView === 'context' ? 'is-active' : ''}`}
              onClick={() => setActiveView('context')}
            >
              🔬 Shared Context Inspector
            </button>
            <button
              type="button"
              className={`product-drawer-tab ${activeView === 'mapping' ? 'is-active' : ''}`}
              onClick={() => setActiveView('mapping')}
            >
              📋 Business Mapping &amp; Validation
            </button>
          </div>

          {workflowContext && (
            <div className="product-drawer-jump-links">
              <span>Jump to:</span>
              <button type="button" onClick={() => scrollToSection('section-pipeline')}>
                Pipeline
              </button>
              <button type="button" onClick={() => scrollToSection('section-shared-context')}>
                Context
              </button>
              <button type="button" onClick={() => scrollToSection('section-agent-timeline')}>
                Trace
              </button>
              <button type="button" onClick={() => scrollToSection('section-mapping-table')}>
                Matrix
              </button>
              <button type="button" onClick={() => scrollToSection('section-llm-enhancement')}>
                LLM
              </button>
              <button type="button" onClick={() => scrollToSection('section-audit-trail')}>
                Audit
              </button>
            </div>
          )}
        </div>

        {/* Drawer Scrollable Content */}
        <div className="product-drawer-body" ref={drawerBodyRef}>
          {/* Architecture Guardrail Banner */}
          <div className="product-drawer-banner">
            <span className="product-banner-icon" aria-hidden="true">🛡️</span>
            <div>
              <strong>Architecture Guarantee: Deterministic Authority Intact</strong>
              <p>
                Deterministic rules (1–5) and constraint validation govern 100% of field mappings,
                confidence scores, and conditional branch routing. The controlled LLM operates
                strictly within Pydantic guardrails to generate plain-language narrative and checklists
                with zero decision authority.
              </p>
            </div>
          </div>

          {workflowContext ? (
            <>
              {/* Interactive Pipeline Visualizer */}
              <div id="drawer-section-pipeline">
                <WorkflowPipelineHeader
                  workflowContext={workflowContext}
                  activeView={activeView}
                  onViewChange={setActiveView}
                  onScrollToSection={scrollToSection}
                />
              </div>

              {/* Shared Context Inspector (Full or Context view) */}
              {(activeView === 'full' || activeView === 'context') && (
                <div id="drawer-section-shared-context">
                  <SharedWorkflowContextPanel workflowContext={workflowContext} />
                </div>
              )}

              {/* Agent Timeline & 10-Node Trace (Full or Context view) */}
              {(activeView === 'full' || activeView === 'context') && (
                <div id="drawer-section-agent-timeline">
                  <AgentTimeline
                    agentOutputs={workflowContext.agent_outputs}
                    nodeTrace={workflowContext.node_trace ?? []}
                    selectedRoute={workflowContext.selected_route}
                    routingStatus={workflowContext.routing_status}
                    routingReason={workflowContext.routing_reason}
                  />
                </div>
              )}

              {/* Mapping Matrix & Validation (Full or Mapping view) */}
              {(activeView === 'full' || activeView === 'mapping') && (
                <>
                  <div id="drawer-section-mapping-table">
                    <MappingTable
                      recommendation={workflowContext.final_recommendation ?? null}
                      workflowId={workflowContext.workflow_id}
                    />
                  </div>
                  <div className="product-advanced-grid">
                    <TransformationPlanPanel
                      transformationPlan={workflowContext.transformation_plan ?? null}
                    />
                    <ValidationSummaryPanel
                      validationResult={workflowContext.validation_results ?? null}
                    />
                  </div>
                </>
              )}

              {/* Controlled LLM Advisory Panel */}
              <div id="drawer-section-llm-enhancement">
                <LLMEnhancementPanel
                  llmEnhancement={workflowContext.llm_enhancement}
                  llmTelemetry={workflowContext.llm_telemetry}
                />
              </div>

              {/* In-Memory Audit Trail & Recent Runs */}
              <div id="drawer-section-audit-trail">
                <AuditTrailPanel
                  currentAudit={currentAudit}
                  historicalAudits={historicalAudits}
                  explanation={workflowContext.explanation ?? null}
                  onRefreshAudits={onRefreshAudits}
                />
              </div>
            </>
          ) : currentAudit ? (
            <>
              <div className="product-drawer-info-callout">
                <strong>Historical Audit Record Loaded</strong>
                <p>
                  Displaying execution telemetry and decision summary recorded for workflow{' '}
                  <code>{currentAudit.workflow_id}</code>.
                </p>
              </div>
              <div id="drawer-section-audit-trail">
                <AuditTrailPanel
                  currentAudit={currentAudit}
                  historicalAudits={historicalAudits}
                  explanation={null}
                  onRefreshAudits={onRefreshAudits}
                />
              </div>
            </>
          ) : (
            <div className="product-drawer-empty">
              <div className="product-drawer-empty-icon" aria-hidden="true">🔬</div>
              <h3>No Execution Trace Loaded Yet</h3>
              <p>
                Run a mapping assessment from the main business workspace or select an entry
                from Recent Assessments to inspect the end-to-end 10-node LangGraph trace,
                routing logic, deterministic rules, and LLM telemetry.
              </p>
              {onRunSampleAssessment && (
                <button
                  type="button"
                  className="product-button product-button-primary mt-4"
                  onClick={onRunSampleAssessment}
                >
                  Run Sample Assessment Now
                </button>
              )}
            </div>
          )}

          {auditError && (
            <p className="product-history-error" role="status">
              {auditError}
            </p>
          )}

          {technicalError && (
            <details className="product-technical-error">
              <summary>Show technical error trace</summary>
              <pre>{technicalError}</pre>
            </details>
          )}
        </div>
      </div>
    </div>
  );
};
