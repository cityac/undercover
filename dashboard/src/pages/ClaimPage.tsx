import { ApiError } from "../api";
import { StateBadge } from "../components/Badges";
import { DecisionPanel } from "../components/DecisionPanel";
import { SignOffPanel } from "../components/SignOffPanel";
import { StepList } from "../components/StepList";
import type { Claim, Step } from "../types";
import { usePolling } from "../usePolling";
import { ClaimDetails, PolicyPanel } from "./ClaimDetails";

export function ClaimPage({ id }: Readonly<{ id: string }>) {
  const { data: claim, error } = usePolling<Claim>(`/claims/${id}`);
  const { data: steps } = usePolling<Step[]>(`/claims/${id}/steps`);
  if (error instanceof ApiError && error.status === 404)
    return <p className="error">Claim not found: {id}</p>;
  if (!claim) return <p className="muted">Loading {id}</p>;
  return (
    <>
      <h2>
        <span className="id">{claim.claim_id}</span>{" "}
        <StateBadge state={claim.state} />
      </h2>
      <div className="grid">
        <DecisionPanel claim={claim} />
        {claim.state === "waiting_for_sign_off" && (
          <SignOffPanel claim={claim} />
        )}
      </div>
      <div className="grid">
        <ClaimDetails claim={claim} />
        <PolicyPanel claim={claim} />
      </div>
      <StepList steps={steps ?? []} />
    </>
  );
}
