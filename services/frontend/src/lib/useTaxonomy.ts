import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { api } from "../api/client";
import type { Language, TaxonomyClass } from "../api/types";
import { classColor } from "./timeline";

export interface TaxonomyView {
  classes: TaxonomyClass[];
  order: string[];
  name: (classId: string, language: Language) => string;
  color: (classId: string) => string;
}

/** Class list, names and colours come from the API — the frontend declares no taxonomy. */
export function useTaxonomy(): TaxonomyView | undefined {
  const query = useQuery({ queryKey: ["taxonomy"], queryFn: api.taxonomy, staleTime: Infinity });
  return useMemo(() => {
    if (!query.data) return undefined;
    const classes = query.data.classes;
    const byId = new Map(classes.map((c, index) => [c.class_id, { ...c, index }]));
    return {
      classes,
      order: classes.map((c) => c.class_id),
      name: (id, language) => {
        const entry = byId.get(id);
        return entry ? (language === "vi" ? entry.label_vi : entry.label_en) : id;
      },
      color: (id) => classColor(byId.get(id)?.index ?? 0),
    };
  }, [query.data]);
}
