import { useState } from "react";
import type { PriorityType } from "./use-filters";

// Custom hook for filter functionality
export const useUrgencyFilter = (initialValue: PriorityType | null = null) => {
  const [filter, setFilter] = useState(initialValue);

  const handleFilterChange = (value: PriorityType | null) => {
    setFilter(value);
  };

  return {
    filter,
    setFilter: handleFilterChange,
  };
};