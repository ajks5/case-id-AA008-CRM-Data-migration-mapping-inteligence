import React, { useState } from 'react';
import type { ScenarioItem, MigrationRequest } from '../api/client';

interface SchemaSelectorProps {
  scenarios: ScenarioItem[];
  selectedScenarioId: string;
  onSelectScenario: (scenario: ScenarioItem) => void;
  currentRequest: MigrationRequest | null;
  onRequestChange: (request: MigrationRequest) => void;
  onRunMigration: () => void;
  isLoading: boolean;
}

export const SchemaSelector: React.FC<SchemaSelectorProps> = ({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  currentRequest,
  onRequestChange,
  onRunMigration,
  isLoading,
}) => {
  const [showJsonEditor, setShowJsonEditor] = useState(false);
  const [jsonText, setJsonText] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);

  const handleJsonToggle = () => {
    if (!showJsonEditor && currentRequest) {
      setJsonText(JSON.stringify(currentRequest, null, 2));
    }
    setShowJsonEditor(!showJsonEditor);
  };

  const handleJsonApply = () => {
    try {
      const parsed = JSON.parse(jsonText);
      if (!parsed.source_schema || !parsed.destination_schema) {
        throw new Error('Must include source_schema and destination_schema');
      }
      onRequestChange(parsed);
      setJsonError(null);
      setShowJsonEditor(false);
    } catch (err: any) {
      setJsonError(err.message || 'Invalid JSON format');
    }
  };

  return (
    <div className="card">
      <div className="card-header flex-between">
        <div>
          <h2 className="text-lg font-bold text-gray-800">1. Select Migration Scenario / Schema</h2>
          <p className="text-sm text-gray-500">
            Choose a canonical Product Bible §17 scenario or inspect the raw schema payload.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="btn btn-secondary text-xs"
            onClick={handleJsonToggle}
          >
            {showJsonEditor ? 'Close JSON Editor' : 'Edit Raw JSON'}
          </button>
          <button
            type="button"
            className="btn btn-primary font-semibold"
            onClick={onRunMigration}
            disabled={isLoading || !currentRequest}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="spinner"></span> Executing Agents...
              </span>
            ) : (
              'Run 5-Agent Migration Pipeline 🚀'
            )}
          </button>
        </div>
      </div>

      <div className="card-body">
        <div className="grid grid-3 gap-3 mb-4">
          {scenarios.map((s) => {
            const isSelected = s.id === selectedScenarioId;
            return (
              <div
                key={s.id}
                onClick={() => onSelectScenario(s)}
                className={`scenario-card ${isSelected ? 'scenario-card-active' : ''}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="badge badge-scenario font-semibold">{s.id.replace('_', ' ').toUpperCase()}</span>
                  {isSelected && <span className="text-xs text-primary font-bold">✓ Selected</span>}
                </div>
                <h4 className="font-bold text-sm text-gray-900 mb-1">{s.name}</h4>
                <p className="text-xs text-gray-600 mb-2 leading-relaxed">{s.description}</p>
                <div className="text-xs text-indigo-700 bg-indigo-50 p-2 rounded border border-indigo-100">
                  <strong>Expected:</strong> {s.expected_behavior}
                </div>
              </div>
            );
          })}
        </div>

        {showJsonEditor && (
          <div className="json-editor-container mb-4">
            <div className="flex-between mb-1">
              <span className="text-xs font-semibold text-gray-700">Custom Schema Payload (JSON)</span>
              {jsonError && <span className="text-xs text-red-600 font-semibold">{jsonError}</span>}
            </div>
            <textarea
              className="json-textarea"
              rows={10}
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
            />
            <div className="flex justify-end gap-2 mt-2">
              <button
                type="button"
                className="btn btn-secondary text-xs"
                onClick={() => setShowJsonEditor(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary text-xs"
                onClick={handleJsonApply}
              >
                Apply Custom JSON Schema
              </button>
            </div>
          </div>
        )}

        {currentRequest && (
          <div className="schema-summary-bar">
            <div className="summary-col">
              <span className="summary-label">Source Table</span>
              <span className="summary-val font-mono">{currentRequest.source_schema.table_name}</span>
              <span className="summary-sub">{currentRequest.source_schema.fields.length} fields</span>
            </div>
            <div className="summary-arrow">➔</div>
            <div className="summary-col">
              <span className="summary-label">Destination Table</span>
              <span className="summary-val font-mono">{currentRequest.destination_schema.table_name}</span>
              <span className="summary-sub">{currentRequest.destination_schema.fields.length} fields</span>
            </div>
            <div className="summary-divider"></div>
            <div className="summary-col">
              <span className="summary-label">Sample Data</span>
              <span className="summary-val">{currentRequest.sample_rows?.length || 0} rows</span>
            </div>
            <div className="summary-col">
              <span className="summary-label">Relationships</span>
              <span className="summary-val">
                {(currentRequest.relationship_metadata?.length || 0) +
                  (currentRequest.destination_schema.relationships?.length || 0)} defined
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
