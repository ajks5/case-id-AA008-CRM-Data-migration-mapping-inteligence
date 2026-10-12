import React, { useState } from 'react';
import type { WorkflowContext } from '../api/client';

interface SharedWorkflowContextPanelProps {
  workflowContext: WorkflowContext | null;
}

export const SharedWorkflowContextPanel: React.FC<SharedWorkflowContextPanelProps> = ({
  workflowContext,
}) => {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'profile' | 'candidates' | 'transforms' | 'validation' | 'recommendation' | 'json'
  >('overview');
  const [copied, setCopied] = useState(false);

  if (!workflowContext) {
    return (
      <div id="section-shared-context" className="card mb-6">
        <div className="card-header flex-between">
          <div>
            <h2 className="text-lg font-bold text-gray-800">
              3. Run-Scoped Shared Workflow Context
            </h2>
            <p className="text-sm text-gray-500">
              Ephemeral execution-run context container (Product Bible §11 & Feeder Guide 04).
            </p>
          </div>
          <span className="badge badge-neutral text-xs">Awaiting Execution</span>
        </div>
        <div className="card-body text-center py-8 text-gray-400">
          No workflow executed yet. Run a migration scenario to inspect the initialized run-scoped shared workflow context.
        </div>
      </div>
    );
  }

  const {
    workflow_id,
    source_schema,
    destination_schema,
    sample_rows,
    relationship_metadata,
    known_mapping_hints,
    schema_profile,
    mapping_candidates,
    transformation_plan,
    validation_results,
    final_recommendation,
    explanation,
    audit_reference,
    errors,
  } = workflowContext;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(workflowContext, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const contextEvolutionSteps = [
    {
      agent: 'Context Builder',
      role: 'Workflow Initializer',
      mutation: 'Initialized context container, generated workflow ID, normalized raw schema requests.',
      fieldsAdded: ['workflow_id', 'source_schema', 'destination_schema', 'relationships', 'hints'],
      status: 'INITIALIZED',
    },
    {
      agent: 'Schema Analyzer Agent',
      role: 'Agent 1',
      mutation: `Profiled ${schema_profile?.field_count_source ?? 0} source & ${schema_profile?.field_count_destination ?? 0} destination fields, normalized types.`,
      fieldsAdded: ['schema_profile'],
      status: schema_profile ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Field Mapping Agent',
      role: 'Agent 2',
      mutation: `Discovered ${mapping_candidates?.length ?? 0} mapping candidates using exact match and synonym aliases.`,
      fieldsAdded: ['mapping_candidates'],
      status: mapping_candidates ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Transformation Agent',
      role: 'Agent 3',
      mutation: `Determined ${transformation_plan?.length ?? 0} transformation actions, type casts, and default values.`,
      fieldsAdded: ['transformation_plan'],
      status: transformation_plan ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Validation Agent',
      role: 'Agent 4',
      mutation: `Validated ${validation_results?.items.length ?? 0} constraint items, required coverage, and relationship integrity.`,
      fieldsAdded: ['validation_results'],
      status: validation_results ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Migration Decision Agent',
      role: 'Agent 5',
      mutation: `Synthesized final recommendation with status '${final_recommendation?.overall_status ?? 'N/A'}'.`,
      fieldsAdded: ['final_recommendation'],
      status: final_recommendation ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Conditional Routing Gateway',
      role: 'Phase 2.2 Branch Router',
      mutation: workflowContext.selected_route
        ? `Evaluated Product Bible §20 rules -> Branch '${workflowContext.selected_route}' taken (${workflowContext.routing_status}).`
        : 'Awaiting conditional routing evaluation.',
      fieldsAdded: ['selected_route', 'routing_status', 'routing_reason'],
      status: workflowContext.selected_route ? 'POPULATED' : 'PENDING',
    },
    {
      agent: 'Explainer & Audit Store',
      role: 'Audit Pipeline',
      mutation: `Generated ${explanation?.rule_citations.length ?? 0} rule citations and recorded immutable audit record.`,
      fieldsAdded: ['explanation', 'audit_reference'],
      status: audit_reference ? 'POPULATED' : 'PENDING',
    },
  ];

  return (
    <div id="section-shared-context" className="card mb-6 border-indigo-200 shadow-sm">
      {/* Panel Header */}
      <div className="card-header flex-between flex-wrap gap-3 bg-slate-900 text-white py-3.5 px-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge bg-indigo-500 text-white font-mono text-2xs uppercase">
              Product Bible §11
            </span>
            <h2 className="text-md font-bold text-white tracking-tight">
              3. Run-Scoped Shared Workflow Context Inspector
            </h2>
          </div>
          <p className="text-xs text-slate-300 mt-0.5">
            Structured state accumulated across all 5 specialized domain agents. Isolated to current run (not permanent/long-term memory).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-right">
            <span className="text-2xs technical-dark-label font-mono block">RUN CONTEXT ID</span>
            <span className="font-mono text-xs text-indigo-300 font-bold">{workflow_id}</span>
          </div>
          <button
            type="button"
            className="btn btn-secondary text-2xs px-2.5 py-1 bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700 ml-2"
            onClick={handleCopyJson}
            title="Copy full context JSON to clipboard"
          >
            {copied ? '✓ Copied JSON' : '📋 Copy Context JSON'}
          </button>
        </div>
      </div>

      {/* Context Lifecycle Evolution Stepper */}
      <div className="p-4 bg-indigo-50/40 border-b border-indigo-100">
        <div className="flex-between mb-2">
          <span className="text-2xs font-bold uppercase tracking-wider text-indigo-900">
            🔄 Context State Accumulation History (Step-by-Step Mutations)
          </span>
          <span className="text-2xs text-indigo-700 font-semibold">
            {contextEvolutionSteps.filter((s) => s.status === 'POPULATED' || s.status === 'INITIALIZED').length} / {contextEvolutionSteps.length} Stages Completed
          </span>
        </div>

        <div className="grid grid-4 gap-2 text-xs">
          {contextEvolutionSteps.map((step, idx) => (
            <div
              key={step.agent}
              className="p-2.5 bg-white rounded-md border border-indigo-100 shadow-2xs hover:border-indigo-300 transition-colors"
            >
              <div className="flex-between mb-1">
                <span className="text-2xs font-bold text-slate-500 font-mono">
                  STEP {idx} • {step.role}
                </span>
                <span className="inline-block px-1.5 py-0.2 rounded text-2xs font-semibold bg-emerald-100 text-emerald-800">
                  ✓ {step.status}
                </span>
              </div>
              <div className="font-bold text-slate-800 text-xs truncate mb-1">{step.agent}</div>
              <p className="text-2xs text-slate-600 leading-snug mb-1.5">{step.mutation}</p>
              <div className="flex flex-wrap gap-1">
                {step.fieldsAdded.map((f) => (
                  <span
                    key={f}
                    className="font-mono text-3xs px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded border border-slate-200"
                  >
                    +{f}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tab Navigation for Context Views */}
      <div className="flex border-b border-slate-200 bg-slate-50 px-4 pt-2 gap-2 text-xs overflow-x-auto">
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'overview'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Context Overview
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'profile'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('profile')}
        >
          🧬 Schema Profile ({schema_profile?.field_count_destination ?? 0} fields)
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'candidates'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('candidates')}
        >
          🎯 Mapping Candidates ({mapping_candidates?.length ?? 0})
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'transforms'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('transforms')}
        >
          ⚡ Transformation Plan ({transformation_plan?.length ?? 0})
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'validation'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('validation')}
        >
          🛡️ Validation Results ({validation_results?.items.length ?? 0})
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'recommendation'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('recommendation')}
        >
          🏆 Decision Output ({final_recommendation?.overall_status ?? '—'})
        </button>
        <button
          type="button"
          className={`px-3 py-2 font-semibold border-b-2 transition-all whitespace-nowrap font-mono ${
            activeTab === 'json'
              ? 'border-indigo-600 text-indigo-600 bg-white rounded-t'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setActiveTab('json')}
        >
          {'{ }'} Raw Context JSON
        </button>
      </div>

      {/* Tab Body */}
      <div className="p-4 bg-white">
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div className="grid grid-4 gap-3 text-xs">
              <div className="p-3 bg-white rounded border border-slate-200 shadow-2xs">
                <span className="text-2xs uppercase text-slate-500 font-bold block mb-1">Source Schema</span>
                <span className="font-mono font-bold text-slate-800 text-sm block">{source_schema.table_name}</span>
                <span className="text-2xs text-slate-500 block mt-1">{source_schema.fields.length} columns declared</span>
              </div>
              <div className="p-3 bg-white rounded border border-slate-200 shadow-2xs">
                <span className="text-2xs uppercase text-slate-500 font-bold block mb-1">Destination Schema</span>
                <span className="font-mono font-bold text-slate-800 text-sm block">{destination_schema.table_name}</span>
                <span className="text-2xs text-slate-500 block mt-1">{destination_schema.fields.length} columns declared</span>
              </div>
              <div className="p-3 bg-white rounded border border-slate-200 shadow-2xs">
                <span className="text-2xs uppercase text-slate-500 font-bold block mb-1">Relational Constraints</span>
                <span className="font-bold text-slate-800 text-sm block">{relationship_metadata.length} Foreign Keys</span>
                <span className="text-2xs text-slate-500 block mt-1">Cross-table integrity rules</span>
              </div>
              <div className="p-3 bg-white rounded border border-slate-200 shadow-2xs">
                <span className="text-2xs uppercase text-slate-500 font-bold block mb-1">Decision Status</span>
                <span
                  className={`inline-block px-2 py-0.5 rounded font-bold text-xs ${
                    final_recommendation?.overall_status === 'READY'
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {final_recommendation?.overall_status ?? 'IN PROGRESS'}
                </span>
                <span className="text-2xs text-slate-500 block mt-1">
                  {final_recommendation?.review_items.length ?? 0} review items flagged
                </span>
              </div>
            </div>

            {/* Business Input Summary */}
            <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
              <h4 className="font-bold text-slate-800 uppercase text-2xs mb-2">
                📥 Business Input Ingested into Context (Product Bible §5)
              </h4>
              <div className="grid grid-3 gap-3">
                <div className="p-2.5 bg-white rounded border border-slate-200">
                  <span className="text-2xs font-semibold text-slate-500 block mb-0.5">Sample Rows Provided:</span>
                  <span className="font-mono text-slate-800 font-bold">{sample_rows.length} row(s)</span>
                </div>
                <div className="p-2.5 bg-white rounded border border-slate-200">
                  <span className="text-2xs font-semibold text-slate-500 block mb-0.5">Known Mapping Hints:</span>
                  <span className="font-mono text-slate-800 font-bold">
                    {Object.keys(known_mapping_hints).length > 0
                      ? Object.entries(known_mapping_hints)
                          .map(([s, d]) => `${s} → ${d}`)
                          .join(', ')
                      : 'None provided'}
                  </span>
                </div>
                <div className="p-2.5 bg-white rounded border border-slate-200">
                  <span className="text-2xs font-semibold text-slate-500 block mb-0.5">Context Error Status:</span>
                  <span className={`font-bold ${errors.length > 0 ? 'text-red-600' : 'text-emerald-700'}`}>
                    {errors.length === 0 ? '✓ Clean execution (0 errors)' : `${errors.length} error(s)`}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Schema Profile */}
        {activeTab === 'profile' && schema_profile && (
          <div className="space-y-3 text-xs">
            <p className="text-slate-600 text-xs">
              Contributed by <strong>Agent 1: Schema Analyzer Agent</strong>. Contains normalized column types, primary key flags, and relationship descriptors.
            </p>
            <div className="grid grid-2 gap-4">
              <div className="border border-slate-200 rounded p-3 bg-slate-50">
                <h4 className="font-bold text-slate-800 mb-2">
                  Source: <span className="font-mono">{schema_profile.source_table}</span> ({schema_profile.field_count_source} cols)
                </h4>
                <div className="space-y-1">
                  {schema_profile.source_fields.map((f) => (
                    <div key={f.name} className="flex-between py-1 border-b border-slate-200 text-2xs">
                      <span className="font-mono font-medium text-slate-800">
                        {f.name} {f.is_primary_key && <span className="badge badge-primary text-3xs">PK</span>}
                      </span>
                      <span className="font-mono text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                        {f.data_type} → {f.normalized_type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border border-slate-200 rounded p-3 bg-slate-50">
                <h4 className="font-bold text-slate-800 mb-2">
                  Destination: <span className="font-mono">{schema_profile.destination_table}</span> ({schema_profile.field_count_destination} cols)
                </h4>
                <div className="space-y-1">
                  {schema_profile.destination_fields.map((f) => (
                    <div key={f.name} className="flex-between py-1 border-b border-slate-200 text-2xs">
                      <span className="font-mono font-medium text-slate-800">
                        {f.name} {f.is_required && <span className="badge badge-warning text-3xs">REQ</span>}
                      </span>
                      <span className="font-mono text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                        {f.data_type} → {f.normalized_type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Mapping Candidates */}
        {activeTab === 'candidates' && mapping_candidates && (
          <div className="space-y-2 text-xs">
            <p className="text-slate-600">
              Contributed by <strong>Agent 2: Field Mapping Agent</strong>. Evaluates exact names, aliases, and hints.
            </p>
            <div className="overflow-x-auto border border-slate-200 rounded">
              <table className="w-full text-left text-2xs">
                <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="p-2">Destination Field</th>
                    <th className="p-2">Matched Source Field</th>
                    <th className="p-2">Candidate Type</th>
                    <th className="p-2">Confidence</th>
                    <th className="p-2">Rule Applied</th>
                    <th className="p-2">Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-mono">
                  {mapping_candidates.map((c) => (
                    <tr key={c.destination_field} className="hover:bg-slate-50">
                      <td className="p-2 font-bold text-slate-800">{c.destination_field}</td>
                      <td className="p-2 text-indigo-700">{c.source_field ?? <span className="text-slate-400 font-sans italic">—</span>}</td>
                      <td className="p-2">
                        <span className={`px-1.5 py-0.5 rounded text-3xs font-bold ${
                          c.candidate_type === 'EXACT' ? 'bg-emerald-100 text-emerald-800' :
                          c.candidate_type === 'ALIAS' ? 'bg-indigo-100 text-indigo-800' :
                          c.candidate_type === 'HINT' ? 'bg-purple-100 text-purple-800' :
                          c.candidate_type === 'DEFAULT_VALUE' ? 'bg-amber-100 text-amber-800' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {c.candidate_type}
                        </span>
                      </td>
                      <td className="p-2 font-bold text-slate-800">{c.confidence_score}%</td>
                      <td className="p-2 text-slate-600">{c.rule_applied}</td>
                      <td className="p-2 font-sans text-slate-600 text-3xs max-w-xs truncate" title={c.evidence}>
                        {c.evidence}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 4: Transformation Plan */}
        {activeTab === 'transforms' && transformation_plan && (
          <div className="space-y-2 text-xs">
            <p className="text-slate-600">
              Contributed by <strong>Agent 3: Transformation Agent</strong>. Specifies casts, normalizations, and default values.
            </p>
            <div className="overflow-x-auto border border-slate-200 rounded">
              <table className="w-full text-left text-2xs">
                <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="p-2">Target Field</th>
                    <th className="p-2">Source Field</th>
                    <th className="p-2">Action Type</th>
                    <th className="p-2">Rule Applied</th>
                    <th className="p-2">Sample Before</th>
                    <th className="p-2">Sample After</th>
                    <th className="p-2">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-mono">
                  {transformation_plan.map((t) => (
                    <tr key={t.destination_field} className="hover:bg-slate-50">
                      <td className="p-2 font-bold text-slate-800">{t.destination_field}</td>
                      <td className="p-2 text-slate-700">{t.source_field ?? '—'}</td>
                      <td className="p-2">
                        <span className={`px-1.5 py-0.5 rounded text-3xs font-bold ${
                          t.action_type === 'NO_OP' ? 'bg-slate-100 text-slate-700' :
                          t.action_type === 'TYPE_CAST' ? 'bg-blue-100 text-blue-800' :
                          t.action_type === 'DEFAULT_VALUE' ? 'bg-purple-100 text-purple-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {t.action_type}
                        </span>
                      </td>
                      <td className="p-2 text-slate-600">{t.transformation_rule ?? 'NONE'}</td>
                      <td className="p-2 text-slate-500 font-sans">{t.sample_before ? String(t.sample_before) : '—'}</td>
                      <td className="p-2 text-emerald-700 font-bold font-sans">{t.sample_after ? String(t.sample_after) : '—'}</td>
                      <td className="p-2 font-sans text-slate-600 text-3xs">{t.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 5: Validation Results */}
        {activeTab === 'validation' && validation_results && (
          <div className="space-y-3 text-xs">
            <p className="text-slate-600">
              Contributed by <strong>Agent 4: Validation Agent</strong>. Evaluates Rule 4 (Required Coverage) and Rule 5 (Relationship Integrity).
            </p>
            <div className="grid grid-2 gap-3 mb-2">
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <span className="text-2xs uppercase text-slate-500 font-bold block">Overall Validation Status</span>
                <span className={`font-bold ${validation_results.all_valid ? 'text-emerald-700' : 'text-red-600'}`}>
                  {validation_results.all_valid ? '✓ ALL CONSTRAINTS SATISFIED' : '⚠ BLOCKING CONSTRAINTS DETECTED'}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <span className="text-2xs uppercase text-slate-500 font-bold block">Issue Counts</span>
                <span className="font-mono text-slate-700">
                  {validation_results.blocking_issues.length} blocking • {validation_results.warning_issues.length} warnings
                </span>
              </div>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded">
              <table className="w-full text-left text-2xs">
                <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="p-2">Field / Entity</th>
                    <th className="p-2">Check Category</th>
                    <th className="p-2">Status</th>
                    <th className="p-2">Rule Applied</th>
                    <th className="p-2">Message</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-mono">
                  {validation_results.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-2 font-bold text-slate-800">{item.field_name}</td>
                      <td className="p-2 text-slate-600">{item.check_type}</td>
                      <td className="p-2">
                        <span className={`px-1.5 py-0.5 rounded text-3xs font-bold ${
                          item.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' :
                          item.status === 'WARNING' ? 'bg-amber-100 text-amber-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="p-2 text-slate-600">{item.rule_applied}</td>
                      <td className="p-2 font-sans text-slate-700 text-3xs">{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 6: Recommendation */}
        {activeTab === 'recommendation' && final_recommendation && (
          <div className="space-y-3 text-xs">
            <p className="text-slate-600">
              Contributed by <strong>Agent 5: Migration Decision Agent</strong>. Synthesizes field actions, counts, and review flags.
            </p>
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <div className="flex-between mb-2">
                <span className="font-bold text-slate-800">Overall Status: {final_recommendation.overall_status}</span>
                <span className="text-2xs text-slate-500 font-mono">Triggered Rules: {final_recommendation.triggered_rules.join(', ')}</span>
              </div>
              <p className="text-slate-700 text-2xs mb-2 leading-relaxed">{final_recommendation.explanation_narrative}</p>
              
              <div className="grid grid-5 gap-2 text-center text-2xs font-mono font-bold mt-2">
                <div className="p-2 bg-emerald-50 text-emerald-800 rounded border border-emerald-200">
                  DIRECT: {final_recommendation.summary_counts.DIRECT_MAP}
                </div>
                <div className="p-2 bg-blue-50 text-blue-800 rounded border border-blue-200">
                  TRANSFORM: {final_recommendation.summary_counts.TRANSFORM}
                </div>
                <div className="p-2 bg-purple-50 text-purple-800 rounded border border-purple-200">
                  DEFAULT: {final_recommendation.summary_counts.DEFAULT}
                </div>
                <div className="p-2 bg-slate-100 text-slate-700 rounded border border-slate-200">
                  UNMAPPED: {final_recommendation.summary_counts.UNMAPPED}
                </div>
                <div className="p-2 bg-amber-50 text-amber-800 rounded border border-amber-200">
                  REVIEW: {final_recommendation.summary_counts.REVIEW}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 7: Raw Context JSON */}
        {activeTab === 'json' && (
          <div>
            <div className="flex-between mb-2 text-2xs text-slate-500">
              <span>Complete In-Memory Workflow Context State</span>
              <span>{JSON.stringify(workflowContext).length} characters</span>
            </div>
            <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg text-2xs font-mono overflow-x-auto max-h-96 leading-relaxed">
              {JSON.stringify(workflowContext, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
