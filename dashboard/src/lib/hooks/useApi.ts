import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback, useMemo, useState, useEffect } from 'react';
import { HeadlessPMClient } from '@/lib/api/client';
import { useProjectContext } from '@/lib/contexts/project-context';
import { 
  AgentRole, SkillLevel, TaskStatus, DocumentType,
  Epic, Feature, Task, Agent, Document, Service, Mention, Project, TaskUpdateRequest
} from '@/lib/types';

// API client is now managed by ProjectContext

// Use project context instead
export const useCurrentProject = () => {
  const { currentProjectId } = useProjectContext();
  return currentProjectId;
};

// Project hooks - use context projects
export const useProjects = () => {
  const { projects, isLoading } = useProjectContext();
  return {
    data: projects,
    isLoading,
    error: null,
    refetch: () => Promise.resolve()
  };
};

export const useCreateProject = () => {
  const { apiClient, loadProjects } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      name: string;
      description: string;
      shared_path: string;
      instructions_path: string;
      project_docs_path: string;
    }) => apiClient.createProject(data),
    onSuccess: () => {
      loadProjects();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    }
  });
};

export const useUpdateProject = () => {
  const { apiClient, loadProjects } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, updates }: {
      projectId: number;
      updates: {
        description?: string;
        shared_path?: string;
        instructions_path?: string;
        project_docs_path?: string;
      };
    }) => apiClient.updateProject(projectId, updates),
    onSuccess: () => {
      loadProjects();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    }
  });
};

export const useDeleteProject = () => {
  const { apiClient, loadProjects } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: number) => apiClient.deleteProject(projectId),
    onSuccess: () => {
      loadProjects();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    }
  });
};

// Epic hooks
export const useEpics = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['epics', currentProjectId],
    queryFn: () => apiClient.getEpics(),
    enabled: !!currentProjectId,
    refetchInterval: 30000,
    refetchOnWindowFocus: false
  });
};

export const useCreateEpic = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string; pmId?: string }) => 
      apiClient.createEpic(data.name, data.description, data.pmId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['epics', currentProjectId] });
    }
  });
};

// Feature hooks
export const useFeatures = (epicId?: number) => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['features', epicId, currentProjectId],
    queryFn: () => apiClient.getFeatures(epicId),
    enabled: epicId !== undefined && !!currentProjectId
  });
};

// Task hooks
export const useTasks = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['tasks', currentProjectId],
    queryFn: () => apiClient.getTasks(),
    enabled: !!currentProjectId,
    refetchInterval: 10000,
    refetchOnWindowFocus: false
  });
};

export const useTasksByFeature = (featureId: number) => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['tasks', 'feature', featureId, currentProjectId],
    queryFn: () => apiClient.getTasksByFeature(featureId),
    enabled: !!featureId && !!currentProjectId
  });
};

export const useUpdateTaskStatus = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, status, agentId }: { taskId: number; status: TaskStatus; agentId: string }) =>
      apiClient.updateTaskStatus(taskId, status, agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', currentProjectId] });
    }
  });
};

export const useUpdateTaskDetails = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, updates }: { taskId: number; updates: TaskUpdateRequest }) =>
      apiClient.updateTaskDetails(taskId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', currentProjectId] });
    }
  });
};

// Agent hooks
export const useAgents = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['agents', currentProjectId],
    queryFn: () => apiClient.getAgents(),
    enabled: !!currentProjectId,
    refetchInterval: 30000,
    refetchOnWindowFocus: false,
    staleTime: 10000,
    retry: 1
  });
};

// Document hooks
export const useDocuments = (authorId?: string, type?: DocumentType, enabled = true) => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['documents', authorId, type, currentProjectId],
    queryFn: () => apiClient.getDocuments(authorId, type),
    enabled: enabled && !!currentProjectId,
    refetchInterval: 15000,
    refetchOnWindowFocus: false
  });
};

export const useCreateDocument = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { type: DocumentType; title: string; content: string; author_id: string }) =>
      apiClient.createDocument(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['mentions'] });
    }
  });
};

// Mention hooks
export const useMentions = (agentId?: string, unreadOnly = false, enabled = true) => {
  const { apiClient, currentProjectId } = useProjectContext();
  console.log('useMentions called with agentId:', agentId);
  return useQuery({
    queryKey: ['mentions', agentId, unreadOnly, currentProjectId],
    queryFn: () => apiClient.getMentions(agentId, unreadOnly),
    enabled: enabled && !!currentProjectId,
    refetchInterval: 10000,
    refetchOnWindowFocus: false
  });
};

export const useMentionsByRole = (role?: string, unreadOnly = false, enabled = true) => {
  const { apiClient, currentProjectId } = useProjectContext();
  console.log('useMentionsByRole called with role:', role);
  return useQuery({
    queryKey: ['mentions', 'by-role', role, unreadOnly, currentProjectId],
    queryFn: () => apiClient.getMentionsByRole(role, unreadOnly),
    enabled: enabled && !!currentProjectId,
    refetchInterval: 10000,
    refetchOnWindowFocus: false
  });
};

// Service hooks
export const useServices = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['services', currentProjectId],
    queryFn: () => apiClient.getServices(),
    enabled: !!currentProjectId,
    refetchInterval: 5000,
    refetchOnWindowFocus: false
  });
};

// Context hook
export const useProjectContextData = () => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['context', currentProjectId],
    queryFn: () => apiClient.getContext(),
    enabled: !!currentProjectId,
    staleTime: Infinity
  });
};

// Changes hook for real-time updates
export const useChanges = (since: number, agentId?: string) => {
  const { apiClient, currentProjectId } = useProjectContext();
  return useQuery({
    queryKey: ['changes', since, agentId, currentProjectId],
    queryFn: () => apiClient.getChanges(since, agentId),
    refetchInterval: 3000,
    enabled: !!since && !!currentProjectId,
    refetchOnWindowFocus: false
  });
};

// Generic useApi hook for flexible API calls
export const useApi = <T>(
  queryKey?: string | readonly unknown[],
  queryFn?: (client: HeadlessPMClient) => Promise<T>,
  options?: {
    refetchInterval?: number;
    enabled?: boolean;
    staleTime?: number;
  }
) => {
  const { apiClient } = useProjectContext();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKey ? (Array.isArray(queryKey) ? queryKey : [queryKey]) : ['default'],
    queryFn: queryFn ? () => queryFn(apiClient) : async () => null as T,
    refetchInterval: options?.refetchInterval || false,
    refetchOnWindowFocus: false,
    enabled: options?.enabled !== false && !!queryFn,
    staleTime: options?.staleTime || 30000,
    retry: 1,
    retryDelay: 2000
  });

  return {
    data: data as T,
    isLoading,
    error,
    refetch,
    mutate: refetch,
    client: apiClient
  };
};