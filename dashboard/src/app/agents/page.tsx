'use client';

import { useState } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { AgentGrid } from '@/components/agents/agent-grid';
import { AgentStats } from '@/components/agents/agent-stats';
import { AgentActivityFeed } from '@/components/agents/agent-activity-feed-real';
import { AgentFilters, AgentFilters as AgentFiltersType } from '@/components/agents/agent-filters';
import { AgentAvailabilityDashboard } from '@/components/agents/agent-availability-dashboard';
import { useProjectContext } from '@/lib/contexts/project-context';

export default function AgentsPage() {
  const [filters, setFilters] = useState<AgentFiltersType>({
    search: '',
    role: 'all',
    skillLevel: 'all',
    connectionType: 'all',
    status: 'all'
  });
  
  const { currentProject } = useProjectContext();

  return (
    <PageLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Agent Activity</h1>
        </div>

        <AgentStats />
        
        {/* Agent Availability Dashboard for Project PMs */}
        {currentProject && (
          <AgentAvailabilityDashboard projectId={currentProject.id} />
        )}
        
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div className="xl:col-span-3">
            <AgentFilters onFiltersChange={setFilters} />
          </div>
          <div className="xl:col-span-6">
            <AgentGrid filters={filters} />
          </div>
          <div className="xl:col-span-3">
            <AgentActivityFeed />
          </div>
        </div>
      </div>
    </PageLayout>
  );
}