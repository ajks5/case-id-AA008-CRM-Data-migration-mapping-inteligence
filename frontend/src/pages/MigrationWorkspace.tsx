import React, { useState, useEffect } from 'react';
import {
  fetchScenarios,
  runMigration,
  fetchAuditRecords,
  fetchHealth,
} from '../api/client';
import type {
  ScenarioItem,
  MigrationRequest,
  WorkflowContext,
  AuditRecord,
} from '../api/client';
import { SchemaSelector } from '../components/SchemaSelector';
import { WorkflowPipelineHeader } from '../components/WorkflowPipelineHeader';
import { SharedWorkflowContextPanel } from '../components/SharedWorkflowContextPanel';
import { AgentTimeline } from '../components/AgentTimeline';
import { MappingTable } from '../components/MappingTable';
import { TransformationPlanPanel } from '../components/TransformationPlanPanel';
import { ValidationSummaryPanel } from '../components/ValidationSummaryPanel';
import { AuditTrailPanel } from '../components/AuditTrailPanel';
import { LLMEnhancementPanel } from '../components/LLMEnhancementPanel';


export const MigrationWorkspace: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('simple_schema');
  const [currentRequest, setCurrentRequest] = useState<MigrationRequest | null>(null);
  const [workflowContext, setWorkflowContext] = useState<WorkflowContext | null>(null);
  const [historicalAudits, setHistoricalAudits] = useState<AuditRecord[]>([]);
  const [currentAudit, setCurrentAudit] = useState<AuditRecord | null>(null);
  const [backendHealth, setBackendHealth] = useState<string>('Checking...');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'full' | 'context' | 'mapping'>('full');

  useEffect(() => {
    // Initial data loading
    const initialize = async () => {
      try {
        const health = await fetchHealth();
        setBackendHealth(health.status);
      } catch {
        setBackendHealth('Offline (Ensure backend is running on :8000)');
      }

      try {
        const loadedScenarios = await fetchScenarios();
        setScenarios(loadedScenarios);
        if (loadedScenarios.length > 0) {
          const params = new URLSearchParams(window.location.search);
          const scenarioParam = params.get('scenario');
          const matched =
            loadedScenarios.find((s) => s.id === scenarioParam) || loadedScenarios[0];
          setSelectedScenarioId(matched.id);
          setCurrentRequest(matched.request);

          const viewParam = params.get('view') as 'full' | 'context' | 'mapping' | null;
          if (viewParam && ['full', 'context', 'mapping'].includes(viewParam)) {
            setActiveView(viewParam);
          }


          if (params.get('autorun') === '1' || params.get('autorun') === 'true') {
            setIsLoading(true);
            try {
              const context = await runMigration(matched.request);
              setWorkflowContext(context);
              const records = await fetchAuditRecords();
              setHistoricalAudits(records);
              const matchedAudit = records.find((r) => r.workflow_id === context.workflow_id);
              if (matchedAudit) {
                setCurrentAudit(matchedAudit);
              }
            } catch (runErr: any) {
              setErrorMessage(runErr.message || 'Auto-run migration failed.');
            } finally {
              setIsLoading(false);
            }
          }
        }
      } catch (err: any) {
        setErrorMessage(`Could not load scenarios: ${err.message}`);
      }

      refreshAudits();
    };

    initialize();
  }, []);

  const refreshAudits = async () => {
    try {
      const records = await fetchAuditRecords();
      setHistoricalAudits(records);
    } catch {
      // ignore in background
    }
  };

  const handleSelectScenario = (scenario: ScenarioItem) => {
    setSelectedScenarioId(scenario.id);
    setCurrentRequest(scenario.request);
    setErrorMessage(null);
  };

  const handleRunMigration = async () => {
    if (!currentRequest) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const context = await runMigration(currentRequest);
      setWorkflowContext(context);

      // Fetch refreshed audit records
      const records = await fetchAuditRecords();
      setHistoricalAudits(records);
      const matchedAudit = records.find((r) => r.workflow_id === context.workflow_id);
      if (matchedAudit) {
        setCurrentAudit(matchedAudit);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Migration execution failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrollToSection = (sectionId: string) => {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="workspace-container">
      {/* Top Navbar */}
      <header className="workspace-header flex-between flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge badge-primary font-mono text-xs">AA008</span>
            <h1 className="text-xl font-black text-gray-900 tracking-tight">
              CRM Data Migration Mapping Intelligence
            </h1>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            RealRails Agentic AI Batch 2 • LangGraph Conditional Routing • Phase 2.2
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-2xs text-gray-400 font-mono">BACKEND API (:8000)</div>
            <span
              className={`inline-block px-2 py-0.5 rounded text-2xs font-semibold ${
                backendHealth === 'healthy'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              ● {backendHealth}
            </span>
          </div>
        </div>
      </header>

      {/* Main Workspace Body */}
      <main className="workspace-main space-y-6">
        {errorMessage && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex justify-between items-center">
            <span>{errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-red-900 font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {/* 1. Architecture Visualizer Header & View Mode Switcher */}
        <WorkflowPipelineHeader
          workflowContext={workflowContext}
          activeView={activeView}
          onViewChange={setActiveView}
          onScrollToSection={handleScrollToSection}
        />

        {/* 2. Business Input: Scenario Selector & Schema Preview */}
        <div id="section-schema-selector">
          <SchemaSelector
            scenarios={scenarios}
            selectedScenarioId={selectedScenarioId}
            onSelectScenario={handleSelectScenario}
            currentRequest={currentRequest}
            onRequestChange={setCurrentRequest}
            onRunMigration={handleRunMigration}
            isLoading={isLoading}
          />
        </div>

        {/* 3. Run-Scoped Shared Workflow Context Inspector (Visible in 'full' and 'context' views) */}
        {(activeView === 'full' || activeView === 'context') && (
          <SharedWorkflowContextPanel workflowContext={workflowContext} />
        )}

        {/* 4. Deterministic Agent Execution Timeline (Visible in 'full' and 'context' views) */}
        {(activeView === 'full' || activeView === 'context') && (
          <AgentTimeline
            agentOutputs={workflowContext?.agent_outputs || []}
            nodeTrace={workflowContext?.node_trace || []}
            selectedRoute={workflowContext?.selected_route}
            routingStatus={workflowContext?.routing_status}
            routingReason={workflowContext?.routing_reason}
          />
        )}

        {/* 5. Controlled LLM Enhancement Panel (Product Bible §21) */}
        <div id="section-llm-enhancement">
          <LLMEnhancementPanel
            llmEnhancement={workflowContext?.llm_enhancement}
            llmTelemetry={workflowContext?.llm_telemetry}
          />
        </div>

        {/* 6. Mapping Recommendations Table (Visible in 'full' and 'mapping' views) */}
        {(activeView === 'full' || activeView === 'mapping') && (
          <MappingTable
            recommendation={workflowContext?.final_recommendation || null}
            workflowId={workflowContext?.workflow_id || '—'}
          />
        )}

        {/* 7. Transformation Plan & Validation Summary (Visible in 'full' and 'mapping' views) */}
        {(activeView === 'full' || activeView === 'mapping') && (
          <div className="grid grid-2 gap-6">
            <TransformationPlanPanel
              transformationPlan={workflowContext?.transformation_plan || null}
            />
            <ValidationSummaryPanel
              validationResult={workflowContext?.validation_results || null}
            />
          </div>
        )}

        {/* 8. Audit Trail & Explanation Panel */}
        <div id="section-audit-trail">
          <AuditTrailPanel
            currentAudit={currentAudit}
            historicalAudits={historicalAudits}
            explanation={workflowContext?.explanation || null}
            onRefreshAudits={refreshAudits}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="workspace-footer text-center py-6 text-xs text-gray-400">
        AA008 CRM Data Migration Mapping Intelligence • RealRails Agentic AI Batch 2 • Phase 2.3: Controlled LLM Enhancement
      </footer>
    </div>
  );

};
