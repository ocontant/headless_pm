'use client';

import { useState, useMemo } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { useServices, useAgents } from '@/lib/hooks/useApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StatsWidget } from '@/components/ui/stats-widget';
import { ServiceHealthStatus } from '@/components/health/service-health-status';
import { 
  Server, 
  Activity, 
  AlertCircle, 
  CheckCircle2,
  Clock,
  Users,
  Wifi,
  Database,
  Globe,
  Zap,
  RefreshCw,
  Link
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function HealthPage() {
  // Fetch services and agents - let the API calls handle project requirements internally
  const { data: services, isLoading: servicesLoading, refetch: refetchServices, error: servicesError } = useServices();
  const { data: agents, isLoading: agentsLoading, refetch: refetchAgents, error: agentsError } = useAgents();

  // Calculate health metrics
  const healthMetrics = useMemo(() => {
    // Check if we have data, are loading, or have errors
    const isLoading = servicesLoading || agentsLoading;
    const hasErrors = servicesError || agentsError;
    const hasProjectData = services && agents;
    
    // If there are errors (likely "No project selected"), treat as no project
    if (hasErrors || (!hasProjectData && !isLoading)) {
      return {
        hasProjectData: false,
        isLoading: false, // Not loading if we have errors
        hasErrors,
        services: { total: 0, active: 0, inactive: 0, withPing: 0, healthScore: 0 },
        agents: { total: 0, online: 0, recentlyActive: 0, offline: 0, healthScore: 0 },
        overallHealthScore: 0,
        servicesData: [],
        agentsData: [],
        onlineAgents: [],
        recentlyActiveAgents: [],
        offlineAgents: []
      };
    }
    
    // If we're still loading
    if (isLoading) {
      return {
        hasProjectData: false,
        isLoading: true,
        hasErrors: false,
        services: { total: 0, active: 0, inactive: 0, withPing: 0, healthScore: 0 },
        agents: { total: 0, online: 0, recentlyActive: 0, offline: 0, healthScore: 0 },
        overallHealthScore: 0,
        servicesData: [],
        agentsData: [],
        onlineAgents: [],
        recentlyActiveAgents: [],
        offlineAgents: []
      };
    }

    const now = Date.now();
    const fiveMinutesAgo = now - 5 * 60 * 1000;
    const oneHourAgo = now - 60 * 60 * 1000;

    // Service health
    const activeServices = services?.filter(s => s.status?.toLowerCase() === 'up') || [];
    const inactiveServices = services?.filter(s => s.status?.toLowerCase() === 'down') || [];
    const servicesWithPing = services?.filter(s => s.ping_url) || [];

    // Agent health
    const onlineAgents = agents?.filter(a => {
      if (!a.last_seen) return false;
      const lastSeenTime = new Date(a.last_seen).getTime();
      return lastSeenTime > fiveMinutesAgo;
    }) || [];

    const recentlyActiveAgents = agents?.filter(a => {
      if (!a.last_seen) return false;
      const lastSeenTime = new Date(a.last_seen).getTime();
      return lastSeenTime > oneHourAgo && lastSeenTime <= fiveMinutesAgo;
    }) || [];

    const offlineAgents = agents?.filter(a => {
      if (!a.last_seen) return true;
      const lastSeenTime = new Date(a.last_seen).getTime();
      return lastSeenTime <= oneHourAgo;
    }) || [];

    // Overall system health score
    const totalServices = services?.length || 0;
    const totalAgents = agents?.length || 0;
    const healthyServices = activeServices.length;
    const healthyAgents = onlineAgents.length;
    
    const serviceHealthScore = totalServices > 0 ? (healthyServices / totalServices) * 100 : 100;
    const agentHealthScore = totalAgents > 0 ? (healthyAgents / totalAgents) * 100 : 100;
    const overallHealthScore = (serviceHealthScore + agentHealthScore) / 2;

    return {
      hasProjectData: true,
      services: {
        total: totalServices,
        active: activeServices.length,
        inactive: inactiveServices.length,
        withPing: servicesWithPing.length,
        healthScore: serviceHealthScore
      },
      agents: {
        total: totalAgents,
        online: onlineAgents.length,
        recentlyActive: recentlyActiveAgents.length,
        offline: offlineAgents.length,
        healthScore: agentHealthScore
      },
      overallHealthScore,
      servicesData: services || [],
      agentsData: agents || [],
      onlineAgents,
      recentlyActiveAgents,
      offlineAgents
    };
  }, [services, agents]);

  const getServiceStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'up':
      case 'active': return 'bg-green-100 text-green-800';
      case 'down':
      case 'inactive': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAgentStatusColor = (agent: any) => {
    if (!agent.last_seen) return 'bg-gray-100 text-gray-800';
    
    const lastSeenTime = new Date(agent.last_seen).getTime();
    const now = Date.now();
    const fiveMinutesAgo = now - 5 * 60 * 1000;
    const oneHourAgo = now - 60 * 60 * 1000;

    if (lastSeenTime > fiveMinutesAgo) return 'bg-green-100 text-green-800';
    if (lastSeenTime > oneHourAgo) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getAgentStatus = (agent: any) => {
    if (!agent.last_seen) return 'Never seen';
    
    const lastSeenTime = new Date(agent.last_seen).getTime();
    const now = Date.now();
    const fiveMinutesAgo = now - 5 * 60 * 1000;
    const oneHourAgo = now - 60 * 60 * 1000;

    if (lastSeenTime > fiveMinutesAgo) return 'Online';
    if (lastSeenTime > oneHourAgo) return 'Recently Active';
    return 'Offline';
  };

  const handleRefresh = () => {
    refetchServices();
    refetchAgents();
  };

  // Show loading only if we're actually loading (not failed due to missing project)
  const isActuallyLoading = (servicesLoading || agentsLoading) && !servicesError && !agentsError;
  
  if (isActuallyLoading) {
    return (
      <PageLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">System Health</h1>
            <p className="text-muted-foreground mt-1">Loading system status...</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        </div>
      </PageLayout>
    );
  }

  if (!healthMetrics) {
    return (
      <PageLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">System Health</h1>
            <p className="text-muted-foreground mt-1">No health data available</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">System Health</h1>
            <p className="text-muted-foreground mt-1">
              Service registry and agent monitoring
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-3 py-2 text-sm border rounded-md hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {/* System Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsWidget
            title="Overall Health"
            value={healthMetrics.hasProjectData ? `${healthMetrics.overallHealthScore.toFixed(0)}%` : "N/A"}
            description="System status"
            icon={<Activity className="h-4 w-4" />}
            trend={healthMetrics.hasProjectData ? { 
              value: healthMetrics.overallHealthScore > 80 ? 5 : -10, 
              isPositive: healthMetrics.overallHealthScore > 80 
            } : undefined}
          />
          <StatsWidget
            title="Services"
            value={healthMetrics.hasProjectData ? `${healthMetrics.services.active}/${healthMetrics.services.total}` : "N/A"}
            description="Active services"
            icon={<Server className="h-4 w-4" />}
          />
          <StatsWidget
            title="Agents"
            value={healthMetrics.hasProjectData ? `${healthMetrics.agents.online}/${healthMetrics.agents.total}` : "N/A"}
            description="Online agents"
            icon={<Users className="h-4 w-4" />}
          />
          <StatsWidget
            title="Connectivity"
            value={healthMetrics.hasProjectData ? `${healthMetrics.services.withPing}/${healthMetrics.services.total}` : "N/A"}
            description="Services with ping"
            icon={<Wifi className="h-4 w-4" />}
          />
        </div>
        
        {/* Project Selection Notice */}
        {!healthMetrics.hasProjectData && (
          <div className={`border rounded-lg p-4 ${
            healthMetrics.isLoading 
              ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
              : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
          }`}>
            <div className="flex items-center gap-2">
              {healthMetrics.isLoading ? (
                <RefreshCw className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              )}
              <span className={`text-sm font-medium ${
                healthMetrics.isLoading 
                  ? 'text-blue-800 dark:text-blue-200'
                  : 'text-yellow-800 dark:text-yellow-200'
              }`}>
                {healthMetrics.isLoading ? 'Loading project data...' : 'No project selected'}
              </span>
            </div>
            <p className={`text-sm mt-1 ${
              healthMetrics.isLoading 
                ? 'text-blue-700 dark:text-blue-300'
                : 'text-yellow-700 dark:text-yellow-300'
            }`}>
              {healthMetrics.isLoading 
                ? 'Loading project-specific services and agents...'
                : 'Select a project from the dropdown above to view project-specific services and agents. The Service Health tab shows infrastructure status regardless of project selection.'
              }
            </p>
          </div>
        )}

        {/* Detailed Health Info */}
        <Tabs defaultValue="health" className="space-y-4">
          <TabsList>
            <TabsTrigger value="health">Service Health</TabsTrigger>
            {healthMetrics.hasProjectData && (
              <>
                <TabsTrigger value="services">Service Registry</TabsTrigger>
                <TabsTrigger value="agents">Agents</TabsTrigger>
                <TabsTrigger value="system">System Overview</TabsTrigger>
              </>
            )}
          </TabsList>

          <TabsContent value="health" className="space-y-4">
            <ServiceHealthStatus />
          </TabsContent>

          {healthMetrics.hasProjectData && (
            <TabsContent value="services" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5" />
                  Service Registry
                </CardTitle>
                <CardDescription>
                  Registered services and their health status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[500px]">
                  <div className="space-y-4">
                    {healthMetrics.servicesData && healthMetrics.servicesData.length > 0 ? (
                      healthMetrics.servicesData.map((service, index) => (
                        <Card key={service.service_name || index} className="p-4">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 space-y-2">
                              <div className="flex items-center gap-2">
                                <h3 className="font-medium">{service.service_name}</h3>
                                <Badge className={getServiceStatusColor(service.status)}>
                                  {service.status}
                                </Badge>
                                {service.ping_url && (
                                  <Badge variant="outline" className="text-xs">
                                    <Link className="h-3 w-3 mr-1" />
                                    Pingable
                                  </Badge>
                                )}
                              </div>
                              <div className="text-sm text-muted-foreground space-y-1">
                                <p><span className="font-medium">Port:</span> {service.port}</p>
                                <p><span className="font-medium">Owner:</span> {service.owner_agent_id}</p>
                                {service.ping_url && (
                                  <p><span className="font-medium">Ping URL:</span> {service.ping_url}</p>
                                )}
                                <p><span className="font-medium">Last heartbeat:</span> {
                                  service.last_heartbeat 
                                    ? formatDistanceToNow(new Date(service.last_heartbeat), { addSuffix: true })
                                    : 'Never'
                                }</p>
                              </div>
                              {service.meta_data && Object.keys(service.meta_data).length > 0 && (
                                <div className="text-xs">
                                  <span className="font-medium">Metadata:</span>
                                  <pre className="mt-1 p-2 bg-gray-50 rounded text-xs">
                                    {JSON.stringify(service.meta_data, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                            <div className="flex items-center">
                              {service.status?.toLowerCase() === 'up' ? (
                                <CheckCircle2 className="h-5 w-5 text-green-600" />
                              ) : (
                                <AlertCircle className="h-5 w-5 text-red-600" />
                              )}
                            </div>
                          </div>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Server className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                        <p className="text-muted-foreground">No services registered</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
          )}

          {healthMetrics.hasProjectData && (
            <TabsContent value="agents" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Online Agents */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600">
                    <CheckCircle2 className="h-5 w-5" />
                    Online ({healthMetrics.agents.online})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[300px]">
                    <div className="space-y-2">
                      {healthMetrics.onlineAgents.map(agent => (
                        <div key={agent.id} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{agent.name || agent.id}</p>
                              <p className="text-xs text-muted-foreground">{agent.role}</p>
                              <p className="text-xs text-muted-foreground">
                                {agent.last_seen && formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true })}
                              </p>
                            </div>
                            <Badge className="bg-green-100 text-green-800 text-xs">Online</Badge>
                          </div>
                        </div>
                      ))}
                      {healthMetrics.agents.online === 0 && (
                        <p className="text-sm text-muted-foreground text-center py-4">No online agents</p>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* Recently Active Agents */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-yellow-600">
                    <Clock className="h-5 w-5" />
                    Recently Active ({healthMetrics.agents.recentlyActive})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[300px]">
                    <div className="space-y-2">
                      {healthMetrics.recentlyActiveAgents.map(agent => (
                        <div key={agent.id} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{agent.name || agent.id}</p>
                              <p className="text-xs text-muted-foreground">{agent.role}</p>
                              <p className="text-xs text-muted-foreground">
                                {agent.last_seen && formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true })}
                              </p>
                            </div>
                            <Badge className="bg-yellow-100 text-yellow-800 text-xs">Away</Badge>
                          </div>
                        </div>
                      ))}
                      {healthMetrics.agents.recentlyActive === 0 && (
                        <p className="text-sm text-muted-foreground text-center py-4">No recently active agents</p>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* Offline Agents */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-5 w-5" />
                    Offline ({healthMetrics.agents.offline})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[300px]">
                    <div className="space-y-2">
                      {healthMetrics.offlineAgents.map(agent => (
                        <div key={agent.id} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{agent.name || agent.id}</p>
                              <p className="text-xs text-muted-foreground">{agent.role}</p>
                              <p className="text-xs text-muted-foreground">
                                {agent.last_seen 
                                  ? formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true })
                                  : 'Never seen'
                                }
                              </p>
                            </div>
                            <Badge className="bg-red-100 text-red-800 text-xs">Offline</Badge>
                          </div>
                        </div>
                      ))}
                      {healthMetrics.agents.offline === 0 && (
                        <p className="text-sm text-muted-foreground text-center py-4">No offline agents</p>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          )}

          {healthMetrics.hasProjectData && (
            <TabsContent value="system" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Health Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Health Summary
                  </CardTitle>
                  <CardDescription>Overall system health metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium">Service Health</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold">{healthMetrics.services.healthScore.toFixed(0)}%</span>
                      {healthMetrics.services.healthScore > 80 ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-purple-600" />
                      <span className="text-sm font-medium">Agent Health</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold">{healthMetrics.agents.healthScore.toFixed(0)}%</span>
                      {healthMetrics.agents.healthScore > 80 ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">Overall Health</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold">{healthMetrics.overallHealthScore.toFixed(0)}%</span>
                      {healthMetrics.overallHealthScore > 80 ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* System Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    System Information
                  </CardTitle>
                  <CardDescription>Current system status and configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">API Endpoint</span>
                      <span className="font-mono text-xs">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Services</span>
                      <span>{healthMetrics.services.total}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Agents</span>
                      <span>{healthMetrics.agents.total}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Updated</span>
                      <span>{new Date().toLocaleTimeString()}</span>
                    </div>
                  </div>
                  
                  <div className="pt-3 border-t">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Globe className="h-4 w-4" />
                      <span>Auto-refresh every 5 seconds</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          )}
        </Tabs>
      </div>
    </PageLayout>
  );
}