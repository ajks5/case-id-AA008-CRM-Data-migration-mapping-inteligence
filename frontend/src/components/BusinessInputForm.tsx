import React, { useState } from 'react';
import type { MigrationRequest, ScenarioItem } from '../api/client';

interface BusinessInputFormProps {
  scenarios: ScenarioItem[];
  selectedScenarioId: string;
  currentRequest: MigrationRequest | null;
  isLoadingExamples: boolean;
  isSubmitting: boolean;
  onSelectScenario: (scenario: ScenarioItem) => void;
  onRequestChange: (request: MigrationRequest) => void;
  onRunAssessment: () => void;
  onRetryExamples: () => void;
}

const scenarioCopy: Record<string, { title: string; description: string; focus: string }> = {
  simple_schema: {
    title: 'Standard contact records',
    description: 'The source and destination mostly use matching field names and compatible types.',
    focus: 'Review a high-coverage mapping plan.',
  },
  naming_mismatch: {
    title: 'Legacy field names',
    description: 'The source uses older abbreviations and a different date format.',
    focus: 'Review suggested matches and the date conversion.',
  },
  relationship_mismatch: {
    title: 'Missing account relationship',
    description: 'The destination requires an account link that is not present in the source.',
    focus: 'Identify the relationship that needs analyst attention.',
  },
};

function scenarioDetails(scenario: ScenarioItem) {
  return scenarioCopy[scenario.id] ?? {
    title: scenario.name.replace(/^Scenario\s*\d+\s*:\s*/i, ''),
    description: scenario.description,
    focus: 'Review the suggested field matches and any items that need attention.',
  };
}

export const BusinessInputForm: React.FC<BusinessInputFormProps> = ({
  scenarios,
  selectedScenarioId,
  currentRequest,
  isLoadingExamples,
  isSubmitting,
  onSelectScenario,
  onRequestChange,
  onRunAssessment,
  onRetryExamples,
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [jsonText, setJsonText] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [customApplied, setCustomApplied] = useState(false);

  const openCustomInput = () => {
    if (!showCustomInput && currentRequest) {
      setJsonText(JSON.stringify(currentRequest, null, 2));
    }
    setJsonError(null);
    setShowCustomInput((visible) => !visible);
  };

  const applyCustomInput = () => {
    try {
      const parsed = JSON.parse(jsonText) as Partial<MigrationRequest>;
      const source = parsed.source_schema;
      const destination = parsed.destination_schema;
      if (
        !source || typeof source.table_name !== 'string' || !Array.isArray(source.fields) ||
        !destination || typeof destination.table_name !== 'string' || !Array.isArray(destination.fields)
      ) {
        throw new Error('Include source_schema and destination_schema with a table name and fields list.');
      }

      const request: MigrationRequest = {
        source_schema: source,
        destination_schema: destination,
        sample_rows: Array.isArray(parsed.sample_rows) ? parsed.sample_rows : [],
        relationship_metadata: Array.isArray(parsed.relationship_metadata)
          ? parsed.relationship_metadata
          : [],
        known_mapping_hints:
          parsed.known_mapping_hints && typeof parsed.known_mapping_hints === 'object'
            ? parsed.known_mapping_hints
            : {},
      };

      onRequestChange(request);
      setCustomApplied(true);
      setJsonError(null);
      setShowCustomInput(false);
    } catch (error) {
      setJsonError(error instanceof Error ? error.message : 'Check the schema details and try again.');
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onRunAssessment();
  };

  const chooseScenario = (scenario: ScenarioItem) => {
    setCustomApplied(false);
    onSelectScenario(scenario);
  };

  return (
    <form className="product-panel product-input-panel" onSubmit={handleSubmit} aria-busy={isSubmitting}>
      <div className="product-panel-heading">
        <div>
          <h2 id="input-heading">Choose a schema pair</h2>
          <p>Start with a sample CRM migration or provide your own schema request.</p>
        </div>
        {currentRequest && (
          <span className="product-soft-label">
            {customApplied || selectedScenarioId === 'custom' ? 'Custom schema pair' : 'Sample schema pair'}
          </span>
        )}
      </div>

      {isLoadingExamples ? (
        <div className="product-empty-inline" role="status">Loading sample schema pairs…</div>
      ) : scenarios.length === 0 ? (
        <div className="product-empty-inline" role="status">
          <p>Sample schema pairs are unavailable right now.</p>
          <button className="product-button product-button-secondary" type="button" onClick={onRetryExamples}>
            Try again
          </button>
        </div>
      ) : (
        <fieldset className="product-scenario-fieldset" aria-labelledby="input-heading">
          <legend className="product-sr-only">Available CRM schema pairs</legend>
          <div className="product-scenario-list">
            {scenarios.map((scenario) => {
              const copy = scenarioDetails(scenario);
              const selected = selectedScenarioId === scenario.id;
              return (
                <label
                  key={scenario.id}
                  className={`product-scenario-option${selected ? ' is-selected' : ''}`}
                  htmlFor={`scenario-${scenario.id}`}
                >
                  <input
                    id={`scenario-${scenario.id}`}
                    type="radio"
                    name="schema-scenario"
                    value={scenario.id}
                    checked={selected}
                    onChange={() => chooseScenario(scenario)}
                  />
                  <span className="product-scenario-copy">
                    <span className="product-scenario-title">{copy.title}</span>
                    <span className="product-scenario-description">{copy.description}</span>
                    <span className="product-scenario-focus">{copy.focus}</span>
                  </span>
                  <span className="product-scenario-check" aria-hidden="true">{selected ? 'Selected' : ''}</span>
                </label>
              );
            })}
          </div>
        </fieldset>
      )}

      {currentRequest && (
        <div className="product-schema-summary" aria-label="Selected schema pair details">
          <div>
            <span className="product-summary-label">Source</span>
            <strong>{currentRequest.source_schema.table_name}</strong>
            <span>{currentRequest.source_schema.fields.length} fields</span>
          </div>
          <span className="product-schema-arrow" aria-hidden="true">→</span>
          <div>
            <span className="product-summary-label">Destination</span>
            <strong>{currentRequest.destination_schema.table_name}</strong>
            <span>{currentRequest.destination_schema.fields.length} fields</span>
          </div>
          <div className="product-summary-extra">
            <span>{currentRequest.sample_rows?.length ?? 0} sample rows</span>
            <span>{(currentRequest.relationship_metadata?.length ?? 0) + (currentRequest.destination_schema.relationships?.length ?? 0)} relationships</span>
          </div>
        </div>
      )}

      <details
        className="product-custom-input"
        open={showCustomInput}
        onToggle={(event) => setShowCustomInput(event.currentTarget.open)}
      >
        <summary onClick={(event) => { event.preventDefault(); openCustomInput(); }}>
          Use a custom schema request <span>Advanced JSON</span>
        </summary>
        <div className="product-custom-input-body">
          <p>Paste a request containing source_schema and destination_schema. Sample rows, relationships, and mapping hints are optional.</p>
          <label className="product-sr-only" htmlFor="custom-schema-json">Custom schema request JSON</label>
          <textarea
            id="custom-schema-json"
            className="product-json-input"
            rows={9}
            spellCheck={false}
            value={jsonText}
            onChange={(event) => setJsonText(event.target.value)}
            aria-describedby={jsonError ? 'custom-schema-error' : 'custom-schema-help'}
          />
          <p id="custom-schema-help" className="product-field-help">The request is sent to the existing mapping assessment workflow.</p>
          {jsonError && <p id="custom-schema-error" className="product-field-error" role="alert">{jsonError}</p>}
          <div className="product-inline-actions">
            <button className="product-button product-button-secondary" type="button" onClick={openCustomInput}>Cancel</button>
            <button className="product-button product-button-secondary" type="button" onClick={applyCustomInput}>Apply schema pair</button>
          </div>
        </div>
      </details>

      <div className="product-form-footer">
        <p>Creates a recommendation for review. It does not change CRM records.</p>
        <button className="product-button product-button-primary" type="submit" disabled={!currentRequest || isSubmitting || isLoadingExamples}>
          {isSubmitting ? 'Preparing recommendation…' : 'Generate mapping recommendation'}
        </button>
      </div>
    </form>
  );
};
