'use client';

import { useState } from 'react';
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
import { useApi } from '@/lib/hooks/useApi';

interface FeatureCreateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  epicId: number | null;
  epicName?: string;
  onFeatureCreated: (featureId: number) => void;
}

export function FeatureCreateModal({ 
  open, 
  onOpenChange, 
  epicId,
  epicName,
  onFeatureCreated 
}: FeatureCreateModalProps) {
  const { client } = useApi();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      // Validate required fields
      if (!formData.name.trim()) {
        setErrors({ name: 'Feature name is required' });
        setIsLoading(false);
        return;
      }

      if (!epicId) {
        setErrors({ submit: 'Epic ID is required' });
        setIsLoading(false);
        return;
      }

      const feature = await client.createFeature(
        epicId,
        formData.name.trim(), 
        formData.description.trim()
      );

      onFeatureCreated(feature.id);
      onOpenChange(false);
      
      // Reset form
      setFormData({ name: '', description: '' });
    } catch (error: unknown) {
      console.error('Failed to create feature:', error);
      setErrors({ 
        submit: (error as any)?.response?.data?.detail || 'Failed to create feature. Please try again.' 
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

  const handleClose = () => {
    setFormData({ name: '', description: '' });
    setErrors({});
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Feature</DialogTitle>
          <DialogDescription>
            Create a new feature within the &quot;{epicName}&quot; epic.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="feature-name">Feature Name *</Label>
            <Input
              id="feature-name"
              placeholder="Enter feature name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className={errors.name ? 'border-destructive' : ''}
              autoFocus
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="feature-description">Description</Label>
            <Textarea
              id="feature-description"
              placeholder="Enter feature description (optional)"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={3}
            />
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
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Feature
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}