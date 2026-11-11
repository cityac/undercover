import { useEffect, useState } from "react";
import { api } from "../api";
import { money } from "../format";
import type { Claim, Handler } from "../types";

export function SignOffPanel({ claim }: Readonly<{ claim: Claim }>) {
  const [handlers, setHandlers] = useState<Handler[]>([]);
  const [handlerId, setHandlerId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void api.handlers().then((list) => {
      setHandlers(list.filter((h) => h.can_approve_over_limit));
    });
  }, []);

  const signOff = () => {
    setBusy(true);
    setError("");
    api
      .signOff(claim.claim_id, handlerId)
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        setBusy(false);
      });
  };

  return (
    <section className="panel" aria-label="Sign-off">
      <h2>Sign-off</h2>
      <p>
        The payout of{" "}
        <span className="mono">{money(claim.decision?.payout ?? "0")}</span> is
        over the $1,000.00 limit and waits for a handler. Sign-off releases the
        payment; it does not change the decision.
      </p>
      <div className="sign-off">
        <label>
          Handler{" "}
          <select
            value={handlerId}
            onChange={(e) => {
              setHandlerId(e.target.value);
            }}
          >
            <option value="">Choose your name</option>
            {handlers.map((h) => (
              <option key={h.handler_id} value={h.handler_id}>
                {h.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" disabled={!handlerId || busy} onClick={signOff}>
          Sign off and pay
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </section>
  );
}
