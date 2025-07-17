'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  version: string;
  timestamp: string;
  database?: string;
  api_backend?: string;
  active_sessions?: number;
}

interface ServiceHealthStatusProps {
  title?: string;
  showTitle?: boolean;
}

export function ServiceHealthStatus({ title = "Service Health Status", showTitle = true }: ServiceHealthStatusProps) {
  const [apiHealth, setApiHealth] = useState<HealthStatus | null>(null);
  const [mcpHealth, setMcpHealth] = useState<HealthStatus | null>(null);
  const [dashboardHealth, setDashboardHealth] = useState<HealthStatus>({
    status: 'healthy',
    service: 'headless-pm-dashboard',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        // Check API health via the dashboard's health endpoint
        try {
          const apiResponse = await fetch('/api/health');
          if (apiResponse.ok) {
            const apiData = await apiResponse.json();
            // Transform the response to match the expected format
            setApiHealth({
              status: apiData.api_backend === 'healthy' ? 'healthy' : 'unhealthy',
              service: 'headless-pm-api',
              version: '1.0.0',
              database: apiData.api_backend === 'healthy' ? 'healthy' : 'unhealthy',
              timestamp: apiData.timestamp
            });
          } else {
            setApiHealth({
              status: 'unhealthy',
              service: 'headless-pm-api',
              version: '1.0.0',
              timestamp: new Date().toISOString()
            });
          }
        } catch (error) {
          setApiHealth({
            status: 'unhealthy',
            service: 'headless-pm-api',
            version: '1.0.0',
            timestamp: new Date().toISOString()
          });
        }

        // Check MCP health via proxy
        try {
          const mcpResponse = await fetch('/api/mcp-health');
          if (mcpResponse.ok) {
            const mcpData = await mcpResponse.json();
            setMcpHealth(mcpData);
          } else {
            setMcpHealth({
              status: 'unhealthy',
              service: 'headless-pm-mcp',
              version: '1.0.0',
              timestamp: new Date().toISOString()
            });
          }
        } catch (error) {
          setMcpHealth({
            status: 'unhealthy',
            service: 'headless-pm-mcp',
            version: '1.0.0',
            timestamp: new Date().toISOString()
          });
        }
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getOverallStatus = () => {
    if (loading) return 'checking';
    if (!apiHealth || apiHealth.status === 'unhealthy') return 'unhealthy';
    if (apiHealth.status === 'degraded' || (mcpHealth && mcpHealth.status === 'degraded')) return 'degraded';
    return 'healthy';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✓';
      case 'degraded': return '⚠';
      case 'unhealthy': return '✗';
      default: return '⋯';
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'healthy': return 'default';
      case 'degraded': return 'secondary';
      case 'unhealthy': return 'destructive';
      default: return 'outline';
    }
  };

  const overallStatus = getOverallStatus();

  return (
    <Card>
      {showTitle && (
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{title}</span>
            <Badge variant={getStatusBadgeVariant(overallStatus)} className="ml-2">
              {getStatusIcon(overallStatus)} {overallStatus.toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <div className="space-y-4">
          <div className="text-center text-sm text-muted-foreground">
            {loading ? 'Checking services...' : `Last updated: ${new Date().toLocaleString()}`}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* API Service */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium mb-2">API Service</h4>
              {apiHealth ? (
                <div className="space-y-2">
                  <div className={`flex items-center ${getStatusColor(apiHealth.status)}`}>
                    <span className="mr-2">{getStatusIcon(apiHealth.status)}</span>
                    <span className="text-sm font-medium">{apiHealth.status.toUpperCase()}</span>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Service: {apiHealth.service}</div>
                    <div>Version: {apiHealth.version}</div>
                    {apiHealth.database && <div>Database: {apiHealth.database}</div>}
                    <div>Port: 6969</div>
                  </div>
                </div>
              ) : (
                <div className="text-muted-foreground text-sm">Loading...</div>
              )}
            </div>

            {/* MCP Service */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium mb-2">MCP Service</h4>
              {mcpHealth ? (
                <div className="space-y-2">
                  <div className={`flex items-center ${getStatusColor(mcpHealth.status)}`}>
                    <span className="mr-2">{getStatusIcon(mcpHealth.status)}</span>
                    <span className="text-sm font-medium">{mcpHealth.status.toUpperCase()}</span>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Service: {mcpHealth.service}</div>
                    <div>Version: {mcpHealth.version}</div>
                    {mcpHealth.active_sessions !== undefined && (
                      <div>Sessions: {mcpHealth.active_sessions}</div>
                    )}
                    <div>Port: 6968</div>
                  </div>
                </div>
              ) : (
                <div className="text-muted-foreground text-sm">Loading...</div>
              )}
            </div>

            {/* Dashboard Service */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium mb-2">Dashboard Service</h4>
              <div className="space-y-2">
                <div className={`flex items-center ${getStatusColor(dashboardHealth.status)}`}>
                  <span className="mr-2">{getStatusIcon(dashboardHealth.status)}</span>
                  <span className="text-sm font-medium">{dashboardHealth.status.toUpperCase()}</span>
                </div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>Service: {dashboardHealth.service}</div>
                  <div>Version: {dashboardHealth.version}</div>
                  <div>Port: 3001</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}