import { stepLabel, time } from "../format";
import type { Step } from "../types";

export function StepList({ steps }: Readonly<{ steps: Step[] }>) {
  return (
    <section className="panel" aria-label="Agent steps">
      <h2>Agent steps</h2>
      {steps.length === 0 ? (
        <p className="muted">No steps yet.</p>
      ) : (
        <ol className="steps">
          {steps.map((step) => (
            <li key={step.id}>
              <span className="mono muted">{time(step.created_at)}</span>
              <strong className={step.kind === "error" ? "error" : undefined}>
                {stepLabel[step.kind]}
              </strong>
              <span className="content">{step.content}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
