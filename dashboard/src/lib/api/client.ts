import axios, { AxiosInstance } from 'axios';
import { 
  Agent, Epic, Feature, Task, TaskComment, Document, 
  Mention, Service, ProjectContext, Changes,
  TaskStatus, AgentRole, SkillLevel, DocumentType,
  Project, AgentAvailability, TaskUpdateRequest,
  TimeEntryCreateRequest, TimeEntry, TaskTimeTracking
} from '@/lib/types';

export class HeadlessPMClient {
  private client: AxiosInstance;
  private currentProjectId: number | null = null;

  constructor(baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969', apiKey?: string) {
    // Check localStorage first for user-configured values
    const storedUrl = typeof window !== 'undefined' ? localStorage.getItem('apiUrl') : null;
    const storedKey = typeof window !== 'undefined' ? localStorage.getItem('apiKey') : null;
    
    const finalUrl = storedUrl || baseURL;
    const apiKeyToUse = storedKey || apiKey || process.env.API_KEY;
    
    this.client = axios.create({
      baseURL: `${finalUrl}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKeyToUse && { 'X-API-Key': apiKeyToUse })
      }
    });
  }

  setCurrentProject(projectId: number | null) {
    this.currentProjectId = projectId;
  }

  getCurrentProject(): number | null {
    return this.currentProjectId;
  }

  // Project endpoints
  async getProjects() {
    const { data } = await this.client.get<Project[]>('/projects');
    return data;
  }

  async getProject(projectId: number) {
    const { data } = await this.client.get<Project>(`/projects/${projectId}`);
    return data;
  }

  async createProject(project: {
    name: string;
    description: string;
    shared_path: string;
    instructions_path: string;
    project_docs_path: string;
    code_guidelines_path?: string;
  }) {
    const { data } = await this.client.post<Project>('/projects', project);
    return data;
  }

  async updateProject(projectId: number, updates: {
    description?: string;
    shared_path?: string;
    instructions_path?: string;
    project_docs_path?: string;
    code_guidelines_path?: string;
  }) {
    const { data } = await this.client.patch<Project>(`/projects/${projectId}`, updates);
    return data;
  }

  async deleteProject(projectId: number) {
    await this.client.delete(`/projects/${projectId}`);
  }

  // Agent endpoints
  async registerAgent(agentId: string, role: AgentRole, skillLevel: SkillLevel, name?: string) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const { data } = await this.client.post<Agent>('/register', {
      agent_id: agentId,
      project_id: this.currentProjectId,
      role,
      skill_level: skillLevel,
      name
    });
    return data;
  }

  async getAgents() {
    const params = this.currentProjectId ? `?project_id=${this.currentProjectId}` : '';
    const { data } = await this.client.get<Agent[]>(`/agents${params}`);
    return data;
  }

  async deleteAgent(agentId: string) {
    await this.client.delete(`/agents/${agentId}`);
  }

  async getAgentsAvailability(role?: AgentRole) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    if (role) {
      params.append('role', role);
    }
    const { data } = await this.client.get<AgentAvailability[]>(`/agents/availability?${params.toString()}`);
    return data;
  }

  async getAgentAvailability(agentId: string) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    const { data } = await this.client.get<AgentAvailability>(`/agents/${agentId}/availability?${params.toString()}`);
    return data;
  }

  async assignTaskToAgent(taskId: number, targetAgentId: string, assignerAgentId: string) {
    const params = new URLSearchParams();
    params.append('target_agent_id', targetAgentId);
    params.append('assigner_agent_id', assignerAgentId);
    const { data } = await this.client.post<Task>(`/tasks/${taskId}/assign?${params.toString()}`);
    return data;
  }

  // Epic endpoints
  async getEpics() {
    const { data } = await this.client.get<Epic[]>('/epics');
    return data;
  }

  async createEpic(name: string, description?: string, agentId: string = 'dashboard-user') {
    const params = new URLSearchParams();
    params.append('agent_id', agentId);
    
    const { data } = await this.client.post<Epic>(`/epics?${params.toString()}`, {
      name,
      description
    });
    return data;
  }

  async deleteEpic(id: number) {
    await this.client.delete(`/epics/${id}`);
  }

  // Feature endpoints
  async getFeatures(epicId?: number) {
    const url = epicId ? `/features/${epicId}` : '/features';
    const { data } = await this.client.get<Feature[]>(url);
    return data;
  }

  async createFeature(epicId: number, name: string, description?: string, agentId: string = 'dashboard-user') {
    const params = new URLSearchParams();
    params.append('agent_id', agentId);
    
    const { data } = await this.client.post<Feature>(`/features?${params.toString()}`, {
      epic_id: epicId,
      name,
      description
    });
    return data;
  }

  // Task endpoints
  async getTasks() {
    let url = '/tasks';
    if (this.currentProjectId) {
      url += `?project_id=${this.currentProjectId}`;
    }
    const { data } = await this.client.get<Task[]>(url);
    return data;
  }

  async getTasksByFeature(featureId: number) {
    const { data } = await this.client.get<Task[]>(`/tasks/feature/${featureId}`);
    return data;
  }

  async createTask(task: {
    feature_id: number;
    title: string;
    description?: string;
    assigned_role?: AgentRole;
    difficulty: string;
    complexity: string;
  }, agentId: string = 'dashboard-user') {
    const params = new URLSearchParams();
    params.append('agent_id', agentId);
    
    const { data } = await this.client.post<Task>(`/tasks/create?${params.toString()}`, task);
    return data;
  }

  async updateTaskStatus(taskId: number, status: TaskStatus, agentId: string) {
    const url = `/tasks/${taskId}/status?agent_id=${encodeURIComponent(agentId)}`;
    const payload = { status };
    
    try {
      const { data } = await this.client.put<Task>(url, payload);
      return data;
    } catch (error) {
      console.error('UpdateTaskStatus error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  async updateTaskDetails(taskId: number, updates: TaskUpdateRequest) {
    const url = `/tasks/${taskId}/details?agent_id=dashboard-user`;
    const payload = updates;
    
    try {
      const { data } = await this.client.put<Task>(url, payload);
      return data;
    } catch (error) {
      console.error('UpdateTaskDetails error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  async deleteTask(taskId: number) {
    const url = `/tasks/${taskId}?agent_id=dashboard-user`;
    
    try {
      const { data } = await this.client.delete<{ message: string }>(url);
      return data;
    } catch (error) {
      console.error('DeleteTask error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  async addTaskComment(taskId: number, agentId: string, content: string) {
    const { data } = await this.client.post<TaskComment>(`/tasks/${taskId}/comment`, {
      agent_id: agentId,
      content
    });
    return data;
  }

  // Time tracking endpoints
  async addTimeEntry(taskId: number, request: TimeEntryCreateRequest) {
    const url = `/tasks/${taskId}/time?agent_id=dashboard-user`;
    const payload = request;
    
    try {
      const { data } = await this.client.post<TimeEntry>(url, payload);
      return data;
    } catch (error) {
      console.error('AddTimeEntry error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  async getTaskTimeTracking(taskId: number) {
    const url = `/tasks/${taskId}/time?agent_id=dashboard-user`;
    
    try {
      const { data } = await this.client.get<TaskTimeTracking>(url);
      return data;
    } catch (error) {
      console.error('GetTaskTimeTracking error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  async deleteTimeEntry(entryId: number) {
    const url = `/time-entries/${entryId}?agent_id=dashboard-user`;
    
    try {
      const { data } = await this.client.delete<{ message: string }>(url);
      return data;
    } catch (error) {
      console.error('DeleteTimeEntry error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      throw error;
    }
  }

  // Document endpoints
  async getDocuments(authorId?: string, type?: DocumentType) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    if (authorId) params.append('author_id', authorId);
    if (type) params.append('type', type);
    
    const { data } = await this.client.get<Document[]>(`/documents?${params.toString()}`);
    return data;
  }

  async getDocument(documentId: number) {
    const { data } = await this.client.get<Document>(`/documents/${documentId}`);
    return data;
  }

  async createDocument(document: {
    type: DocumentType;
    title: string;
    content: string;
    author_id: string;
  }) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('author_id', document.author_id);
    params.append('project_id', this.currentProjectId.toString());
    
    const { data } = await this.client.post<Document>(`/documents?${params.toString()}`, {
      doc_type: document.type,
      title: document.title,
      content: document.content
    });
    return data;
  }

  // Mention endpoints
  async getMentions(agentId?: string, unreadOnly = false) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    if (agentId) {
      params.append('agent_id', agentId);
    }
    // Always explicitly set unread_only parameter
    params.append('unread_only', unreadOnly ? 'true' : 'false');
    
    const { data } = await this.client.get<Mention[]>(`/mentions?${params.toString()}`);
    return data;
  }

  async getMentionsByRole(role?: string, unreadOnly = false) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    if (role) {
      params.append('role', role);
    }
    params.append('unread_only', unreadOnly ? 'true' : 'false');
    
    const { data } = await this.client.get<Mention[]>(`/mentions/by-role?${params.toString()}`);
    return data;
  }

  async markMentionRead(mentionId: number) {
    await this.client.put(`/mentions/${mentionId}/read`);
  }

  // Service endpoints
  async getServices() {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('project_id', this.currentProjectId.toString());
    const { data } = await this.client.get<Service[]>(`/services?${params.toString()}`);
    return data;
  }

  async registerService(service: {
    name: string;
    type: string;
    endpoint_url: string;
    ping_url?: string;
    metadata?: Record<string, any>;
  }, agentId: string) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('agent_id', agentId);
    params.append('project_id', this.currentProjectId.toString());
    
    const { data } = await this.client.post<Service>(`/services/register?${params.toString()}`, {
      service_name: service.name,
      ping_url: service.ping_url || service.endpoint_url,
      port: service.endpoint_url ? parseInt(new URL(service.endpoint_url).port) || undefined : undefined,
      status: 'UP',
      meta_data: service.metadata
    });
    return data;
  }

  async sendHeartbeat(serviceName: string, agentId: string) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('agent_id', agentId);
    params.append('project_id', this.currentProjectId.toString());
    await this.client.post(`/services/${serviceName}/heartbeat?${params.toString()}`);
  }

  // Context and changes
  async getContext() {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const { data } = await this.client.get<ProjectContext>(`/context/${this.currentProjectId}`);
    return data;
  }

  async getChanges(since: number, agentId?: string) {
    if (!this.currentProjectId) {
      throw new Error('No project selected. Please select a project first.');
    }
    const params = new URLSearchParams();
    params.append('since', new Date(since * 1000).toISOString());
    params.append('project_id', this.currentProjectId.toString());
    if (agentId) params.append('agent_id', agentId);
    
    const { data } = await this.client.get<Changes>(`/changes?${params.toString()}`);
    return data;
  }

  async getChangelog(hours = 24) {
    const { data } = await this.client.get(`/changelog?hours=${hours}`);
    return data;
  }
}