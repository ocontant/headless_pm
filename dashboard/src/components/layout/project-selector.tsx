'use client';

import { useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useProjectContext } from '@/lib/contexts/project-context';
import { Project } from '@/lib/types';
import { PlusCircle } from 'lucide-react';

interface ProjectSelectorProps {
  onProjectChange: (project: Project) => void;
  currentProject?: Project;
}

export function ProjectSelector({ onProjectChange, currentProject }: ProjectSelectorProps) {
  const { projects, apiClient, loadProjects } = useProjectContext();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    shared_path: './shared',
    instructions_path: './agent_instructions',
    project_docs_path: './docs'
  });
  const [isLoading, setIsLoading] = useState(false);

  // Projects are now loaded by context

  const handleCreateProject = async () => {
    setIsLoading(true);
    try {
      const newProject = await apiClient.createProject(formData);
      await loadProjects(); // Refresh projects list
      setIsCreateDialogOpen(false);
      setFormData({
        name: '',
        description: '',
        shared_path: './shared',
        instructions_path: './agent_instructions',
        project_docs_path: './docs'
      });
      onProjectChange(newProject);
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectSelect = (projectId: string) => {
    const project = projects.find(p => p.id === parseInt(projectId));
    if (project) {
      onProjectChange(project);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Select
        value={currentProject?.id.toString() || ''}
        onValueChange={handleProjectSelect}
      >
        <SelectTrigger className="w-[180px] h-9">
          <SelectValue placeholder="Select project" />
        </SelectTrigger>
        <SelectContent>
          {projects.map((project) => (
            <SelectItem key={project.id} value={project.id.toString()}>
              {project.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost" size="icon" className="h-9 w-9">
            <PlusCircle className="h-4 w-4" />
            <span className="sr-only">New Project</span>
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter project name"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter project description"
              />
            </div>
            <div>
              <Label htmlFor="shared_path">Shared Path</Label>
              <Input
                id="shared_path"
                value={formData.shared_path}
                onChange={(e) => setFormData({ ...formData, shared_path: e.target.value })}
                placeholder="./shared"
              />
            </div>
            <div>
              <Label htmlFor="instructions_path">Instructions Path</Label>
              <Input
                id="instructions_path"
                value={formData.instructions_path}
                onChange={(e) => setFormData({ ...formData, instructions_path: e.target.value })}
                placeholder="./agent_instructions"
              />
            </div>
            <div>
              <Label htmlFor="project_docs_path">Documentation Path</Label>
              <Input
                id="project_docs_path"
                value={formData.project_docs_path}
                onChange={(e) => setFormData({ ...formData, project_docs_path: e.target.value })}
                placeholder="./docs"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateProject}
                disabled={!formData.name || isLoading}
              >
                {isLoading ? 'Creating...' : 'Create Project'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}