'use client';

import { useState, useEffect } from 'react';
import { AgentAvailability, AgentRole, AgentStatus } from '@/lib/types';
import { useApi } from '@/lib/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RefreshCw, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface AgentAvailabilityDashboardProps {
  projectId: number;
  className?: string;
}

export function AgentAvailabilityDashboard({ projectId, className = '' }: AgentAvailabilityDashboardProps) {
  const { client } = useApi();
  const [agents, setAgents] = useState<AgentAvailability[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<AgentAvailability[]>([]);
  const [selectedRole, setSelectedRole] = useState<AgentRole | 'all'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    client.setCurrentProject(projectId);
    loadAgentAvailability();
  }, [projectId]);

  useEffect(() => {
    if (selectedRole === 'all') {
      setFilteredAgents(agents);
    } else {
      // Note: We'd need to also fetch agent role data or include it in AgentAvailability
      setFilteredAgents(agents);
    }
  }, [agents, selectedRole]);

  const loadAgentAvailability = async () => {
    try {
      setLoading(true);
      const availabilityData = await client.getAgentsAvailability(
        selectedRole !== 'all' ? selectedRole : undefined
      );
      setAgents(availabilityData);
      setError(null);
    } catch (err) {
      console.error('Failed to load agent availability:', err);
      setError('Failed to load agent availability');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case AgentStatus.Idle:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case AgentStatus.Working:
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case AgentStatus.Offline:
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: AgentStatus, isAvailable: boolean) => {
    if (!isAvailable) {
      return <Badge variant="destructive">Unavailable</Badge>;
    }

    switch (status) {
      case AgentStatus.Idle:
        return <Badge variant="success" className="bg-green-100 text-green-800">Available</Badge>;
      case AgentStatus.Working:
        return <Badge variant="warning" className="bg-yellow-100 text-yellow-800">Working</Badge>;
      case AgentStatus.Offline:
        return <Badge variant="destructive">Offline</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const formatLastActivity = (lastActivity: string) => {
    const date = new Date(lastActivity);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const getAvailabilityStats = () => {
    const total = filteredAgents.length;
    const available = filteredAgents.filter(a => a.is_available && a.status === AgentStatus.Idle).length;
    const working = filteredAgents.filter(a => a.status === AgentStatus.Working).length;
    const offline = filteredAgents.filter(a => a.status === AgentStatus.Offline).length;
    
    return { total, available, working, offline };
  };

  const stats = getAvailabilityStats();

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            Loading Agent Availability...
          </CardTitle>
        </CardHeader>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Agent Availability</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <Button onClick={loadAgentAvailability} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Agent Availability</CardTitle>
          <div className="flex items-center gap-2">
            <Select value={selectedRole} onValueChange={(value) => setSelectedRole(value as AgentRole | 'all')}>
              <SelectTrigger className="w-[140px] h-8">
                <SelectValue placeholder="Filter by role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value={AgentRole.FrontendDev}>Frontend Dev</SelectItem>
                <SelectItem value={AgentRole.BackendDev}>Backend Dev</SelectItem>
                <SelectItem value={AgentRole.QA}>QA</SelectItem>
                <SelectItem value={AgentRole.Architect}>Architect</SelectItem>
                <SelectItem value={AgentRole.ProjectPM}>Project PM</SelectItem>
                <SelectItem value={AgentRole.GlobalPM}>Global PM</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={loadAgentAvailability} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Stats Summary */}
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <CheckCircle className="h-4 w-4 text-green-500" />
            {stats.available} Available
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4 text-yellow-500" />
            {stats.working} Working
          </span>
          <span className="flex items-center gap-1">
            <AlertCircle className="h-4 w-4 text-red-500" />
            {stats.offline} Offline
          </span>
          <span className="text-gray-500">Total: {stats.total}</span>
        </div>
      </CardHeader>
      
      <CardContent>
        {filteredAgents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No agents found for this project.
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAgents.map((agent) => (
              <div
                key={agent.agent_id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(agent.status)}
                  <div>
                    <div className="font-medium text-sm">{agent.agent_id}</div>
                    <div className="text-xs text-gray-500">
                      Last activity: {formatLastActivity(agent.last_activity)}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {agent.current_task_id && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Task {agent.current_task_id}:</span>
                      <span className="ml-1">{agent.current_task_title || 'Untitled'}</span>
                    </div>
                  )}
                  {getStatusBadge(agent.status, agent.is_available)}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}