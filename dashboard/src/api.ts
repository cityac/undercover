import type { Claim, Customer, Handler, Policy } from "./types";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {
      detail?: unknown;
    };
    const detail =
      typeof body.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

function post<T>(path: string, body: object): Promise<T> {
  return get<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  policy: (id: string) => get<Policy>(`/policies/${id}`),
  customer: (id: string) => get<Customer>(`/customers/${id}`),
  handlers: () => get<Handler[]>("/handlers"),
  instructions: () => get<{ text: string }>("/instructions"),
  signOff: (id: string, handlerId: string) =>
    post<Claim>(`/claims/${id}/sign-off`, { handler_id: handlerId }),
};
