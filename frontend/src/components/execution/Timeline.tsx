"use client";

import React from 'react';
import StepCard, { ExecutionStep, Status } from './StepCard';

interface TimelineProps {
  steps: ExecutionStep[];
  className?: string;
}

const Timeline: React.FC<TimelineProps> = ({ steps, className = '' }) => {
  return (
    <div className={`relative ${className}`}>
      {/* Vertical connector line */}
      <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-700"></div>
      
      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={step.id} className="relative pl-20">
            {/* Status dot on the connector line */}
            <div className={`absolute left-5 top-6 w-4 h-4 rounded-full border-2 ${
              step.status === 'completed' ? 'bg-green-500 border-green-600' :
              step.status === 'running' ? 'bg-blue-500 border-blue-600' :
              step.status === 'failed' ? 'bg-red-500 border-red-600' :
              'bg-gray-400 border-gray-500'
            }`}></div>
            
            <StepCard step={step} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline;
