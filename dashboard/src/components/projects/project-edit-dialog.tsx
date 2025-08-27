'use client';

import { useState, useEffect } from 'react';
import { useApi } from '@/lib/hooks/useApi';
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
import { Loader2 } from 'lucide-react';
import { Project } from '@/lib/types';

interface ProjectEditDialogProps {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectUpdated: () => void;
}

export function ProjectEditDialog({ 
  project,
  open, 
  onOpenChange, 
  onProjectUpdated 
}: ProjectEditDialogProps) {
  const { client } = useApi();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    description: '',
    shared_path: '',
    instructions_path: '',
    project_docs_path: '',
    code_guidelines_path: '',
    
    // Repository configuration
    repository_url: '',
    repository_main_branch: 'main',
    repository_clone_path: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Update form data when project changes
  useEffect(() => {
    if (project) {
      setFormData({
        description: project.description || '',
        shared_path: project.shared_path || '',
        instructions_path: project.instructions_path || '',
        project_docs_path: project.project_docs_path || '',
        code_guidelines_path: project.code_guidelines_path || '',
        
        // Repository configuration
        repository_url: project.repository_url || '',
        repository_main_branch: project.repository_main_branch || 'main',
        repository_clone_path: project.repository_clone_path || ''
      });
      setErrors({});
    }
  }, [project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!project) return;
    
    setIsLoading(true);
    setErrors({});

    try {
      // Validate required fields
      const newErrors: Record<string, string> = {};
      if (!formData.shared_path.trim()) {
        newErrors.shared_path = 'Shared path is required';
      }
      if (!formData.instructions_path.trim()) {
        newErrors.instructions_path = 'Instructions path is required';
      }
      if (!formData.project_docs_path.trim()) {
        newErrors.project_docs_path = 'Project docs path is required';
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        setIsLoading(false);
        return;
      }

      await client.updateProject(project.id, {
        description: formData.description.trim() || undefined,
        shared_path: formData.shared_path.trim(),
        instructions_path: formData.instructions_path.trim(),
        project_docs_path: formData.project_docs_path.trim(),
        code_guidelines_path: formData.code_guidelines_path.trim() || undefined,
        
        // Repository configuration
        repository_url: formData.repository_url.trim() || undefined,
        repository_main_branch: formData.repository_main_branch.trim(),
        repository_clone_path: formData.repository_clone_path.trim() || undefined
      });

      onProjectUpdated();
    } catch (error: any) {
      console.error('Failed to update project:', error);
      setErrors({ 
        submit: error.response?.data?.detail || 'Failed to update project. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (!project) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>Edit Project: {project.name}</DialogTitle>
          <DialogDescription>
            Update project configuration and file paths.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto pr-2">
            <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {/* Project Name (read-only) */}
            <div className="space-y-2">
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                value={project.name}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground">
                Project name cannot be changed after creation
              </p>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Enter project description (optional)"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
              />
            </div>

            {/* File Paths */}
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="shared_path">Shared Path *</Label>
                <Input
                  id="shared_path"
                  placeholder="/shared"
                  value={formData.shared_path}
                  onChange={(e) => handleChange('shared_path', e.target.value)}
                  className={errors.shared_path ? 'border-destructive' : ''}
                />
                {errors.shared_path && (
                  <p className="text-sm text-destructive">{errors.shared_path}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Path for shared project files and resources
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="instructions_path">Instructions Path *</Label>
                <Input
                  id="instructions_path"
                  placeholder="/instructions"
                  value={formData.instructions_path}
                  onChange={(e) => handleChange('instructions_path', e.target.value)}
                  className={errors.instructions_path ? 'border-destructive' : ''}
                />
                {errors.instructions_path && (
                  <p className="text-sm text-destructive">{errors.instructions_path}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Path for agent instructions and role definitions
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="project_docs_path">Project Docs Path *</Label>
                <Input
                  id="project_docs_path"
                  placeholder="/docs"
                  value={formData.project_docs_path}
                  onChange={(e) => handleChange('project_docs_path', e.target.value)}
                  className={errors.project_docs_path ? 'border-destructive' : ''}
                />
                {errors.project_docs_path && (
                  <p className="text-sm text-destructive">{errors.project_docs_path}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Path for project documentation and artifacts
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="code_guidelines_path">Code Guidelines Path</Label>
                <Input
                  id="code_guidelines_path"
                  placeholder="/guidelines/code.md"
                  value={formData.code_guidelines_path}
                  onChange={(e) => handleChange('code_guidelines_path', e.target.value)}
                  className={errors.code_guidelines_path ? 'border-destructive' : ''}
                />
                {errors.code_guidelines_path && (
                  <p className="text-sm text-destructive">{errors.code_guidelines_path}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Path to code guidelines and coding standards (optional)
                </p>
              </div>
            </div>

            {/* Repository Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Repository Configuration</h3>
              
              <div className="space-y-2">
                <Label htmlFor="repository_url">Repository URL</Label>
                <Input
                  id="repository_url"
                  placeholder="Auto-generated from project name (e.g., http://localhost:8080/git/project-name.git)"
                  value={formData.repository_url}
                  onChange={(e) => handleChange('repository_url', e.target.value)}
                  className={errors.repository_url ? 'border-destructive' : ''}
                />
                {errors.repository_url && (
                  <p className="text-sm text-destructive">{errors.repository_url}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Git repository URL (auto-generated from project name if left empty)
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="repository_main_branch">Main Branch *</Label>
                  <Input
                    id="repository_main_branch"
                    placeholder="main"
                    value={formData.repository_main_branch}
                    onChange={(e) => handleChange('repository_main_branch', e.target.value)}
                    className={errors.repository_main_branch ? 'border-destructive' : ''}
                  />
                  {errors.repository_main_branch && (
                    <p className="text-sm text-destructive">{errors.repository_main_branch}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Main branch name (e.g., main, master)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="repository_clone_path">Clone Path</Label>
                  <Input
                    id="repository_clone_path"
                    placeholder="/opt/repos/project-name"
                    value={formData.repository_clone_path}
                    onChange={(e) => handleChange('repository_clone_path', e.target.value)}
                    className={errors.repository_clone_path ? 'border-destructive' : ''}
                  />
                  {errors.repository_clone_path && (
                    <p className="text-sm text-destructive">{errors.repository_clone_path}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Local path for repository clone (optional)
                  </p>
                </div>
              </div>
            </div>

            {/* Project Stats (read-only) */}
            <div className="space-y-2">
              <Label>Project Statistics</Label>
              <div className="grid grid-cols-3 gap-4 p-3 bg-muted rounded-md">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Agents</p>
                  <p className="text-lg font-semibold">{project.agent_count || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Epics</p>
                  <p className="text-lg font-semibold">{project.epic_count || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Tasks</p>
                  <p className="text-lg font-semibold">{project.task_count || 0}</p>
                </div>
              </div>
            </div>
          </div>
            </div>

            {errors.submit && (
              <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
                {errors.submit}
              </div>
            )}
          </div>

          <DialogFooter className="flex-shrink-0">
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
              Update Project
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}