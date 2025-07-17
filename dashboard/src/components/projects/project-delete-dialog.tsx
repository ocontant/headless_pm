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
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, AlertTriangle } from 'lucide-react';
import { Project } from '@/lib/types';

interface ProjectDeleteDialogProps {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectDeleted: () => void;
}

export function ProjectDeleteDialog({ 
  project,
  open, 
  onOpenChange, 
  onProjectDeleted 
}: ProjectDeleteDialogProps) {
  const { client } = useApi();
  const [isLoading, setIsLoading] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [forceDelete, setForceDelete] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!project) return;
    
    setIsLoading(true);
    setError('');

    try {
      await client.deleteProject(project.id);
      onProjectDeleted();
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      setError(error.response?.data?.detail || 'Failed to delete project. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const resetState = () => {
    setConfirmationText('');
    setForceDelete(false);
    setError('');
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      resetState();
    }
    onOpenChange(open);
  };

  if (!project) return null;

  const isConfirmationValid = confirmationText === project.name;
  const hasData = (project.agent_count || 0) > 0 || (project.epic_count || 0) > 0 || (project.task_count || 0) > 0;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Delete Project
          </DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete the project and all associated data.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Project Info */}
          <div className="p-4 bg-muted rounded-md">
            <h4 className="font-semibold text-sm mb-2">Project: {project.name}</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Agents</p>
                <p className="font-medium">{project.agent_count || 0}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Epics</p>
                <p className="font-medium">{project.epic_count || 0}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Tasks</p>
                <p className="font-medium">{project.task_count || 0}</p>
              </div>
            </div>
          </div>

          {/* Warning for projects with data */}
          {hasData && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-md">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium text-destructive mb-1">Warning: Project contains data</p>
                  <p className="text-destructive/80">
                    This project contains {project.agent_count || 0} agents, {project.epic_count || 0} epics, 
                    and {project.task_count || 0} tasks. All of this data will be permanently deleted.
                  </p>
                </div>
              </div>
              
              <div className="mt-3 flex items-center space-x-2">
                <Checkbox 
                  id="force-delete" 
                  checked={forceDelete}
                  onCheckedChange={(checked) => setForceDelete(checked as boolean)}
                />
                <Label htmlFor="force-delete" className="text-sm">
                  I understand that this will delete all project data
                </Label>
              </div>
            </div>
          )}

          {/* Confirmation Input */}
          <div className="space-y-2">
            <Label htmlFor="confirmation">
              Type <code className="bg-muted px-1 py-0.5 rounded text-sm">{project.name}</code> to confirm deletion:
            </Label>
            <Input
              id="confirmation"
              placeholder={`Type "${project.name}" here`}
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              className={!isConfirmationValid && confirmationText ? 'border-destructive' : ''}
            />
          </div>

          {error && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
              {error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button 
            variant="destructive" 
            onClick={handleDelete}
            disabled={
              isLoading || 
              !isConfirmationValid || 
              (hasData && !forceDelete)
            }
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Delete Project
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}