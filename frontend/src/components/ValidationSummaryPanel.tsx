import React from 'react';
import type { ValidationResult } from '../api/client';

interface ValidationSummaryPanelProps {
  validationResult: ValidationResult | null;
}

export const ValidationSummaryPanel: React.FC<ValidationSummaryPanelProps> = ({
  validationResult,
}) => {
  if (!validationResult) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-md font-bold text-gray-800">5. Validation Summary</h3>
          <p className="text-xs text-gray-500">Awaiting workflow run.</p>
        </div>
        <div className="card-body text-center py-6 text-gray-400 text-xs">
          No validation checks performed yet.
        </div>
      </div>
    );
  }

  const { all_valid, items, blocking_issues, warning_issues } = validationResult;

  return (
    <div className="card">
      <div className="card-header flex-between">
        <div>
          <h3 className="text-md font-bold text-gray-800">5. Validation & Constraint Summary</h3>
          <p className="text-xs text-gray-500">
            Rules 4 & 5 constraint verification (Product Bible §8 & §12).
          </p>
        </div>
        <span
          className={`badge font-bold text-xs ${
            all_valid ? 'badge-success' : 'badge-error'
          }`}
        >
          {all_valid ? '✓ ALL CHECKS PASSED' : '✕ CONFLICTS DETECTED'}
        </span>
      </div>

      <div className="card-body">
        {blocking_issues.length > 0 && (
          <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded text-xs text-red-800">
            <strong className="block font-bold text-red-900 mb-1">
              🚨 Blocking Issues ({blocking_issues.length}):
            </strong>
            <ul className="list-disc pl-4 space-y-1">
              {blocking_issues.map((issue, idx) => (
                <li key={idx} className="font-medium">
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {warning_issues.length > 0 && (
          <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
            <strong className="block font-bold text-amber-900 mb-1">
              ⚠️ Warnings ({warning_issues.length}):
            </strong>
            <ul className="list-disc pl-4 space-y-1">
              {warning_issues.map((warn, idx) => (
                <li key={idx}>{warn}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="space-y-2 mt-2">
          {items.map((item, idx) => {
            const isPass = item.status === 'PASS';
            const isFail = item.status === 'FAIL';
            return (
              <div
                key={idx}
                className={`p-2.5 rounded border text-xs flex items-start gap-2.5 ${
                  isPass
                    ? 'bg-emerald-50/40 border-emerald-100'
                    : isFail
                    ? 'bg-red-50/60 border-red-200'
                    : 'bg-amber-50/40 border-amber-100'
                }`}
              >
                <span
                  className={`mt-0.5 font-bold ${
                    isPass
                      ? 'text-emerald-600'
                      : isFail
                      ? 'text-rose-600'
                      : 'text-amber-600'
                  }`}
                >
                  {isPass ? '✓' : isFail ? '✕' : '⚠'}
                </span>
                <div className="flex-1">
                  <div className="flex-between mb-0.5">
                    <span className="font-mono font-bold text-gray-800">
                      {item.field_name}
                    </span>
                    <span className="text-2xs text-gray-500 font-mono">
                      {item.check_type} • {item.rule_applied}
                    </span>
                  </div>
                  <p className="text-gray-600">{item.message}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
