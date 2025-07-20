/**
 * Branch naming utilities for task management
 * 
 * Naming Convention:
 * - feature/task-name - For new features (both major and minor tasks)
 * - fix/issue-name - For bug fixes  
 * - hotfix/critical-issue - For critical production fixes
 */

export interface BranchNameOptions {
  title: string;
  complexity?: 'major' | 'minor';
  type?: 'feature' | 'fix' | 'hotfix';
}

/**
 * Generates a branch name following the established naming convention
 * Examples:
 * - "Implement user login" -> "feature/implement-user-login"
 * - "Fix login validation bug" -> "fix/login-validation-bug"
 */
export function generateBranchName({ title, complexity, type }: BranchNameOptions): string {
  // Create a slug from the task title
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '') // Remove special characters except spaces and hyphens
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .replace(/^-|-$/g, '') // Remove leading/trailing hyphens
    .substring(0, 40); // Reasonable length limit
  
  // Determine prefix based on type or infer from title
  let prefix = type || 'feature';
  
  if (!type) {
    // Auto-detect type from title keywords
    const titleLower = title.toLowerCase();
    if (titleLower.includes('fix') || titleLower.includes('bug') || titleLower.includes('issue')) {
      prefix = 'fix';
    } else if (titleLower.includes('hotfix') || titleLower.includes('critical') || titleLower.includes('urgent')) {
      prefix = 'hotfix';
    }
  }
  
  return `${prefix}/${slug}`;
}

/**
 * Validates if a branch name follows the naming convention
 */
export function isValidBranchName(branchName: string): boolean {
  const pattern = /^(feature|fix|hotfix)\/[a-z0-9-]+$/;
  return pattern.test(branchName);
}

/**
 * Suggests a branch name based on common patterns
 */
export function suggestBranchName(title: string): string[] {
  const baseSlug = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 40);
    
  return [
    `feature/${baseSlug}`,
    `fix/${baseSlug}`,
    `hotfix/${baseSlug}`
  ];
}