'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Home, 
  Kanban, 
  Users, 
  MessageSquare, 
  BarChart3, 
  Activity,
  FolderOpen
} from 'lucide-react';
import { ProjectSelector } from './project-selector';
import { Project } from '@/lib/types';
import { useProjectContext } from '@/lib/contexts/project-context';
import { ThemeToggle } from '@/components/theme-toggle';
import { SettingsMenu } from './settings-menu';
import { MobileNav } from './mobile-nav';

const navigationItems = [
  {
    name: 'Overview',
    href: '/',
    icon: Home,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderOpen,
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: Kanban,
  },
  {
    name: 'Agents',
    href: '/agents',
    icon: Users,
  },
  {
    name: 'Communications',
    href: '/communications',
    icon: MessageSquare,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
  },
  {
    name: 'System Health',
    href: '/system-health',
    icon: Activity,
  },
];

interface NavigationProps {
  // No longer needed - project context handles state
}

export function Navigation({}: NavigationProps) {
  const pathname = usePathname();
  const { currentProject, setCurrentProject } = useProjectContext();

  const handleProjectChange = (project: Project) => {
    setCurrentProject(project);
  };

  return (
    <nav className="border-b">
      {/* Top bar with logo and project/settings */}
      <div className="container mx-auto px-4">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <MobileNav />
            
            <Link href="/" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold">PM</span>
              </div>
              <span className="font-semibold text-lg hidden sm:inline">Headless PM</span>
            </Link>
            
            <div className="h-4 w-px bg-border hidden sm:block" />
            
            <div className="hidden sm:block">
              <ProjectSelector 
                onProjectChange={handleProjectChange}
                currentProject={currentProject}
              />
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            <div className="sm:hidden">
              <ProjectSelector 
                onProjectChange={handleProjectChange}
                currentProject={currentProject}
              />
            </div>
            <ThemeToggle />
            <SettingsMenu />
          </div>
        </div>
      </div>
      
      {/* Navigation tabs below */}
      <div className="hidden md:block border-t bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="flex items-center gap-1 overflow-x-auto py-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || 
                (item.href !== '/' && pathname.startsWith(item.href));
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap",
                    isActive
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:bg-background/50 hover:text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}