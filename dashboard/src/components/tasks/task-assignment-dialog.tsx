'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useApi } from '@/lib/hooks/useApi';
import { Task, AgentAvailability, AgentStatus } from '@/lib/types';
import { UserCheck, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface TaskAssignmentDialogProps {
  task: Task;
  projectId: number;
  assignerAgentId: string;
  onAssignmentComplete?: (task: Task) => void;
  children: React.ReactNode;
}

export function TaskAssignmentDialog({
  task,
  projectId,
  assignerAgentId,
  onAssignmentComplete,
  children
}: TaskAssignmentDialogProps) {
  const { client } = useApi();
  const [isOpen, setIsOpen] = useState(false);
  const [agents, setAgents] = useState<AgentAvailability[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadAvailableAgents();
    }
  }, [isOpen]);

  const loadAvailableAgents = async () => {
    try {
      setLoading(true);
      client.setCurrentProject(projectId);
      const availabilityData = await client.getAgentsAvailability();
      // Filter to only show agents that match the task's target role and are available
      const suitableAgents = availabilityData.filter(agent => 
        agent.is_available && agent.status === AgentStatus.Idle
      );
      setAgents(suitableAgents);
      setError(null);
    } catch (err) {
      console.error('Failed to load available agents:', err);
      setError('Failed to load available agents');
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedAgentId) return;

    try {
      setLoading(true);
      const updatedTask = await client.assignTaskToAgent(
        task.id,
        selectedAgentId,
        assignerAgentId
      );
      onAssignmentComplete?.(updatedTask);
      setIsOpen(false);
      setSelectedAgentId('');
    } catch (err) {
      console.error('Failed to assign task:', err);
      setError(err instanceof Error ? err.message : 'Failed to assign task');
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

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserCheck className="h-5 w-5" />
            Assign Task to Agent
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Task Info */}
          <div className="p-3 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-sm text-gray-900">Task: {task.title}</h4>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline">{task.target_role}</Badge>
              <Badge variant="outline">{task.difficulty}</Badge>
              <Badge variant="outline">{task.complexity}</Badge>
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-sm text-gray-600">Loading available agents...</span>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
              <Button 
                onClick={loadAvailableAgents}
                variant="outline" 
                size="sm" 
                className="mt-2"
              >
                Retry
              </Button>
            </div>
          )}

          {!loading && !error && (
            <>
              {/* Agent Selection */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Select Agent
                </label>
                <Select value={selectedAgentId || ''} onValueChange={setSelectedAgentId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose an available agent..." />
                  </SelectTrigger>
                  <SelectContent>
                    {agents.length === 0 ? (
                      <div className="p-2 text-sm text-gray-500">
                        No available agents for this task role
                      </div>
                    ) : (
                      agents.map((agent) => (
                        <SelectItem key={agent.agent_id} value={agent.agent_id}>
                          <div className="flex items-center gap-2 w-full">
                            {getStatusIcon(agent.status)}
                            <span>{agent.agent_id}</span>
                            <span className="text-xs text-gray-500 ml-auto">
                              {formatLastActivity(agent.last_activity)}
                            </span>
                          </div>
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* Selected Agent Info */}
              {selectedAgentId && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  {(() => {
                    const selectedAgent = agents.find(a => a.agent_id === selectedAgentId);
                    if (!selectedAgent) return null;
                    
                    return (
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          {getStatusIcon(selectedAgent.status)}
                          <span className="font-medium">{selectedAgent.agent_id}</span>
                          <Badge variant="outline" className="bg-green-100 text-green-800">
                            Available
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600">
                          Last activity: {formatLastActivity(selectedAgent.last_activity)}
                        </p>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* Assignment Actions */}
              <div className="flex justify-end gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsOpen(false)}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAssign}
                  disabled={!selectedAgentId || loading}
                >
                  {loading ? 'Assigning...' : 'Assign Task'}
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}