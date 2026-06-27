import React from 'react';
import type { PipelineStage } from '../types';

export function DataPipeline({ stages }: { stages: PipelineStage[] }) {
  return (
    <div className="data-pipeline" data-testid="data-pipeline">
      {stages.map((stage, index) => (
        <React.Fragment key={stage.id}>
          <div className={`pipe-stage pipe-${stage.kind}`}>
            <b>{stage.label}</b>
            <span>{stage.detail}</span>
          </div>
          {index < stages.length - 1 && <span className="pipe-arrow" aria-hidden="true">↓</span>}
        </React.Fragment>
      ))}
    </div>
  );
}
