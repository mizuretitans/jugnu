import type { RoadmapStep } from '../api/types';

export const Roadmap = ({ steps }: { steps: RoadmapStep[] }) =>
  steps.map((step) => (
    <details className="resource" key={step.title}>
      <summary>{step.title}</summary>
      <p>{step.text}</p>
    </details>
  ));
