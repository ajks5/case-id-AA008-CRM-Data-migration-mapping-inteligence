import React, { useState } from 'react';
import type { AgentExecutionOutput, NodeTraceEntry } from '../api/client';

interface AgentTimelineProps {
  agentOutputs: AgentExecutionOutput[];
  nodeTrace?: NodeTraceEntry[];
  selectedRoute?: string;
  routingStatus?: string;
  routingReason?: string;
}

export const AgentTimeline: React.FC<AgentTimelineProps> = ({
  agentOutputs,
  nodeTrace,
  selectedRoute,
  routingStatus,
  routingReason,
}) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const toggleExpand = (agentName: string) => {
    setExpandedAgent(expandedAgent === agentName ? null : agentName);
  };

  if (!agentOutputs || agentOutputs.length === 0) {
    return (
      <div id="section-agent-timeline" className="card mb-6">
        <div className="card-header">
          <h2 className="text-lg font-bold text-gray-800">4. Agent Execution Timeline</h2>
          <p className="text-sm text-gray-500">Awaiting workflow run to display agent telemetry.</p>
        </div>
        <div className="card-body text-center py-8 text-gray-400">
          No workflow executed yet. Click <strong>"Run 5-Agent Migration Pipeline"</strong> above.
        </div>
      </div>
    );
  }

  // Domain agent mapping to Product Bible §8
  const agentMetadata: Record<string, { role: string; contextKey: string; rules: string }> = {
    'Schema Analyzer Agent': {
      role: 'Agent 1 • Profiling & Normalization',
      contextKey: 'schema_profile',
      rules: 'Normalizes column names, maps data types, registers primary keys and relationships.',
    },
    'Field Mapping Agent': {
      role: 'Agent 2 • Candidate Matching',
      contextKey: 'mapping_candidates',
      rules: 'Evaluates Rule 1 (Exact Match) and Rule 2 (CRM Aliases).',
    },
    'Transformation Agent': {
      role: 'Agent 3 • Type Conversion & Normalization',
      contextKey: 'transformation_plan',
      rules: 'Evaluates Rule 3 (Type-Convertible Transforms & Default Values).',
    },
    'Validation Agent': {
      role: 'Agent 4 • Constraint & Integrity Checking',
      contextKey: 'validation_results',
      rules: 'Evaluates Rule 4 (Required Coverage) and Rule 5 (Relational Conflicts).',
    },
    'Migration Decision Agent': {
      role: 'Agent 5 • Decision Synthesis',
      contextKey: 'final_recommendation',
      rules: 'Synthesizes all prior outputs into approved field actions (READY / NEEDS_REVIEW).',
    },
  };

  return (
    <div id="section-agent-timeline" className="card mb-6 border-slate-200 shadow-sm">
      <div className="card-header flex-between flex-wrap gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge badge-primary font-mono text-2xs uppercase">Phase 2.3 • LangGraph Routing + Controlled LLM</span>
            <h2 className="text-lg font-bold text-gray-800">
              4. LangGraph Node Execution & Domain Agent Timeline
            </h2>
          </div>
          <p className="text-sm text-gray-500">
            Dynamic conditional branching and controlled LLM enhancement via LangGraph StateGraph (Product Bible §20 & §21).
          </p>
        </div>
        <div className="flex items-center gap-2">
          {selectedRoute && (
            <span className="badge badge-primary text-xs font-mono font-semibold">
              Route: {selectedRoute}
            </span>
          )}
          <span className="badge badge-success text-xs font-semibold">
            {nodeTrace ? `${nodeTrace.length} Nodes` : `${agentOutputs.length} Agents`} Executed
          </span>
        </div>
      </div>

      <div className="card-body">
        {/* LangGraph Node Execution Trace Visualizer */}
        {nodeTrace && nodeTrace.length > 0 && (
          <div className="pipeline-dark-container">
            <div className="flex-between items-center mb-2.5 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-2xs font-bold font-mono uppercase bg-indigo-500/40 text-indigo-200 border border-indigo-400/40">
                  LangGraph Conditional StateGraph Trace
                </span>
                <span className="text-xs text-slate-300">
                  Topology: <code>START → 6 Nodes → [Router] → Branch Node → LLM Enhancement → Explainer → Audit → END</code>
                </span>
              </div>
              <div className="flex items-center gap-2">
                {selectedRoute && (
                  <span className="badge-branch-tag">
                    🔀 Branch: {selectedRoute} ({routingStatus})
                  </span>
                )}
                <span className="text-2xs font-mono text-emerald-400 font-semibold">
                  ● {nodeTrace.length} Nodes Executed
                </span>
              </div>
            </div>

            {routingReason && (
              <div className="mb-3 text-2xs text-slate-300 bg-slate-800 p-2 rounded border border-slate-700">
                <strong className="text-amber-300">Routing Rationale:</strong> {routingReason}
              </div>
            )}

            <div className="node-trace-grid text-2xs font-mono">
              {nodeTrace.map((step) => {
                const isBranchNode = ['direct_accept', 'transform_verify', 'human_review'].includes(step.node);
                const isLLMNode = step.node === 'llm_enhancement';
                return (
                  <div
                    key={step.node}
                    className={
                      isLLMNode
                        ? 'p-2 rounded bg-purple-900/60 border border-purple-400 flex flex-col justify-between shadow-xs'
                        : isBranchNode
                        ? 'node-trace-card-branch'
                        : 'node-trace-card'
                    }
                  >
                    <div>
                      <div
                        className={`text-3xs font-bold mb-0.5 ${
                          isLLMNode
                            ? 'text-purple-300'
                            : isBranchNode
                            ? 'text-amber-300'
                            : 'text-indigo-300'
                        }`}
                      >
                        #{step.step_number} {step.node}
                        {isLLMNode && ' 🤖'}
                        {isBranchNode && ' ★'}
                      </div>
                      <div className="text-slate-300 font-sans text-3xs truncate" title={step.agent}>
                        {step.agent}
                      </div>
                    </div>
                    <div className="text-emerald-400 text-3xs mt-1.5 font-bold">✓ {step.status}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="timeline-container">
          {agentOutputs.map((agent, index) => {
            const isLast = index === agentOutputs.length - 1;
            const isSuccess = agent.status === 'SUCCESS';
            const isWarning = agent.status === 'WARNING';
            const isExpanded = expandedAgent === agent.agent_name;
            const meta = agentMetadata[agent.agent_name] || {
              role: `Agent ${index + 1}`,
              contextKey: 'agent_outputs',
              rules: 'Deterministic domain rules.',
            };

            return (
              <div key={agent.agent_name} className="timeline-item">
                <div className="timeline-marker-container">
                  <div
                    className={`timeline-marker ${
                      isSuccess ? 'marker-success' : isWarning ? 'marker-warning' : 'marker-error'
                    }`}
                  >
                    {index + 1}
                  </div>
                  {!isLast && <div className="timeline-connector" />}
                </div>

                <div className="timeline-content">
                  <div className="flex-between mb-1.5 flex-wrap gap-2">
                    <div>
                      <span className="text-2xs font-mono font-bold text-indigo-600 uppercase mr-2">
                        {meta.role}
                      </span>
                      <h3 className="font-bold text-gray-900 text-sm inline-block">
                        {agent.agent_name}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 font-mono">
                        {new Date(agent.timestamp).toLocaleTimeString()}
                      </span>
                      <span
                        className={`badge ${
                          isSuccess ? 'badge-success' : isWarning ? 'badge-warning' : 'badge-error'
                        }`}
                      >
                        {agent.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-indigo-900 font-medium mb-2.5 bg-indigo-50/70 border border-indigo-100 px-2.5 py-1.5 rounded">
                    🎯 <strong>Responsibility (Product Bible §8):</strong> {agent.responsibility}
                  </p>

                  {/* Input / Output Structured Cards */}
                  <div className="grid grid-2 gap-3 text-xs mb-2">
                    <div className="agent-io-box bg-slate-50 border border-slate-200 p-2.5 rounded">
                      <strong className="text-slate-700 flex items-center gap-1 mb-1">
                        <span>📥</span> Read from Shared Context:
                      </strong>
                      <span className="text-slate-600 leading-relaxed block">{agent.input_summary}</span>
                    </div>
                    <div className="agent-io-box bg-indigo-50/40 border border-indigo-200/70 p-2.5 rounded">
                      <strong className="text-indigo-900 flex items-center gap-1 mb-1">
                        <span>📤</span> Contributed to Shared Context (<code>context.{meta.contextKey}</code>):
                      </strong>
                      <span className="text-indigo-800 leading-relaxed block">{agent.output_summary}</span>
                    </div>
                  </div>

                  {/* Expandable Inspector Toggle */}
                  <div className="mt-2 flex-between">
                    <button
                      type="button"
                      onClick={() => toggleExpand(agent.agent_name)}
                      className="text-2xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                    >
                      {isExpanded ? '▲ Hide Execution Telemetry & Rule Details' : '▼ Inspect Telemetry & Domain Rules'}
                    </button>
                    <span className="text-3xs font-mono text-slate-400">
                      Context target: context.{meta.contextKey}
                    </span>
                  </div>

                  {/* Expanded Telemetry & Rule Information */}
                  {isExpanded && (
                    <div className="mt-3 p-3 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono space-y-2">
                      <div className="flex-between text-2xs text-indigo-300 border-b border-slate-800 pb-1">
                        <span>AGENT TELEMETRY DETAILS</span>
                        <span>EXECUTION SEQ: #{index + 1}</span>
                      </div>
                      <div className="text-2xs text-slate-300 font-sans">
                        <strong className="text-slate-100 font-mono">Domain Rules & Logic: </strong>
                        {meta.rules}
                      </div>
                      {agent.details && Object.keys(agent.details).length > 0 && (
                        <div>
                          <strong className="text-slate-400 block mb-1 text-2xs">Structured Output Telemetry:</strong>
                          <pre className="text-3xs bg-slate-950 p-2 rounded text-emerald-400 overflow-x-auto leading-relaxed">
                            {JSON.stringify(agent.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
