import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-sm">
        <div className="font-display text-9xl text-ink-400/30 leading-none mb-4">
          404
        </div>
        <div className="eyebrow mb-2">Off the ledger</div>
        <h1 className="font-display text-3xl tracking-tightest mb-6">
          We don't have a record of that page.
        </h1>
        <Link to="/" className="btn-primary">
          Back to overview
        </Link>
      </div>
    </div>
  );
}
