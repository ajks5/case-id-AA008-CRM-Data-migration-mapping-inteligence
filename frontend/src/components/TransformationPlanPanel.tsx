import React from 'react';
import type { TransformationAction } from '../api/client';

interface TransformationPlanPanelProps {
  transformationPlan: TransformationAction[] | null;
}

export const TransformationPlanPanel: React.FC<TransformationPlanPanelProps> = ({
  transformationPlan,
}) => {
  if (!transformationPlan || transformationPlan.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-md font-bold text-gray-800">4. Transformation Plan</h3>
          <p className="text-xs text-gray-500">Awaiting workflow run.</p>
        </div>
        <div className="card-body text-center py-6 text-gray-400 text-xs">
          No transformation plan generated yet.
        </div>
      </div>
    );
  }

  const activeTransforms = transformationPlan.filter(
    (t) => t.action_type === 'TYPE_CAST' || t.action_type === 'DEFAULT_VALUE'
  );

  return (
    <div className="card">
      <div className="card-header flex-between">
        <div>
          <h3 className="text-md font-bold text-gray-800">4. Transformation Plan & Data Preview</h3>
          <p className="text-xs text-gray-500">
            Rule 3 Type Casts & Default Value Normalizations (Product Bible §8 & §12).
          </p>
        </div>
        <span className="badge badge-info text-xs">
          {activeTransforms.length} Active Transforms
        </span>
      </div>

      <div className="card-body">
        <div className="space-y-3">
          {transformationPlan.map((item) => {
            const isCast = item.action_type === 'TYPE_CAST';
            const isDefault = item.action_type === 'DEFAULT_VALUE';
            const isNoop = item.action_type === 'NO_OP';

            return (
              <div
                key={item.destination_field}
                className={`p-3 rounded border text-xs ${
                  isCast
                    ? 'bg-blue-50/60 border-blue-200'
                    : isDefault
                    ? 'bg-purple-50/60 border-purple-200'
                    : 'bg-gray-50/60 border-gray-200'
                }`}
              >
                <div className="flex-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-gray-900">
                      {item.destination_field}
                    </span>
                    {item.source_field && (
                      <span className="text-gray-500">
                        ← <span className="font-mono text-gray-700">{item.source_field}</span>
                      </span>
                    )}
                  </div>
                  <span
                    className={`badge ${
                      isCast
                        ? 'badge-info'
                        : isDefault
                        ? 'badge-purple'
                        : isNoop
                        ? 'badge-neutral'
                        : 'badge-error'
                    }`}
                  >
                    {item.action_type}
                  </span>
                </div>

                <div className="text-gray-700 mb-2">{item.details}</div>

                {(item.sample_before !== undefined || item.sample_after !== undefined) && (
                  <div className="grid grid-2 gap-2 bg-white p-2 rounded border border-gray-200 font-mono text-xs">
                    <div>
                      <span className="text-2xs uppercase text-gray-400 font-bold block">
                        Sample Input:
                      </span>
                      <span className="text-gray-800">
                        {item.sample_before !== null && item.sample_before !== undefined
                          ? String(item.sample_before)
                          : 'null'}
                      </span>
                    </div>
                    <div>
                      <span className="text-2xs uppercase text-indigo-500 font-bold block">
                        Transformed Output:
                      </span>
                      <span className="text-indigo-700 font-semibold">
                        {item.sample_after !== null && item.sample_after !== undefined
                          ? String(item.sample_after)
                          : 'null'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
