import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Define service URLs
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969';
    const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL || 'http://localhost:6968';
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    
    // Helper function to fetch dependency health
    async function fetchDependencyHealth(url: string, serviceName: string) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const response = await fetch(`${url}/health`, {
          signal: controller.signal,
          headers: apiKey ? { 'X-API-Key': apiKey } : {}
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          const data = await response.json();
          // Remove depends_on to avoid recursive loops
          if (data.depends_on) {
            delete data.depends_on;
          }
          return data;
        } else {
          return {
            status: 'unhealthy',
            service: serviceName,
            error: `HTTP ${response.status}`
          };
        }
      } catch (error: any) {
        return {
          status: 'unreachable',
          service: serviceName,
          error: error.name === 'AbortError' ? 'timeout' : error.message
        };
      }
    }
    
    // Get dependency health status (API and MCP servers)
    const [apiDependency, mcpDependency] = await Promise.all([
      fetchDependencyHealth(apiUrl, 'headless-pm-api'),
      fetchDependencyHealth(mcpUrl, 'headless-pm-mcp-sse')
    ]);
    
    // Determine overall status based on dependencies
    const apiHealthy = apiDependency.status === 'healthy';
    const mcpHealthy = mcpDependency.status === 'healthy';
    const overallStatus = apiHealthy && mcpHealthy ? 'healthy' : 'degraded';
    
    return NextResponse.json({
      status: overallStatus,
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      pid: process.pid,
      timestamp: new Date().toISOString(),
      depends_on: [
        {
          service: 'headless-pm-api',
          url: `${apiUrl}/health`,
          health: apiDependency
        },
        {
          service: 'headless-pm-mcp-sse',
          url: `${mcpUrl}/health`,
          health: mcpDependency
        }
      ]
    });
    
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      service: 'headless-pm-dashboard',
      version: '1.0.0',
      pid: process.pid,
      error: error.message,
      timestamp: new Date().toISOString(),
      depends_on: [
        {
          service: 'headless-pm-api',
          url: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969'}/health`,
          health: {
            status: 'unknown',
            service: 'headless-pm-api',
            error: 'Could not check dependency due to service error'
          }
        },
        {
          service: 'headless-pm-mcp-sse',
          url: `${process.env.NEXT_PUBLIC_MCP_URL || 'http://localhost:6968'}/health`,
          health: {
            status: 'unknown',
            service: 'headless-pm-mcp-sse',
            error: 'Could not check dependency due to service error'
          }
        }
      ]
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