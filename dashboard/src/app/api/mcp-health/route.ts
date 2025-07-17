import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const mcpUrl = process.env.MCP_URL || 'http://localhost:6968';
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${mcpUrl}/health`, {
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      return NextResponse.json({
        status: 'unhealthy',
        service: 'headless-pm-mcp',
        version: '1.0.0',
        error: `HTTP ${response.status}`,
        timestamp: new Date().toISOString()
      }, { status: response.status });
    }
  } catch (error: any) {
    return NextResponse.json({
      status: 'unhealthy',
      service: 'headless-pm-mcp',
      version: '1.0.0',
      error: error.name === 'AbortError' ? 'timeout' : error.message,
      timestamp: new Date().toISOString()
    }, { status: 503 });
  }
}