'use client';

import { useState } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { TaskBoard } from '@/components/tasks/task-board-merged';
import { TaskFilters, type TaskFilters as TaskFiltersType } from '@/components/tasks/task-filters';
import { TaskStats } from '@/components/tasks/task-stats';
import { TaskTimeline } from '@/components/tasks/task-timeline';
import { TaskCreateDialog } from '@/components/tasks/task-create-dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LayoutGrid, Calendar, BarChart3, Plus } from 'lucide-react';
import { useTasks } from '@/lib/hooks/useApi';
import { useQueryClient } from '@tanstack/react-query';
import { useProjectContext } from '@/lib/contexts/project-context';

export default function TasksPage() {
  const [view, setView] = useState<'board' | 'timeline' | 'analytics'>('board');
  const [filters, setFilters] = useState<TaskFiltersType>({});
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const { currentProjectId } = useProjectContext();

  const handleTaskCreated = () => {
    // Refresh the tasks list
    queryClient.invalidateQueries({ queryKey: ['tasks', currentProjectId] });
    setCreateDialogOpen(false);
  };

  return (
    <PageLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Task Management</h1>
          <div className="flex items-center gap-4">
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Task
            </Button>
            <Tabs value={view} onValueChange={(v) => setView(v as any)} className="w-auto">
              <TabsList>
                <TabsTrigger value="board" className="flex items-center gap-2">
                  <LayoutGrid className="h-4 w-4" />
                  Board
                </TabsTrigger>
                <TabsTrigger value="timeline" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Timeline
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Analytics
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>

        <TaskFilters onFiltersChange={setFilters} />
        
        <div className="min-h-[600px]">
          {view === 'board' && <TaskBoard filters={filters} />}
          {view === 'timeline' && <TaskTimeline filters={filters} />}
          {view === 'analytics' && <TaskStats filters={filters} />}
        </div>
      </div>

      {/* Task Create Dialog */}
      <TaskCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onTaskCreated={handleTaskCreated}
      />
    </PageLayout>
  );
}