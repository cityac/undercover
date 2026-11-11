import { useEffect, useState } from "react";
import { get } from "./api";

export const POLL_MS = 5000;

export interface Polled<T> {
  data: T | null;
  error: Error | null;
}

export function usePolling<T>(path: string): Polled<T> {
  const [state, setState] = useState<Polled<T>>({ data: null, error: null });
  useEffect(() => {
    let active = true;
    const tick = () => {
      get<T>(path)
        .then((data) => {
          if (active) setState({ data, error: null });
        })
        .catch((error: unknown) => {
          if (active)
            setState((previous) => ({
              data: previous.data,
              error: error instanceof Error ? error : new Error(String(error)),
            }));
        });
    };
    tick();
    const timer = setInterval(tick, POLL_MS);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [path]);
  return state;
}
