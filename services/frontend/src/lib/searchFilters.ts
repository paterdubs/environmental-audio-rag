import type { Filters } from "../api/types";

export function cleanFilters(filters: Filters): Filters {
  const result: Filters = {};
  if (filters.classes_all?.length) result.classes_all = filters.classes_all;
  if (filters.temporal) result.temporal = filters.temporal;
  if (filters.duration) result.duration = filters.duration;
  return result;
}

export function hasFilters(filters: Filters): boolean {
  return Object.keys(cleanFilters(filters)).length > 0;
}
