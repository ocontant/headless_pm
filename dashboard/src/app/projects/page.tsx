'use client';

import { useState } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { useProjects } from '@/lib/hooks/useApi';
import { useProjectContext } from '@/lib/contexts/project-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  Trash2, 
  Users, 
  Briefcase,
  Activity,
  MoreHorizontal,
  Edit
} from 'lucide-react';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Project } from '@/lib/types';
import { ProjectCreateDialog } from '@/components/projects/project-create-dialog';
import { ProjectEditDialog } from '@/components/projects/project-edit-dialog';
import { ProjectDeleteDialog } from '@/components/projects/project-delete-dialog';

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();
  const { loadProjects } = useProjectContext();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [deletingProject, setDeletingProject] = useState<Project | null>(null);

  const handleProjectCreated = () => {
    loadProjects(); // Refresh the projects list
    setCreateDialogOpen(false);
  };

  const handleProjectUpdated = () => {
    loadProjects(); // Refresh the projects list
    setEditingProject(null);
  };

  const handleProjectDeleted = () => {
    loadProjects(); // Refresh the projects list
    setDeletingProject(null);
  };

  if (isLoading) {
    return (
      <PageLayout>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold">Projects</h1>
            <Button disabled>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-muted rounded"></div>
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded"></div>
                    <div className="h-4 bg-muted rounded w-1/2"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Projects</h1>
            <p className="text-muted-foreground mt-1">
              Manage your project portfolio
            </p>
          </div>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
                  <p className="text-2xl font-bold">{projects?.length || 0}</p>
                </div>
                <Briefcase className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Agents</p>
                  <p className="text-2xl font-bold">
                    {projects?.reduce((sum, p) => sum + (p.agent_count || 0), 0) || 0}
                  </p>
                </div>
                <Users className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Epics</p>
                  <p className="text-2xl font-bold">
                    {projects?.reduce((sum, p) => sum + (p.epic_count || 0), 0) || 0}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects?.map((project) => (
            <Card 
              key={project.id} 
              className="relative cursor-pointer hover:shadow-lg transition-shadow"
              onDoubleClick={() => setEditingProject(project)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {project.description || 'No description provided'}
                    </CardDescription>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem 
                        onClick={() => setEditingProject(project)}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Edit Project
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={() => setDeletingProject(project)}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete Project
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-primary">{project.agent_count || 0}</p>
                      <p className="text-xs text-muted-foreground">Agents</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600">{project.epic_count || 0}</p>
                      <p className="text-xs text-muted-foreground">Epics</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">{project.task_count || 0}</p>
                      <p className="text-xs text-muted-foreground">Tasks</p>
                    </div>
                  </div>

                  {/* Project Info */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Created:</span>
                      <span>{new Date(project.created_at).toLocaleDateString()}</span>
                    </div>
                    {project.updated_at && project.updated_at !== project.created_at && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Updated:</span>
                        <span>{new Date(project.updated_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                </div>
              </CardContent>
            </Card>
          ))}

          {/* Empty State */}
          {(!projects || projects.length === 0) && (
            <Card className="col-span-full">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Briefcase className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Create your first project to get started with task management
                </p>
                <Button onClick={() => setCreateDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Project
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Dialogs */}
      <ProjectCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onProjectCreated={handleProjectCreated}
      />

      <ProjectEditDialog
        project={editingProject}
        open={!!editingProject}
        onOpenChange={(open) => !open && setEditingProject(null)}
        onProjectUpdated={handleProjectUpdated}
      />

      <ProjectDeleteDialog
        project={deletingProject}
        open={!!deletingProject}
        onOpenChange={(open) => !open && setDeletingProject(null)}
        onProjectDeleted={handleProjectDeleted}
      />
    </PageLayout>
  );
}