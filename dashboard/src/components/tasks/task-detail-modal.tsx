'use client';

import { useState } from 'react';
import { Task, TaskStatus, TaskDifficulty, TaskComplexity, AgentRole, TaskUpdateRequest } from '@/lib/types';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useUpdateTaskDetails } from '@/lib/hooks/useApi';
import { 
  User, 
  Clock, 
  GitBranch, 
  Flag, 
  Calendar, 
  FileText,
  MessageSquare,
  ExternalLink,
  Edit,
  Save,
  X
} from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
}

const ROLE_COLORS = {
  frontend_dev: 'bg-blue-500 text-white',
  backend_dev: 'bg-green-500 text-white',
  qa: 'bg-purple-500 text-white',
  architect: 'bg-orange-500 text-white',
  pm: 'bg-red-500 text-white'
};

const DIFFICULTY_COLORS = {
  [TaskDifficulty.Junior]: 'bg-green-500 text-white',
  [TaskDifficulty.Senior]: 'bg-yellow-500 text-white',
  [TaskDifficulty.Principal]: 'bg-red-500 text-white'
};

const COMPLEXITY_COLORS = {
  [TaskComplexity.Minor]: 'bg-blue-500 text-white',
  [TaskComplexity.Major]: 'bg-orange-500 text-white'
};

const STATUS_COLORS = {
  [TaskStatus.Created]: 'bg-slate-100 text-slate-700',
  [TaskStatus.UnderWork]: 'bg-blue-100 text-blue-700',
  [TaskStatus.DevDone]: 'bg-green-100 text-green-700',
  [TaskStatus.QADone]: 'bg-purple-100 text-purple-700',
  [TaskStatus.DocumentationDone]: 'bg-orange-100 text-orange-700',
  [TaskStatus.Committed]: 'bg-emerald-100 text-emerald-700'
};

export function TaskDetailModal({ task, isOpen, onClose }: TaskDetailModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<TaskUpdateRequest>({});
  const updateTaskMutation = useUpdateTaskDetails();

  if (!task) return null;

  const handleEdit = () => {
    setEditData({
      title: task.title,
      description: task.description || '',
      target_role: task.target_role,
      difficulty: task.difficulty,
      complexity: task.complexity
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      await updateTaskMutation.mutateAsync({
        taskId: task.id,
        updates: editData
      });
      setIsEditing(false);
      // Note: The modal will automatically refresh via React Query cache invalidation
    } catch (error) {
      console.error('Failed to update task:', error);
      // TODO: Add proper error handling/toast
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData({});
  };

  const getTaskIcon = (title: string) => {
    const lower = title.toLowerCase();
    if (lower.includes('navigation') || lower.includes('ui')) return '🎨';
    if (lower.includes('login') || lower.includes('auth')) return '🔐';
    if (lower.includes('profile') || lower.includes('user')) return '👤';
    if (lower.includes('payment') || lower.includes('webhook')) return '💳';
    if (lower.includes('shopping') || lower.includes('cart')) return '🛒';
    if (lower.includes('database') || lower.includes('migration')) return '🗄️';
    if (lower.includes('search') || lower.includes('filter')) return '🔍';
    if (lower.includes('analytics') || lower.includes('dashboard')) return '📊';
    if (lower.includes('email') || lower.includes('template')) return '📧';
    if (lower.includes('error') || lower.includes('handling')) return '🔧';
    if (lower.includes('mobile') || lower.includes('responsive')) return '📱';
    if (lower.includes('test') || lower.includes('unit')) return '🧪';
    if (lower.includes('homepage') || lower.includes('home')) return '🏠';
    return '📋';
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-2xl">{getTaskIcon(isEditing ? editData.title || task.title : task.title)}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span>Task #{task.id}</span>
                <Badge className={STATUS_COLORS[task.status]}>
                  {task.status.replace('_', ' ')}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isEditing ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    disabled={updateTaskMutation.isPending}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={updateTaskMutation.isPending}
                  >
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </Button>
                </>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleEdit}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
              )}
            </div>
          </DialogTitle>
          {isEditing ? (
            <Input
              value={editData.title || ''}
              onChange={(e) => setEditData({ ...editData, title: e.target.value })}
              className="text-xl font-semibold mt-2"
              placeholder="Task title"
            />
          ) : (
            <div className="text-xl font-semibold text-foreground mt-2">{task.title}</div>
          )}
        </DialogHeader>

        <div className="space-y-6">
          {/* Metadata Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Task Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Role Field */}
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Role:</span>
                  {isEditing ? (
                    <Select
                      value={editData.target_role || task.target_role}
                      onValueChange={(value) => setEditData({ ...editData, target_role: value as AgentRole })}
                    >
                      <SelectTrigger className="w-[180px] h-7 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={AgentRole.FrontendDev}>Frontend Dev</SelectItem>
                        <SelectItem value={AgentRole.BackendDev}>Backend Dev</SelectItem>
                        <SelectItem value={AgentRole.QA}>QA</SelectItem>
                        <SelectItem value={AgentRole.Architect}>Architect</SelectItem>
                        <SelectItem value={AgentRole.ProjectPM}>Project PM</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge className={`text-xs ${ROLE_COLORS[task.target_role] || 'bg-gray-500 text-white'}`}>
                      {task.target_role.replace('_', ' ')}
                    </Badge>
                  )}
                </div>

                {/* Difficulty Field */}
                <div className="flex items-center gap-2">
                  <Flag className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Difficulty:</span>
                  {isEditing ? (
                    <Select
                      value={editData.difficulty || task.difficulty}
                      onValueChange={(value) => setEditData({ ...editData, difficulty: value as TaskDifficulty })}
                    >
                      <SelectTrigger className="w-[120px] h-7 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={TaskDifficulty.Junior}>Junior</SelectItem>
                        <SelectItem value={TaskDifficulty.Senior}>Senior</SelectItem>
                        <SelectItem value={TaskDifficulty.Principal}>Principal</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge className={`text-xs ${DIFFICULTY_COLORS[task.difficulty]}`}>
                      {task.difficulty.toUpperCase()}
                    </Badge>
                  )}
                </div>

                {/* Complexity Field */}
                <div className="flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Complexity:</span>
                  {isEditing ? (
                    <Select
                      value={editData.complexity || task.complexity}
                      onValueChange={(value) => setEditData({ ...editData, complexity: value as TaskComplexity })}
                    >
                      <SelectTrigger className="w-[100px] h-7 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={TaskComplexity.Minor}>Minor</SelectItem>
                        <SelectItem value={TaskComplexity.Major}>Major</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge className={`text-xs ${COMPLEXITY_COLORS[task.complexity]}`}>
                      {task.complexity.toUpperCase()}
                    </Badge>
                  )}
                </div>

                {task.assigned_agent_id && (
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Assigned:</span>
                    <Badge variant="outline" className="text-xs">
                      {task.assigned_agent_id}
                    </Badge>
                  </div>
                )}

                {task.locked_by && (
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Locked by:</span>
                    <Badge variant="outline" className="text-xs">
                      {task.locked_by}
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Timeline</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {task.created_at && (
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Created:</span>
                    <span className="text-sm">
                      {format(new Date(task.created_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                )}

                {task.updated_at && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Updated:</span>
                    <span className="text-sm">
                      {format(new Date(task.updated_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                )}

                {task.started_at && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Started:</span>
                    <span className="text-sm">
                      {format(new Date(task.started_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                )}

                {task.completed_at && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Completed:</span>
                    <span className="text-sm">
                      {format(new Date(task.completed_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Description Section */}
          {(task.description || isEditing) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Description
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isEditing ? (
                  <Textarea
                    value={editData.description || ''}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                    placeholder="Task description (supports Markdown)"
                    rows={6}
                    className="min-h-[150px]"
                  />
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{task.description}</ReactMarkdown>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Git Information */}
          {(task.git_branch || task.pr_url) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-4 w-4" />
                  Git Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {task.git_branch && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Branch:</span>
                    <Badge variant="outline" className="font-mono text-xs">
                      {task.git_branch}
                    </Badge>
                  </div>
                )}

                {task.pr_url && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Pull Request:</span>
                    <Button variant="link" size="sm" className="p-0 h-auto" asChild>
                      <a href={task.pr_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View PR
                      </a>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Comments Section - Placeholder for future implementation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Comments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Comments feature coming soon</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end pt-4">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}