'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Project } from '@/lib/types';
import { HeadlessPMClient } from '@/lib/api/client';

interface ProjectContextType {
  currentProject: Project | null;
  currentProjectId: number | null;
  isLoading: boolean;
  projects: Project[];
  setCurrentProject: (project: Project | null) => void;
  loadProjects: () => Promise<void>;
  apiClient: HeadlessPMClient;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

interface ProjectProviderProps {
  children: ReactNode;
}

// Create API client instance
const apiClient = new HeadlessPMClient(
  process.env.NEXT_PUBLIC_API_URL,
  process.env.NEXT_PUBLIC_API_KEY
);

export function ProjectProvider({ children }: ProjectProviderProps) {
  const [currentProject, setCurrentProjectState] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      const projectsData = await apiClient.getProjects();
      setProjects(projectsData);
      
      // Auto-select Headless-PM project (ID 1) if no current project
      if (!currentProject && projectsData.length > 0) {
        const headlessPmProject = projectsData.find(p => p.id === 1 || p.name === 'Headless-PM');
        const defaultProject = headlessPmProject || projectsData[0];
        
        console.log('Auto-selecting default project:', defaultProject);
        setCurrentProject(defaultProject);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setCurrentProject = (project: Project | null) => {
    setCurrentProjectState(project);
    // Update API client with selected project
    if (project) {
      apiClient.setCurrentProject(project.id);
      console.log('Set current project in API client:', project.id);
    } else {
      apiClient.setCurrentProject(null);
    }
  };

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Debug logging
  useEffect(() => {
    console.log('ProjectContext state:', { currentProject, projects: projects.length, isLoading });
  }, [currentProject, projects, isLoading]);

  const value: ProjectContextType = {
    currentProject,
    currentProjectId: currentProject?.id || null,
    isLoading,
    projects,
    setCurrentProject,
    loadProjects,
    apiClient
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProjectContext() {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProjectContext must be used within a ProjectProvider');
  }
  return context;
}