"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/PageShell";
import { PrimaryButton } from "@/components/PrimaryButton";
import { apiFetch } from "@/lib/api";
import { resolveImageUrl } from "@/lib/images";
import type { Painting, SetSummary } from "@/lib/types";

export default function TutorialPage() {
  const router = useRouter();
  const [heroPainting, setHeroPainting] = useState<Painting | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHero = async () => {
      try {
        const sets = await apiFetch<SetSummary[]>("/api/sets");
        if (!sets.length) {
          setHeroPainting(null);
          return;
        }
        const paintings = await apiFetch<Painting[]>(`/api/paintings?set_id=${sets[0].set_id}`);
        setHeroPainting(paintings[0] ?? null);
      } catch (error) {
        setHeroPainting(null);
      } finally {
        setLoading(false);
      }
    };

    loadHero();
  }, []);

  const resolvedImage = resolveImageUrl(heroPainting?.image_url ?? null);

  return (
    <PageShell backHref="/" homeHref="/">
      <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="relative overflow-hidden rounded-3xl bg-white shadow-soft">
          {loading ? (
            <div className="flex h-96 items-center justify-center bg-slate-100 text-sm text-slate-400">
              Loading preview...
            </div>
          ) : resolvedImage ? (
            <img
              src={resolvedImage}
              alt={heroPainting.alt || heroPainting.title}
              className="h-96 w-full object-cover"
            />
          ) : (
            <div className="flex h-96 items-center justify-center bg-slate-100 text-sm text-slate-400">
              Preview unavailable
            </div>
          )}
        </div>

        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-4xl font-bold text-midnight">ArtWeave</h1>
            <p className="mt-4 text-base text-slate-600">
              Compare two artworks in just a few taps. Select a set, pick your favorites, and receive a
              focused summary crafted for quick understanding.
            </p>
          </div>
          <PrimaryButton label="Next" onClick={() => router.push("/sets")} />
        </div>
      </div>
    </PageShell>
  );
}