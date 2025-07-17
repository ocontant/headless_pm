import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Test connection to the main API
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969';
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    
    let apiStatus = 'unknown';
    let apiReachable = false;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch(`${apiUrl}/health`, {
        signal: controller.signal,
        headers: apiKey ? { 'X-API-Key': apiKey } : {}
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        apiStatus = 'healthy';
        apiReachable = true;
      } else {
        apiStatus = `unhealthy: ${response.status}`;
        apiReachable = false;
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        apiStatus = 'timeout';
      } else {
        apiStatus = `unreachable: ${error.message}`;
      }
      apiReachable = false;
    }
    
    // Check environment variables
    const envStatus = {
      api_url: !!process.env.NEXT_PUBLIC_API_URL,
      api_key: !!process.env.NEXT_PUBLIC_API_KEY,
      node_env: process.env.NODE_ENV || 'unknown'
    };
    
    const overallStatus = apiReachable ? 'healthy' : 'degraded';
    
    return NextResponse.json({
      status: overallStatus,
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      api_backend: apiStatus,
      api_url: apiUrl,
      environment: envStatus,
      timestamp: new Date().toISOString()
    });
    
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      error: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}

export async function HEAD() {
  // For simple health checks that just need a status code
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969';
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const response = await fetch(`${apiUrl}/health`, {
      signal: controller.signal,
      headers: apiKey ? { 'X-API-Key': apiKey } : {}
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      return new NextResponse(null, { status: 200 });
    } else {
      return new NextResponse(null, { status: 503 });
    }
    
  } catch (error) {
    return new NextResponse(null, { status: 503 });
  }
}