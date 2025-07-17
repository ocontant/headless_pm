'use client';

import { useState } from 'react';
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

interface ProjectCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectCreated: () => void;
}

export function ProjectCreateDialog({ 
  open, 
  onOpenChange, 
  onProjectCreated 
}: ProjectCreateDialogProps) {
  const { client } = useApi();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    shared_path: '/shared',
    instructions_path: '/instructions',
    project_docs_path: '/docs',
    code_guidelines_path: '/guidelines/code.md'
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      // Validate required fields
      const newErrors: Record<string, string> = {};
      if (!formData.name.trim()) {
        newErrors.name = 'Project name is required';
      }
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

      await client.createProject({
        name: formData.name.trim(),
        description: formData.description.trim(),
        shared_path: formData.shared_path.trim(),
        instructions_path: formData.instructions_path.trim(),
        project_docs_path: formData.project_docs_path.trim(),
        code_guidelines_path: formData.code_guidelines_path.trim() || undefined
      });

      // Reset form
      setFormData({
        name: '',
        description: '',
        shared_path: '/shared',
        instructions_path: '/instructions',
        project_docs_path: '/docs',
        code_guidelines_path: '/guidelines/code.md'
      });

      onProjectCreated();
    } catch (error: any) {
      console.error('Failed to create project:', error);
      setErrors({ 
        submit: error.response?.data?.detail || 'Failed to create project. Please try again.' 
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Set up a new project with its configuration and file paths.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                placeholder="Enter project name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className={errors.name ? 'border-destructive' : ''}
              />
              {errors.name && (
                <p className="text-sm text-destructive">{errors.name}</p>
              )}
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
              Create Project
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}