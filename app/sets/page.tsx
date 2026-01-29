"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/PageShell";
import { apiFetch } from "@/lib/api";
import type { SetSummary } from "@/lib/types";

export default function SetsPage() {
  const router = useRouter();
  const [sets, setSets] = useState<SetSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cached = sessionStorage.getItem("artweave_sets");
    if (cached) {
      setSets(JSON.parse(cached) as SetSummary[]);
      setLoading(false);
      return;
    }

    const loadSets = async () => {
      try {
        const data = await apiFetch<SetSummary[]>("/api/sets");
        setSets(data);
        sessionStorage.setItem("artweave_sets", JSON.stringify(data));
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadSets();
  }, []);

  const handleSelect = (setId: string) => {
    sessionStorage.setItem("artweave_selected_set", setId);
    router.push("/paintings");
  };

  return (
    <PageShell backHref="/tutorial" homeHref="/">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-bold text-midnight">Choose the painting set</h1>
          <p className="mt-2 text-sm text-slate-500">
            Select a curated collection to begin comparing standout artworks.
          </p>
        </div>

        {loading ? (
          <div className="rounded-2xl bg-white p-8 text-center text-sm text-slate-400 shadow-soft">
            Loading sets...
          </div>
        ) : error ? (
          <div className="rounded-2xl bg-white p-6 text-sm text-rose-500 shadow-soft">
            {error}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {sets.map((set, index) => (
              <button
                key={set.set_id}
                type="button"
                onClick={() => handleSelect(set.set_id)}
                className="group flex flex-col overflow-hidden rounded-3xl border border-transparent bg-white shadow-soft transition hover:-translate-y-1 hover:border-indigo-200"
              >
                <div className="h-44 w-full bg-slate-100">
                  <div className="flex h-full w-full items-center justify-center text-sm text-slate-400">
                    Preview {index === 0 ? "A" : "B"}
                  </div>
                </div>
                <div className="flex flex-1 flex-col gap-1 px-6 py-5 text-left">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                    Set {index === 0 ? "A" : "B"}
                  </p>
                  <h2 className="text-lg font-semibold text-slate-800">{set.label}</h2>
                  <p className="text-sm text-slate-500">{set.count} paintings</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </PageShell>
  );
}