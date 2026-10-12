import React, { useEffect, useRef, useState } from 'react';
import {
  fetchAuditRecords,
  fetchHealth,
  fetchScenarios,
  runMigration,
} from '../api/client';
import type { AuditRecord, MigrationRequest, ScenarioItem, WorkflowContext } from '../api/client';
import { BusinessInputForm } from '../components/BusinessInputForm';
import { BusinessRecommendation } from '../components/BusinessRecommendation';
import { RecentRuns } from '../components/RecentRuns';
import { TechnicalAuditDrawer } from '../components/TechnicalAuditDrawer';

type MainPage = 'new' | 'recent';
type AdvancedView = 'full' | 'context' | 'mapping';

function errorText(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

function preferredScrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
}

export const ProductWorkspace: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('simple_schema');
  const [currentRequest, setCurrentRequest] = useState<MigrationRequest | null>(null);
  const [workflowContext, setWorkflowContext] = useState<WorkflowContext | null>(null);
  const [historicalAudits, setHistoricalAudits] = useState<AuditRecord[]>([]);
  const [currentAudit, setCurrentAudit] = useState<AuditRecord | null>(null);
  const [serviceStatus, setServiceStatus] = useState<'checking' | 'healthy' | 'offline'>('checking');
  const [mainPage, setMainPage] = useState<MainPage>('new');
  const [advancedView, setAdvancedView] = useState<AdvancedView>('full');
  const [showTechnicalDrawer, setShowTechnicalDrawer] = useState(false);
  const [isLoadingExamples, setIsLoadingExamples] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshingAudits, setIsRefreshingAudits] = useState(false);
  const [scenarioError, setScenarioError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [technicalError, setTechnicalError] = useState<string | null>(null);
  const [auditError, setAuditError] = useState<string | null>(null);
  const initialized = useRef(false);

  const refreshAudits = async () => {
    setIsRefreshingAudits(true);
    try {
      const records = await fetchAuditRecords();
      setHistoricalAudits(records);
      setAuditError(null);
    } catch {
      setAuditError('Recent assessment records are unavailable right now. Try refreshing the list.');
    } finally {
      setIsRefreshingAudits(false);
    }
  };

  const executeAssessment = async (request: MigrationRequest) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    setTechnicalError(null);
    setWorkflowContext(null);
    setCurrentAudit(null);
    setShowTechnicalDrawer(false);
    try {
      const context = await runMigration(request);
      setWorkflowContext(context);
      try {
        const records = await fetchAuditRecords();
        setHistoricalAudits(records);
        setAuditError(null);
        setCurrentAudit(records.find((record) => record.workflow_id === context.workflow_id) ?? null);
      } catch {
        setAuditError('The recommendation is ready, but its audit record could not be refreshed.');
      }
    } catch (error) {
      setErrorMessage('The assessment could not be completed. Check the service connection and schema details, then try again.');
      setTechnicalError(errorText(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadExamples = async (initial = false) => {
    setIsLoadingExamples(true);
    setScenarioError(null);
    try {
      const loadedScenarios = await fetchScenarios();
      setScenarios(loadedScenarios);
      if (loadedScenarios.length > 0) {
        const params = new URLSearchParams(window.location.search);
        const requested = params.get('scenario');
        const matched = loadedScenarios.find((scenario) => scenario.id === requested) ?? loadedScenarios[0];
        setSelectedScenarioId(matched.id);
        setCurrentRequest(matched.request);
        if (initial) {
          const viewParam = params.get('view');
          if (params.get('autorun') === '1' || params.get('autorun') === 'true') {
            await executeAssessment(matched.request);
          }
          if (
            viewParam === 'full' ||
            viewParam === 'context' ||
            viewParam === 'mapping' ||
            viewParam === 'technical' ||
            viewParam === 'audit' ||
            params.get('drawer') === '1' ||
            params.get('drawer') === 'true'
          ) {
            if (viewParam === 'full' || viewParam === 'context' || viewParam === 'mapping') {
              setAdvancedView(viewParam);
            }
            setShowTechnicalDrawer(true);
          }
        }
      } else {
        setScenarioError('No sample schema pairs are available. You can provide a custom request below or try again.');
      }
    } catch {
      setScenarioError('Sample schema pairs could not be loaded. Check the service connection and try again.');
    } finally {
      setIsLoadingExamples(false);
    }
  };

  const initialize = async () => {
    setServiceStatus('checking');
    try {
      const health = await fetchHealth();
      setServiceStatus(health.status === 'healthy' ? 'healthy' : 'offline');
    } catch {
      setServiceStatus('offline');
    }
    await loadExamples(true);
    await refreshAudits();
  };

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    void initialize();
  }, []);

  useEffect(() => {
    if (workflowContext) {
      document.getElementById('section-mapping-table')?.scrollIntoView({
        behavior: preferredScrollBehavior(),
        block: 'start',
      });
    }
  }, [workflowContext]);

  const retryConnection = async () => {
    setServiceStatus('checking');
    try {
      const health = await fetchHealth();
      setServiceStatus(health.status === 'healthy' ? 'healthy' : 'offline');
      if (health.status === 'healthy' && scenarios.length === 0) {
        await loadExamples();
      }
    } catch {
      setServiceStatus('offline');
    }
  };

  const handleSelectScenario = (scenario: ScenarioItem) => {
    setSelectedScenarioId(scenario.id);
    setCurrentRequest(scenario.request);
    setScenarioError(null);
  };

  const handleRequestChange = (request: MigrationRequest) => {
    setCurrentRequest(request);
    const matchingScenario = scenarios.find((scenario) => JSON.stringify(scenario.request) === JSON.stringify(request));
    setSelectedScenarioId(matchingScenario?.id ?? 'custom');
  };

  const handleStartAnother = () => {
    setWorkflowContext(null);
    setCurrentAudit(null);
    setErrorMessage(null);
    setTechnicalError(null);
    setShowTechnicalDrawer(false);
    setMainPage('new');
    window.scrollTo({ top: 0, behavior: preferredScrollBehavior() });
  };

  const openAudit = (record: AuditRecord) => {
    setCurrentAudit(record);
    setErrorMessage(null);
    setTechnicalError(null);
    setShowTechnicalDrawer(true);
  };

  return (
    <div className="product-shell">
      <header className="product-topbar">
        <a className="product-brand" href="#main-content" aria-label="CRM Migration Mapping home">
          <span className="product-case-id">AA008</span>
          <span className="product-brand-copy">
            <strong>CRM Migration Mapping</strong>
            <span>Prepare and review a field mapping plan</span>
          </span>
        </a>

        <nav className="product-navigation" aria-label="Workspace navigation">
          <button
            type="button"
            className={mainPage === 'new' && !showTechnicalDrawer ? 'is-active' : ''}
            aria-current={mainPage === 'new' && !showTechnicalDrawer ? 'page' : undefined}
            onClick={() => { setMainPage('new'); setShowTechnicalDrawer(false); }}
          >
            New assessment
          </button>
          <button
            type="button"
            className={mainPage === 'recent' && !showTechnicalDrawer ? 'is-active' : ''}
            aria-current={mainPage === 'recent' && !showTechnicalDrawer ? 'page' : undefined}
            onClick={() => { setMainPage('recent'); setShowTechnicalDrawer(false); void refreshAudits(); }}
          >
            Recent assessments{historicalAudits.length > 0 ? ` (${historicalAudits.length})` : ''}
          </button>
          <button
            type="button"
            className={`product-nav-technical ${showTechnicalDrawer ? 'is-active' : ''}`}
            onClick={() => setShowTechnicalDrawer(true)}
            title="Inspect Agentic AI internals, 10-node LangGraph trace, routing, and audit records"
            aria-haspopup="dialog"
            aria-expanded={showTechnicalDrawer}
          >
            <span className="product-nav-tech-badge">Reviewer</span>
            <span>Explainability &amp; Audit</span>
          </button>
        </nav>

        <button
          type="button"
          className={`product-service-status product-service-${serviceStatus}`}
          onClick={retryConnection}
          aria-live="polite"
          title="Retry the service connection"
        >
          <span className="product-status-dot" aria-hidden="true" />
          {serviceStatus === 'healthy' ? 'Service connected' : serviceStatus === 'checking' ? 'Checking service' : 'Service unavailable'}
        </button>
      </header>

      <main id="main-content" className="product-main">
        {mainPage === 'new' ? (
          <>
            <section className="product-page-intro">
              <div>
                <p className="product-kicker">CRM data migration</p>
                <h1>Map a schema pair</h1>
                <p>Compare source and destination fields, review proposed changes, and identify gaps before a migration.</p>
              </div>
              <div className="product-process-note" aria-label="Workflow summary">
                <span>Schema pair</span><span aria-hidden="true">→</span><span>Recommendation</span><span aria-hidden="true">→</span><span>Analyst review</span>
              </div>
            </section>

            {errorMessage && (
              <div className="product-alert" role="alert">
                <div><strong>Assessment not completed</strong><p>{errorMessage}</p></div>
                <button type="button" onClick={() => setErrorMessage(null)} aria-label="Dismiss message">Dismiss</button>
              </div>
            )}
            {scenarioError && scenarios.length > 0 && (
              <div className="product-alert product-alert-info" role="status">
                <p>{scenarioError}</p>
                <button type="button" onClick={() => void loadExamples()}>Retry examples</button>
              </div>
            )}

            <div id="section-schema-selector">
              <BusinessInputForm
                scenarios={scenarios}
                selectedScenarioId={selectedScenarioId}
                currentRequest={currentRequest}
                isLoadingExamples={isLoadingExamples}
                isSubmitting={isSubmitting}
                onSelectScenario={handleSelectScenario}
                onRequestChange={handleRequestChange}
                onRunAssessment={() => currentRequest && void executeAssessment(currentRequest)}
                onRetryExamples={() => void loadExamples()}
              />
            </div>

            {workflowContext && (
              <BusinessRecommendation
                workflowContext={workflowContext}
                onStartAnother={handleStartAnother}
                onOpenTechnicalDetails={() => setShowTechnicalDrawer(true)}
              />
            )}

            {!workflowContext && !isSubmitting && !currentAudit && !errorMessage && scenarios.length > 0 && (
              <section className="product-empty-result" aria-live="polite">
                <div className="product-empty-icon" aria-hidden="true">↗</div>
                <div>
                  <h2>Your recommendation will appear here</h2>
                  <p>Choose a schema pair above to see field matches, evidence, proposed changes, and items for review.</p>
                </div>
              </section>
            )}

            {isSubmitting && (
              <section className="product-progress" role="status" aria-live="polite">
                <span className="product-progress-mark" aria-hidden="true" />
                <div><strong>Preparing your mapping recommendation</strong><p>Checking field matches, data types, required fields, and relationships.</p></div>
              </section>
            )}
          </>
        ) : (
          <>
            <section className="product-page-intro product-history-intro">
              <div>
                <p className="product-kicker">Workspace activity</p>
                <h1>Recent assessments</h1>
                <p>Review recommendations recorded during the current service session.</p>
              </div>
              <button className="product-button product-button-primary" type="button" onClick={() => setMainPage('new')}>
                Start a new assessment
              </button>
            </section>
            <RecentRuns
              records={historicalAudits}
              isLoading={isRefreshingAudits}
              errorMessage={auditError}
              onRefresh={() => void refreshAudits()}
              onOpenAudit={openAudit}
            />
          </>
        )}
      </main>

      <footer className="product-footer">
        <span>CRM Migration Mapping · AA008</span>
        <span>Recommendations support analyst review; the application does not run a migration.</span>
      </footer>

      {/* Separate Technical Details / Explainability & Audit Drawer */}
      <TechnicalAuditDrawer
        isOpen={showTechnicalDrawer}
        onClose={() => setShowTechnicalDrawer(false)}
        workflowContext={workflowContext}
        currentAudit={currentAudit}
        historicalAudits={historicalAudits}
        onRefreshAudits={refreshAudits}
        onRunSampleAssessment={() => currentRequest && void executeAssessment(currentRequest)}
        technicalError={technicalError}
        auditError={auditError}
        initialView={advancedView}
      />
    </div>
  );
};
