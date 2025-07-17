'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';
import { ThemeProvider } from '@/lib/theme-provider';
import { ProjectProvider } from '@/lib/contexts/project-context';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000, // 30 seconds (reduced for better real-time updates)
            refetchOnWindowFocus: false,
            refetchOnMount: true, // Allow refetch on mount to start polling
            retry: 1, // Reduce retry attempts
            retryDelay: 1000, // 1 second retry delay
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="headless-pm-theme">
        <ProjectProvider>
          {children}
        </ProjectProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}