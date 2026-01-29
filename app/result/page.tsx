"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/PageShell";
import { PrimaryButton } from "@/components/PrimaryButton";
import { apiFetch } from "@/lib/api";
import type { CompareResponse } from "@/lib/types";

export default function ResultPage() {
  const router = useRouter();
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selectedIds = useMemo(() => {
    if (typeof window === "undefined") return [] as string[];
    const stored = sessionStorage.getItem("artweave_selected_paintings");
    return stored ? (JSON.parse(stored) as string[]) : [];
  }, []);

  const runCompare = useCallback(async () => {
    if (selectedIds.length !== 2) {
      router.replace("/paintings");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiFetch<CompareResponse>("/api/compare", {
        method: "POST",
        body: JSON.stringify({
          painting_a_id: selectedIds[0],
          painting_b_id: selectedIds[1],
        }),
      });
      setData(response);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [router, selectedIds]);

  useEffect(() => {
    runCompare();
  }, [runCompare]);

  return (
    <PageShell backHref="/paintings" homeHref="/">
      <div className="flex flex-col gap-10">
        <div>
          <h1 className="text-3xl font-bold text-midnight">Comparison Summary</h1>
          <p className="mt-2 text-sm text-slate-500">A concise overview of your selected artworks.</p>
        </div>

        {loading ? (
          <div className="rounded-2xl bg-white p-8 text-center text-sm text-slate-400 shadow-soft">
            Generating summary...
          </div>
        ) : error ? (
          <div className="flex flex-col items-center gap-4 rounded-2xl bg-white p-8 text-center text-sm text-rose-500 shadow-soft">
            <p>{error}</p>
            <PrimaryButton label="Try again" onClick={runCompare} />
          </div>
        ) : data ? (
          <div className="flex flex-col gap-8">
            <section className="rounded-3xl bg-white p-6 shadow-soft">
              <h2 className="text-xl font-semibold text-slate-800">Summary</h2>
              <p className="mt-4 text-sm leading-relaxed text-slate-600">{data.summary}</p>
            </section>
          </div>
        ) : null}
      </div>
    </PageShell>
  );
}