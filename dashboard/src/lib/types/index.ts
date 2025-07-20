// API Types based on Headless PM models

export enum AgentRole {
  FrontendDev = "frontend_dev",
  BackendDev = "backend_dev",
  QA = "qa", 
  Architect = "architect",
  ProjectPM = "project_pm",
  UIAdmin = "ui_admin"
}

export enum SkillLevel {
  Junior = "junior",
  Senior = "senior",
  Principal = "principal"
}

export enum ConnectionType {
  Client = "client",
  MCP = "mcp",
  UI = "ui"
}

export enum TaskStatus {
  Created = "created",
  UnderWork = "under_work",
  DevDone = "dev_done",
  QADone = "qa_done",
  DocumentationDone = "documentation_done",
  Committed = "committed",
  // Legacy statuses (deprecated)
  Evaluation = "evaluation",
  Approved = "approved"
}

export enum TaskDifficulty {
  Junior = "junior",
  Senior = "senior",
  Principal = "principal"
}

export enum TaskComplexity {
  Minor = "minor",
  Major = "major"
}

export enum TaskType {
  Regular = "regular",
  Waiting = "waiting",
  Management = "management"
}

export enum AgentStatus {
  Idle = "idle",
  Working = "working",
  Offline = "offline"
}

export enum DocumentType {
  Comment = "comment",
  Update = "update",
  Question = "question",
  Issue = "issue",
  Note = "note",
  Announcement = "announcement",
  Decision = "decision",
  Report = "report"
}

export interface Project {
  id: number;
  name: string;
  description: string;
  shared_path: string;
  instructions_path: string;
  project_docs_path: string;
  code_guidelines_path?: string;
  
  // Repository configuration
  repository_url: string;
  repository_main_branch: string;
  repository_clone_path?: string;
  
  created_at: string;
  updated_at: string;
  agent_count?: number;
  epic_count?: number;
  task_count?: number;
}

export interface Agent {
  id: number;
  agent_id: string;
  project_id: number;
  project_name?: string;
  role: AgentRole;
  level: SkillLevel; // API uses 'level' not 'skill_level'
  skill_level?: SkillLevel; // Keep for backward compatibility
  name?: string;
  connection_type: ConnectionType;
  status: AgentStatus;
  current_task_id?: number;
  created_at?: string;
  last_seen?: string;
  last_activity?: string;
}

export interface AgentAvailability {
  agent_id: string;
  project_id: number;
  is_available: boolean;
  current_task_id?: number;
  current_task_title?: string;
  last_activity: string;
  status: AgentStatus;
}

export interface Epic {
  id: number;
  name: string;
  description?: string;
  pm_id?: string;
  created_at: string;
  updated_at?: string;
  task_count?: number;
  completed_task_count?: number;
  in_progress_task_count?: number;
  features?: Feature[];
}

export interface Feature {
  id: number;
  epic_id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  task_count?: number;
  completed_task_count?: number;
  in_progress_task_count?: number;
  tasks?: Task[];
}

export interface Task {
  id: number;
  feature_id: number;
  title: string;
  description?: string;
  target_role: AgentRole;           // Fixed: was assigned_role
  locked_by?: string;               // Fixed: was assigned_agent_id
  difficulty: TaskDifficulty;
  complexity: TaskComplexity;
  status: TaskStatus;
  branch: string;                   // Fixed: was branch_name
  created_by: string;               // Added: missing field
  locked_at?: string;               // Added: missing field
  notes?: string;                   // Added: missing field
  created_at: string;
  updated_at?: string;
  task_type?: TaskType;             // Added: missing field
  poll_interval?: number;           // Added: missing field
  total_time_minutes?: number;      // Time tracking
  total_time_formatted?: string;    // Human-readable time
  assigned_agent?: Agent;           // Keep for UI convenience
  comments?: TaskComment[];
}

export interface TaskComment {
  id: number;
  task_id: number;
  agent_id: string;
  content: string;
  created_at: string;
  agent?: Agent;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  target_role?: AgentRole;
  difficulty?: TaskDifficulty;
  complexity?: TaskComplexity;
  assigned_agent_id?: string;
}

export interface TimeEntryCreateRequest {
  time_input: string;
  description?: string;
}

export interface TimeEntry {
  id: number;
  task_id: number;
  minutes: number;
  description?: string;
  created_by: string;
  created_at: string;
}

export interface TaskTimeTracking {
  total_minutes: number;
  total_formatted: string;
  entries: TimeEntry[];
}

export interface Document {
  id: number;
  doc_type: DocumentType;
  title: string;
  content: string;
  author_id: string;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  meta_data?: any;
  mentions: string[]; // Array of mentioned agent IDs
  author?: Agent;
}

export interface Mention {
  id: number;
  document_id?: number;
  task_id?: number;
  task_comment_id?: number;
  mentioned_agent_id: string;
  created_by: string;
  is_read: boolean;
  created_at: string;
  document_title?: string;
  task_title?: string;
  document?: Document;
  task_comment?: TaskComment;
  mentioned_agent?: Agent;
  mentioned_by_agent?: Agent;
}

export interface Service {
  id: number;
  service_name: string;
  owner_agent_id: string;
  ping_url?: string;
  port?: number;
  status: "up" | "down" | "starting";
  last_heartbeat?: string;
  last_ping_at?: string;
  last_ping_success?: boolean;
  meta_data?: Record<string, any>;
  updated_at?: string;
}

export interface ProjectContext {
  project_id: number;
  project_name: string;
  shared_path: string;
  instructions_path: string;
  project_docs_path: string;
  code_guidelines_path?: string;
  database_type: string;
}

export interface Changes {
  timestamp: number;
  tasks: Task[];
  documents: Document[];
  mentions: Mention[];
  services: Service[];
}