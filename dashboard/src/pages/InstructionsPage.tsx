import { useEffect, useState } from "react";
import { api } from "../api";

export function InstructionsPage() {
  const [text, setText] = useState<string | null>(null);
  useEffect(() => {
    void api.instructions().then((body) => {
      setText(body.text);
    });
  }, []);
  return (
    <section className="panel" aria-label="Agent instructions">
      <h2>The agent's instructions</h2>
      <p className="muted">
        Read only. These are the instructions the agent works from.
      </p>
      {text === null ? (
        <p className="muted">Loading</p>
      ) : (
        <pre className="instructions">{text}</pre>
      )}
    </section>
  );
}
