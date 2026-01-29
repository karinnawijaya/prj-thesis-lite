export interface SetSummary {
  set_id: string;
  label: string;
  count: number;
}

export interface Painting {
  id: string;
  title: string;
  artist: string;
  year: string | null;
  image_url: string | null;
  alt: string;
  metadata: Record<string, unknown> | null;
}

export interface CompareOverview {
  artworkA: Painting;
  artworkB: Painting;
}

export interface CompareResponse {
  overview: CompareOverview;
  summary: string;
}