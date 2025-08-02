'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useCallback } from 'react'

type PriorityType = 1 | 2 | 3

export interface FilterParams {
  channel?: string
  date_range?: string
  priority?: PriorityType
  sort?: string
  view?: string
  page?: string
  [key: string]: string | number | undefined
}

export function useFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // Get current filter values from URL
  const filters: FilterParams = {
    channel: searchParams.get('channel') ?? undefined,
    date_range: searchParams.get('date_range') ?? undefined,
    priority: searchParams.get('priority') ? Number(searchParams.get('priority')) as PriorityType : undefined,
    sort: searchParams.get('sort') ?? undefined,
    view: searchParams.get('view') ?? undefined,
    page: searchParams.get('page') ?? undefined,
  }

  // Update a single filter
  const updateFilter = useCallback((key: string, value: string | number | null) => {
    const params = new URLSearchParams(searchParams.toString())

    if (value !== null && value !== undefined && value !== '') {
      params.set(key, String(value))
    } else {
      params.delete(key)
    }

    // Reset page when filters change (except when updating page itself)
    if (key !== 'page') {
      params.delete('page')
    }

    const queryString = params.toString()
    const url = queryString ? `${pathname}?${queryString}` : pathname

    router.push(url, { scroll: false })
  }, [searchParams, pathname, router])

  // Update multiple filters at once
  const updateFilters = useCallback((newFilters: Partial<FilterParams>) => {
    const params = new URLSearchParams(searchParams.toString())

    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.set(key, String(value))
      } else {
        params.delete(key)
      }
    })

    // Reset page when filters change
    if (!('page' in newFilters)) {
      params.delete('page')
    }

    const queryString = params.toString()
    const url = queryString ? `${pathname}?${queryString}` : pathname

    router.push(url, { scroll: false })
  }, [searchParams, pathname, router])

  // Clear all filters
  const clearFilters = useCallback(() => {
    router.push(pathname, { scroll: false })
  }, [pathname, router])

  // Clear specific filter
  const clearFilter = useCallback((key: string) => {
    updateFilter(key, null)
  }, [updateFilter])

  return {
    filters,
    updateFilter,
    updateFilters,
    clearFilters,
    clearFilter,
  }
}