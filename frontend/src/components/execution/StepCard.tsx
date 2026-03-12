"use client";

import React, { useState } from 'react';

export type Status = 'pending' | 'running' | 'completed' | 'failed';

export interface ExecutionStep {
  id: string;
  toolName: string;
  args: Record<string, unknown>;
  result?: unknown;
  status: Status;
  timestamp: Date;
  startTime?: Date;
  endTime?: Date;
  error?: string;
  details?: Record<string, unknown>;
}

interface StepCardProps {
  step: ExecutionStep;
  className?: string;
}

const StatusBadge: React.FC<{ status: Status }> = ({ status }) => {
  const statusStyles = {
    pending: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 animate-pulse',
    completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const StepCard: React.FC<StepCardProps> = ({ step, className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDuration = (start?: Date, end?: Date): string => {
    if (!start || !end) return '';
    const duration = (end.getTime() - start.getTime()) / 1000;
    return `${duration.toFixed(2)}s`;
  };

  const formatTimestamp = (date: Date): string => {
    return new Date(date).toLocaleString();
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 transition-all hover:shadow-lg ${className}`}>
      {/* Header: Tool name, status, timestamps */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {step.toolName}
          </h3>
          <div className="flex items-center space-x-3 mt-1">
            <StatusBadge status={step.status} />
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Started: {formatTimestamp(step.timestamp)}
            </span>
          </div>
        </div>
        {step.startTime && step.endTime && (
          <span className="text-sm font-mono text-gray-600 dark:text-gray-300">
            {formatDuration(step.startTime, step.endTime)}
          </span>
        )}
      </div>

      {/* Args section */}
      {step.args && Object.keys(step.args).length > 0 && (
        <div className="mb-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center"
          >
            {isExpanded ? 'Hide' : 'Show'} arguments ▾
          </button>
          {isExpanded && (
            <div className="mt-2 bg-gray-50 dark:bg-gray-900 rounded p-2">
              <pre className="text-xs font-mono text-gray-700 dark:text-gray-300 overflow-x-auto">
                {JSON.stringify(step.args, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Result or Error section */}
      {step.status === 'completed' && step.result !== undefined && (
        <div className="mt-3">
          <h4 className="text-sm font-medium text-green-700 dark:text-green-400 mb-1">Result</h4>
          <div className="bg-green-50 dark:bg-green-900/30 rounded p-2">
            <pre className="text-xs font-mono text-green-800 dark:text-green-300 overflow-x-auto">
              {JSON.stringify(step.result, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {step.status === 'failed' && step.error && (
        <div className="mt-3">
          <h4 className="text-sm font-medium text-red-700 dark:text-red-400 mb-1">Error</h4>
          <div className="bg-red-50 dark:bg-red-900/30 rounded p-2">
            <pre className="text-xs font-mono text-red-800 dark:text-red-300 overflow-x-auto">
              {step.error}
            </pre>
          </div>
        </div>
      )}

      {/* Additional details section */}
      {step.details && Object.keys(step.details).length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center"
          >
            {isExpanded ? 'Hide' : 'Show'} details ▾
          </button>
          {isExpanded && (
            <div className="mt-2 bg-gray-50 dark:bg-gray-900 rounded p-2">
              <pre className="text-xs font-mono text-gray-700 dark:text-gray-300 overflow-x-auto">
                {JSON.stringify(step.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Footer with end timestamp */}
      {step.endTime && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Completed: {formatTimestamp(step.endTime)}
          </span>
        </div>
      )}
    </div>
  );
};

export default StepCard;
