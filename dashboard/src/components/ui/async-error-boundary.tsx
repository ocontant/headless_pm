'use client';

import React, { useEffect, useState } from 'react';
import { ErrorBoundary } from '@/components/error-boundary';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface AsyncErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error) => void;
}

interface AsyncErrorState {
  hasAsyncError: boolean;
  error?: Error;
}

/**
 * Component to handle async errors that don't get caught by React Error Boundaries
 * such as Promise rejections, API errors, etc.
 */
export function AsyncErrorBoundary({ children, fallback, onError }: AsyncErrorBoundaryProps) {
  const [asyncError, setAsyncError] = useState<AsyncErrorState>({ hasAsyncError: false });

  useEffect(() => {
    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      const error = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
      setAsyncError({ hasAsyncError: true, error });
      onError?.(error);
      
      // Prevent the default browser handling
      event.preventDefault();
    };

    // Handle global errors
    const handleError = (event: ErrorEvent) => {
      console.error('Global error:', event.error);
      const error = event.error instanceof Error ? event.error : new Error(event.message);
      setAsyncError({ hasAsyncError: true, error });
      onError?.(error);
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, [onError]);

  const handleRetry = () => {
    setAsyncError({ hasAsyncError: false });
  };

  if (asyncError.hasAsyncError) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100">
            <AlertCircle className="h-6 w-6 text-yellow-600" />
          </div>
          <CardTitle className="text-yellow-900">Network Error</CardTitle>
          <CardDescription>
            A network or async operation failed. This might be temporary.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {process.env.NODE_ENV === 'development' && asyncError.error && (
            <div className="rounded-md bg-yellow-50 p-3">
              <div className="text-sm font-medium text-yellow-800 mb-2">Error Details:</div>
              <div className="text-xs text-yellow-700 font-mono overflow-auto max-h-32">
                {asyncError.error.toString()}
              </div>
            </div>
          )}
          <Button 
            onClick={handleRetry} 
            variant="outline" 
            className="w-full"
            size="sm"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <ErrorBoundary fallback={fallback} onError={onError}>
      {children}
    </ErrorBoundary>
  );
}

// Hook to manually trigger async errors
export function useAsyncError() {
  const [, setError] = useState<Error | null>(null);
  
  return (error: Error) => {
    setError(() => {
      throw error;
    });
  };
}