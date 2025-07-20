'use client';

/**
 * Validation utilities to prevent component errors
 */

// Validate Select component value to prevent empty string errors
export function validateSelectValue(value: string | undefined | null): string {
  if (!value || value === '') {
    return '__none__';
  }
  return value;
}

// Convert special placeholder back to actual value
export function normalizeSelectValue(value: string): string | undefined {
  if (value === '__none__') {
    return undefined;
  }
  return value;
}

// Validate form data to prevent runtime errors
export function validateFormData<T extends Record<string, any>>(
  data: T,
  requiredFields: (keyof T)[] = []
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check required fields
  for (const field of requiredFields) {
    if (!data[field] || data[field] === '') {
      errors.push(`${String(field)} is required`);
    }
  }
  
  // Check for common problematic values
  Object.entries(data).forEach(([key, value]) => {
    if (typeof value === 'string') {
      // Prevent XSS attempts
      if (value.includes('<script') || value.includes('javascript:')) {
        errors.push(`${key} contains invalid characters`);
      }
      
      // Check for extremely long values that might cause UI issues
      if (value.length > 10000) {
        errors.push(`${key} is too long (max 10000 characters)`);
      }
    }
  });
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// Safe number parsing with fallback
export function safeParseInt(value: string | number | undefined, fallback = 0): number {
  if (typeof value === 'number') {
    return isNaN(value) ? fallback : value;
  }
  
  if (typeof value === 'string') {
    const parsed = parseInt(value, 10);
    return isNaN(parsed) ? fallback : parsed;
  }
  
  return fallback;
}

// Safe string coercion
export function safeString(value: any, fallback = ''): string {
  if (value === null || value === undefined) {
    return fallback;
  }
  
  if (typeof value === 'string') {
    return value;
  }
  
  try {
    return String(value);
  } catch {
    return fallback;
  }
}

// Validate API response structure
export function validateApiResponse<T>(
  response: any,
  expectedKeys: string[] = []
): response is T {
  if (!response || typeof response !== 'object') {
    return false;
  }
  
  // Check for expected keys
  for (const key of expectedKeys) {
    if (!(key in response)) {
      console.warn(`Missing expected key in API response: ${key}`);
      return false;
    }
  }
  
  return true;
}