'use client';

import { useState, useEffect } from 'react';
import { useApi, useEpics, useFeatures } from '@/lib/hooks/useApi';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Plus } from 'lucide-react';
import { AgentRole, TaskDifficulty, TaskComplexity } from '@/lib/types';
import { generateBranchName } from '@/lib/utils/branch-naming';
import { EpicCreateModal } from './epic-create-modal';
import { FeatureCreateModal } from './feature-create-modal';

interface TaskCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskCreated: () => void;
}

export function TaskCreateDialog({ 
  open, 
  onOpenChange, 
  onTaskCreated 
}: TaskCreateDialogProps) {
  const { client } = useApi();
  const { data: epics, refetch: refetchEpics } = useEpics();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedEpicId, setSelectedEpicId] = useState<string>('');
  const { data: features, refetch: refetchFeatures } = useFeatures(selectedEpicId ? parseInt(selectedEpicId) : undefined);
  
  // Modal states
  const [showEpicModal, setShowEpicModal] = useState(false);
  const [showFeatureModal, setShowFeatureModal] = useState(false);
  
  // Pending selections for auto-selection after creation
  const [pendingEpicSelection, setPendingEpicSelection] = useState<number | null>(null);
  const [pendingFeatureSelection, setPendingFeatureSelection] = useState<number | null>(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    feature_id: '',
    target_role: '',
    difficulty: '',
    complexity: '',
    branch: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      setFormData({
        title: '',
        description: '',
        feature_id: '',
        target_role: '',
        difficulty: '',
        complexity: '',
        branch: ''
      });
      setSelectedEpicId('');
      setErrors({});
      setShowEpicModal(false);
      setShowFeatureModal(false);
      setPendingEpicSelection(null);
      setPendingFeatureSelection(null);
    }
  }, [open]);

  // Auto-select newly created epic when epics data updates
  useEffect(() => {
    if (pendingEpicSelection && epics) {
      const epicExists = epics.some(epic => epic.id === pendingEpicSelection);
      if (epicExists) {
        setSelectedEpicId(pendingEpicSelection.toString());
        setFormData(prev => ({ ...prev, feature_id: '' })); // Clear feature selection
        setPendingEpicSelection(null);
      }
    }
  }, [epics, pendingEpicSelection]);

  // Auto-select newly created feature when features data updates
  useEffect(() => {
    if (pendingFeatureSelection && features) {
      const featureExists = features.some(feature => feature.id === pendingFeatureSelection);
      if (featureExists) {
        setFormData(prev => ({ ...prev, feature_id: pendingFeatureSelection.toString() }));
        setPendingFeatureSelection(null);
      }
    }
  }, [features, pendingFeatureSelection]);

  // Handle Epic Creation Success
  const handleEpicCreated = async (epicId: number) => {
    setPendingEpicSelection(epicId);
    await refetchEpics();
  };

  // Handle Feature Creation Success
  const handleFeatureCreated = async (featureId: number) => {
    setPendingFeatureSelection(featureId);
    await refetchFeatures();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      // Validate required fields
      const newErrors: Record<string, string> = {};
      if (!formData.title?.trim()) {
        newErrors.title = 'Task title is required';
      }
      if (!formData.feature_id) {
        newErrors.feature_id = 'Feature selection is required';
      }
      if (!formData.target_role) {
        newErrors.target_role = 'Target role is required';
      }
      if (!formData.difficulty) {
        newErrors.difficulty = 'Difficulty level is required';
      }
      if (!formData.complexity) {
        newErrors.complexity = 'Task complexity is required';
      }

      // Auto-generate branch name if empty
      const finalBranchName = formData.branch?.trim() || (formData.title?.trim() ? generateBranchName({ 
        title: formData.title,
        complexity: formData.complexity as 'major' | 'minor'
      }) : '');
      
      if (!finalBranchName) {
        newErrors.branch = 'Branch name is required (will be auto-generated from title)';
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        setIsLoading(false);
        return;
      }

      await client.createTask({
        title: formData.title?.trim() || '',
        description: formData.description?.trim() || '',
        feature_id: parseInt(formData.feature_id),
        target_role: formData.target_role as AgentRole,
        difficulty: formData.difficulty,
        complexity: formData.complexity,
        branch: finalBranchName
      });

      onTaskCreated();
    } catch (error: unknown) {
      console.error('Failed to create task:', error);
      const errorDetail = (error as any)?.response?.data?.detail;
      let errorMessage = 'Failed to create task. Please try again.';
      
      if (typeof errorDetail === 'string') {
        errorMessage = errorDetail;
      } else if (Array.isArray(errorDetail)) {
        // Handle validation errors (422 responses)
        errorMessage = errorDetail.map((err: any) => `${err.loc?.join('.')} ${err.msg}`).join(', ');
      }
      
      setErrors({ submit: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Auto-generate branch name when title changes, if branch is empty
    if (field === 'title' && !formData.branch?.trim() && value?.trim()) {
      const generatedBranch = generateBranchName({ 
        title: value,
        complexity: formData.complexity as 'major' | 'minor'
      });
      setFormData(prev => ({ ...prev, branch: generatedBranch }));
    }
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Create a new task and assign it to a feature and role.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto pr-2">
          <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {/* Task Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Task Title *</Label>
              <Input
                id="title"
                placeholder="Enter task title"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                className={errors.title ? 'border-destructive' : ''}
              />
              {errors.title && (
                <p className="text-sm text-destructive">{errors.title}</p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Enter task description (optional)"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
              />
            </div>

            {/* Epic Selection */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label htmlFor="epic">Epic *</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground"
                  onClick={() => setShowEpicModal(true)}
                  title="Create new epic"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <Select value={selectedEpicId || ''} onValueChange={setSelectedEpicId}>
                <SelectTrigger className={!selectedEpicId ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Select an epic" />
                </SelectTrigger>
                <SelectContent>
                  {epics?.map((epic) => (
                    <SelectItem key={epic.id} value={epic.id.toString()}>
                      {epic.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {!selectedEpicId && (
                <p className="text-sm text-muted-foreground">
                  Select an epic to see available features
                </p>
              )}
            </div>

            {/* Feature Selection */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label htmlFor="feature">Feature *</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground disabled:opacity-50"
                  onClick={() => setShowFeatureModal(true)}
                  disabled={!selectedEpicId}
                  title={selectedEpicId ? "Create new feature" : "Select an epic first"}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <Select 
                value={formData.feature_id || ''} 
                onValueChange={(value) => handleChange('feature_id', value)}
                disabled={!selectedEpicId}
              >
                <SelectTrigger className={errors.feature_id ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Select a feature" />
                </SelectTrigger>
                <SelectContent>
                  {features?.map((feature) => (
                    <SelectItem key={feature.id} value={feature.id.toString()}>
                      {feature.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.feature_id && (
                <p className="text-sm text-destructive">{errors.feature_id}</p>
              )}
            </div>

            {/* Target Role */}
            <div className="space-y-2">
              <Label htmlFor="target_role">Target Role *</Label>
              <Select 
                value={formData.target_role || ''} 
                onValueChange={(value) => handleChange('target_role', value)}
              >
                <SelectTrigger className={errors.target_role ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Select target role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={AgentRole.FrontendDev}>Frontend Developer</SelectItem>
                  <SelectItem value={AgentRole.BackendDev}>Backend Developer</SelectItem>
                  <SelectItem value={AgentRole.Architect}>Architect</SelectItem>
                  <SelectItem value={AgentRole.ProjectPM}>Project Manager</SelectItem>
                  <SelectItem value={AgentRole.QA}>QA Engineer</SelectItem>
                </SelectContent>
              </Select>
              {errors.target_role && (
                <p className="text-sm text-destructive">{errors.target_role}</p>
              )}
            </div>

            {/* Branch */}
            <div className="space-y-2">
              <Label htmlFor="branch">Branch Name</Label>
              <Input
                id="branch"
                placeholder="Auto-generated from title (e.g., feature/task-name)"
                value={formData.branch}
                onChange={(e) => handleChange('branch', e.target.value)}
                className={errors.branch ? 'border-destructive' : ''}
              />
              {errors.branch && (
                <p className="text-sm text-destructive">{errors.branch}</p>
              )}
              <p className="text-xs text-muted-foreground">
                Leave empty to auto-generate from task title. Format: feature/task-name, fix/issue-name
              </p>
            </div>

            {/* Difficulty and Complexity */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="difficulty">Difficulty *</Label>
                <Select 
                  value={formData.difficulty || ''} 
                  onValueChange={(value) => handleChange('difficulty', value)}
                >
                  <SelectTrigger className={errors.difficulty ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Select difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={TaskDifficulty.Junior}>Junior</SelectItem>
                    <SelectItem value={TaskDifficulty.Senior}>Senior</SelectItem>
                    <SelectItem value={TaskDifficulty.Principal}>Principal</SelectItem>
                  </SelectContent>
                </Select>
                {errors.difficulty && (
                  <p className="text-sm text-destructive">{errors.difficulty}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="complexity">Complexity *</Label>
                <Select 
                  value={formData.complexity || ''} 
                  onValueChange={(value) => handleChange('complexity', value)}
                >
                  <SelectTrigger className={errors.complexity ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Select complexity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={TaskComplexity.Minor}>Minor</SelectItem>
                    <SelectItem value={TaskComplexity.Major}>Major</SelectItem>
                  </SelectContent>
                </Select>
                {errors.complexity && (
                  <p className="text-sm text-destructive">{errors.complexity}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Major tasks require pull requests, minor tasks commit directly
                </p>
              </div>
            </div>
          </div>

          {errors.submit && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
              {errors.submit}
            </div>
          )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Task
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>

      {/* Epic Creation Modal */}
      <EpicCreateModal
        open={showEpicModal}
        onOpenChange={setShowEpicModal}
        onEpicCreated={handleEpicCreated}
      />

      {/* Feature Creation Modal */}
      <FeatureCreateModal
        open={showFeatureModal}
        onOpenChange={setShowFeatureModal}
        epicId={selectedEpicId ? parseInt(selectedEpicId) : null}
        epicName={epics?.find(e => e.id.toString() === selectedEpicId)?.name}
        onFeatureCreated={handleFeatureCreated}
      />
    </Dialog>
  );
}