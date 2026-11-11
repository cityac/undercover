import "./styles.css";
import { ClaimPage } from "./pages/ClaimPage";
import { InstructionsPage } from "./pages/InstructionsPage";
import { QueuePage } from "./pages/QueuePage";
import { useRoute } from "./route";

export function App() {
  const route = useRoute();
  return (
    <>
      <header>
        <h1>UnderCover Claims</h1>
        <span className="tagline">Travel insurance, handled with care</span>
        <nav>
          <a href="#/">Queue</a>
          <a href="#/instructions">Agent instructions</a>
        </nav>
      </header>
      <main>
        {route.page === "queue" && <QueuePage />}
        {route.page === "claim" && <ClaimPage key={route.id} id={route.id} />}
        {route.page === "instructions" && <InstructionsPage />}
      </main>
    </>
  );
}
