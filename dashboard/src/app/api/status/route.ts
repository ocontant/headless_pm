import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Test connection to the main API with detailed info
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969';
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    
    let apiDetails: any = {};
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const startTime = Date.now();
      const response = await fetch(`${apiUrl}/health`, {
        signal: controller.signal,
        headers: apiKey ? { 'X-API-Key': apiKey } : {}
      });
      const endTime = Date.now();
      
      clearTimeout(timeoutId);
      
      apiDetails = {
        reachable: true,
        status_code: response.status,
        response_time_ms: endTime - startTime,
        url: `${apiUrl}/health`
      };
      
      if (response.ok) {
        const data = await response.json();
        apiDetails.content = data;
        apiDetails.status = 'healthy';
      } else {
        apiDetails.status = 'unhealthy';
      }
      
    } catch (error: any) {
      apiDetails = {
        reachable: false,
        error: error.name === 'AbortError' ? 'timeout' : error.message,
        status: 'unreachable',
        url: `${apiUrl}/health`
      };
    }
    
    // Check MCP server if configured
    let mcpDetails: any = {};
    const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL || 'http://localhost:6968';
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const startTime = Date.now();
      const response = await fetch(`${mcpUrl}/health`, {
        signal: controller.signal
      });
      const endTime = Date.now();
      
      clearTimeout(timeoutId);
      
      mcpDetails = {
        reachable: true,
        status_code: response.status,
        response_time_ms: endTime - startTime,
        url: `${mcpUrl}/health`
      };
      
      if (response.ok) {
        const data = await response.json();
        mcpDetails.content = data;
        mcpDetails.status = 'healthy';
      } else {
        mcpDetails.status = 'unhealthy';
      }
      
    } catch (error: any) {
      mcpDetails = {
        reachable: false,
        error: error.name === 'AbortError' ? 'timeout' : error.message,
        status: 'unreachable',
        url: `${mcpUrl}/health`
      };
    }
    
    // Environment details
    const environment = {
      node_env: process.env.NODE_ENV || 'unknown',
      next_version: process.env.npm_package_version || 'unknown',
      api_url: apiUrl,
      mcp_url: mcpUrl,
      has_api_key: !!apiKey,
      build_time: process.env.BUILD_TIME || 'unknown',
      deployment: process.env.VERCEL_ENV || 'local'
    };
    
    // Overall status
    const overallStatus = apiDetails.reachable && apiDetails.status === 'healthy' ? 'healthy' : 'degraded';
    
    return NextResponse.json({
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      status: overallStatus,
      dependencies: {
        api_backend: apiDetails,
        mcp_server: mcpDetails
      },
      environment: environment,
      timestamp: new Date().toISOString()
    });
    
  } catch (error: any) {
    return NextResponse.json({
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}