import { useEffect, useState } from "react";

export type Route =
  { page: "queue" } | { page: "claim"; id: string } | { page: "instructions" };

export function parse(hash: string): Route {
  const path = hash.replace(/^#\/?/, "");
  if (path === "instructions") return { page: "instructions" };
  const claim = /^claims\/(.+)$/.exec(path);
  if (claim?.[1]) return { page: "claim", id: decodeURIComponent(claim[1]) };
  return { page: "queue" };
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parse(window.location.hash));
  useEffect(() => {
    const update = () => {
      setRoute(parse(window.location.hash));
    };
    window.addEventListener("hashchange", update);
    return () => {
      window.removeEventListener("hashchange", update);
    };
  }, []);
  return route;
}
