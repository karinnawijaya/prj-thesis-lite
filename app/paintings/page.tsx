"use client";

import Link from "next/link";
import { PageShell } from "@/components/PageShell";
import { PrimaryButton } from "@/components/PrimaryButton";

const floatingPaintings = [
  {
    id: "floating-1",
    title: "Midnight Garden",
    image: "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=400&q=80",
  },
  {
    id: "floating-2",
    title: "Cloudline",
    image: "https://images.unsplash.com/photo-1473197452165-7abc4b248905?auto=format&fit=crop&w=400&q=80",
  },
  {
    id: "floating-3",
    title: "Soft Bloom",
    image: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=400&q=80",
  },
];

export default function LandingPage() {
  return (
    <PageShell showNav={false}>
      <div className="relative flex flex-1 flex-col items-center justify-center gap-10 py-10">
        <div className="absolute inset-0 -z-10 flex items-center justify-center">
          <div className="app-gradient h-full w-full" />
        </div>

        <div className="absolute inset-0 -z-10 hidden md:block">
          {floatingPaintings.map((painting, index) => (
            <div
              key={painting.id}
              className={`absolute w-40 rounded-2xl border border-white/70 bg-white/80 p-2 shadow-soft transition hover:-translate-y-1 ${
                index === 0
                  ? "left-[10%] top-[20%]"
                  : index === 1
                    ? "right-[12%] top-[25%]"
                    : "left-[20%] bottom-[18%]"
              }`}
            >
              <img
                src={painting.image}
                alt={painting.title}
                className="h-24 w-full rounded-xl object-cover"
              />
              <p className="mt-2 text-xs font-semibold text-slate-600">{painting.title}</p>
            </div>
          ))}
        </div>

        <div className="text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Welcome to</p>
          <h1 className="mt-4 text-5xl font-bold text-midnight md:text-6xl">ArtWeave</h1>
          <p className="mt-4 max-w-xl text-base text-slate-600">
            Explore quick comparisons between artworks and discover concise, curated summaries.
          </p>
        </div>

        <Link href="/tutorial">
          <PrimaryButton label="Let’s Begin" />
        </Link>
      </div>
    </PageShell>
  );
}
