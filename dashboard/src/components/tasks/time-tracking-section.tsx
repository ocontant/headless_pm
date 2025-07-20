'use client';

import { useState } from 'react';
import { TimeEntry, TaskTimeTracking, TimeEntryCreateRequest } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useTaskTimeTracking, useAddTimeEntry, useDeleteTimeEntry } from '@/lib/hooks/useApi';
import { 
  Clock, 
  Plus, 
  Minus, 
  Trash2, 
  Calendar,
  AlertCircle,
  Loader2,
  Info
} from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

interface TimeTrackingSectionProps {
  taskId: number;
}

const TIME_SHORTCUTS = [
  { label: '15m', value: '15m', description: '15 minutes' },
  { label: '30m', value: '30m', description: '30 minutes' },
  { label: '1h', value: '1h', description: '1 hour' },
  { label: '2h', value: '2h', description: '2 hours' },
  { label: '4h', value: '4h', description: '4 hours' },
  { label: '1d', value: '1d', description: '1 day (8 hours)' },
];

const QUICK_REMOVES = [
  { label: '-15m', value: '-15m', description: 'Remove 15 minutes' },
  { label: '-30m', value: '-30m', description: 'Remove 30 minutes' },
  { label: '-1h', value: '-1h', description: 'Remove 1 hour' },
];

export function TimeTrackingSection({ taskId }: TimeTrackingSectionProps) {
  const [timeInput, setTimeInput] = useState('');
  const [description, setDescription] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  const { data: timeTracking, isLoading, error } = useTaskTimeTracking(taskId);
  const addTimeEntryMutation = useAddTimeEntry();
  const deleteTimeEntryMutation = useDeleteTimeEntry();

  const handleAddTime = async (timeValue?: string, desc?: string) => {
    const time = timeValue || timeInput;
    const finalDescription = desc || description;
    
    if (!time.trim()) return;

    try {
      const request: TimeEntryCreateRequest = {
        time_input: time,
        description: finalDescription || undefined
      };
      
      await addTimeEntryMutation.mutateAsync({ taskId, request });
      
      // Reset form
      setTimeInput('');
      setDescription('');
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to add time entry:', error);
    }
  };

  const handleDeleteEntry = async (entryId: number) => {
    try {
      await deleteTimeEntryMutation.mutateAsync({ entryId, taskId });
    } catch (error) {
      console.error('Failed to delete time entry:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleAddTime();
    }
  };

  const formatTimeEntry = (entry: TimeEntry) => {
    const isNegative = entry.minutes < 0;
    const absMinutes = Math.abs(entry.minutes);
    
    if (absMinutes >= 1440) {
      const days = Math.floor(absMinutes / 1440);
      const hours = Math.floor((absMinutes % 1440) / 60);
      const mins = absMinutes % 60;
      
      let formatted = `${days}d`;
      if (hours > 0) formatted += ` ${hours}h`;
      if (mins > 0) formatted += ` ${mins}m`;
      
      return isNegative ? `-${formatted}` : formatted;
    } else if (absMinutes >= 60) {
      const hours = Math.floor(absMinutes / 60);
      const mins = absMinutes % 60;
      
      let formatted = `${hours}h`;
      if (mins > 0) formatted += ` ${mins}m`;
      
      return isNegative ? `-${formatted}` : formatted;
    } else {
      return `${isNegative ? '-' : ''}${absMinutes}m`;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Time Tracking
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Time Tracking
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-center gap-2 text-red-700">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">Failed to load time tracking data</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Time Tracking
          </div>
          {timeTracking && (
            <Badge variant="outline" className="text-lg font-mono">
              {timeTracking.total_formatted}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Quick Actions */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Quick Add:</span>
            <div className="flex flex-wrap gap-1">
              {TIME_SHORTCUTS.map((shortcut) => (
                <Button
                  key={shortcut.value}
                  variant="outline"
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={() => handleAddTime(shortcut.value, 'Quick time entry')}
                  disabled={addTimeEntryMutation.isPending}
                  title={shortcut.description}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  {shortcut.label}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Quick Remove:</span>
            <div className="flex flex-wrap gap-1">
              {QUICK_REMOVES.map((remove) => (
                <Button
                  key={remove.value}
                  variant="outline"
                  size="sm"
                  className="h-7 px-2 text-xs text-red-600 border-red-200 hover:bg-red-50"
                  onClick={() => handleAddTime(remove.value, 'Time removal')}
                  disabled={addTimeEntryMutation.isPending}
                  title={remove.description}
                >
                  <Minus className="h-3 w-3 mr-1" />
                  {remove.label}
                </Button>
              ))}
            </div>
          </div>
        </div>

        <Separator />

        {/* Custom Time Entry Form */}
        {showAddForm ? (
          <div className="space-y-3 border rounded-md p-3 bg-slate-50">
            <div className="flex gap-2">
              <div className="flex-1">
                <Input
                  placeholder="e.g., 2h, 30m, 1d, 1w, 1M, -15m"
                  value={timeInput}
                  onChange={(e) => setTimeInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={addTimeEntryMutation.isPending}
                />
                <div className="text-xs text-muted-foreground mt-1">
                  Formats: 1m, 1h, 1d, 1w, 1M. Use negative values to remove time.
                </div>
              </div>
            </div>
            <Textarea
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={addTimeEntryMutation.isPending}
              rows={2}
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowAddForm(false);
                  setTimeInput('');
                  setDescription('');
                }}
                disabled={addTimeEntryMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={() => handleAddTime()}
                disabled={addTimeEntryMutation.isPending || !timeInput.trim()}
              >
                {addTimeEntryMutation.isPending ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="h-3 w-3 mr-1" />
                    Add Time
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddForm(true)}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Custom Time Entry
          </Button>
        )}

        {/* Error Display */}
        {addTimeEntryMutation.isError && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-center gap-2 text-red-700">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">
              Failed to add time entry: {addTimeEntryMutation.error instanceof Error ? addTimeEntryMutation.error.message : 'Unknown error'}
            </span>
          </div>
        )}

        {deleteTimeEntryMutation.isError && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-center gap-2 text-red-700">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">
              Failed to delete time entry: {deleteTimeEntryMutation.error instanceof Error ? deleteTimeEntryMutation.error.message : 'Unknown error'}
            </span>
          </div>
        )}

        {/* Time Entries List */}
        {timeTracking && timeTracking.entries.length > 0 && (
          <>
            <Separator />
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Calendar className="h-3 w-3" />
                Time Entries ({timeTracking.entries.length})
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {timeTracking.entries.map((entry) => (
                  <div
                    key={entry.id}
                    className="flex items-center justify-between p-2 border rounded text-sm hover:bg-slate-50"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant={entry.minutes < 0 ? "destructive" : "default"}
                          className="font-mono text-xs"
                        >
                          {formatTimeEntry(entry)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                        </span>
                      </div>
                      {entry.description && (
                        <div className="text-xs text-muted-foreground mt-1 truncate">
                          {entry.description}
                        </div>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteEntry(entry.id)}
                      disabled={deleteTimeEntryMutation.isPending}
                      className="h-6 w-6 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                      title="Delete time entry"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Info about time tracking */}
        {!timeTracking || timeTracking.entries.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">
            <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No time entries yet</p>
            <p className="text-xs">Add time using the shortcuts above or custom entries</p>
          </div>
        ) : null}

        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 flex items-start gap-2 text-blue-700">
          <Info className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div className="text-xs">
            <div className="font-medium mb-1">Time Tracking Tips:</div>
            <ul className="list-disc list-inside space-y-0.5 text-xs">
              <li>Use shortcuts: 1m, 1h, 1d, 1w, 1M</li>
              <li>Use negative values to remove time (e.g., -30m)</li>
              <li>Press Ctrl+Enter to quickly add custom entries</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}