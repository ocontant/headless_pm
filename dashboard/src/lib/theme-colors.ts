// Theme-aware color mappings
// These use CSS variables that change based on dark/light mode

export const STATUS_COLORS = {
  // Task statuses
  created: 'bg-muted text-muted-foreground',
  assigned: 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300',
  in_progress: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300',
  dev_done: 'bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-300',
  qa_review: 'bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300',
  qa_pass: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  qa_fail: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300',
  completed: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  blocked: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300',
  cancelled: 'bg-muted text-muted-foreground',
};

export const DOCUMENT_TYPE_COLORS = {
  update: 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300',
  report: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  inquiry: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300',
  feedback: 'bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-300',
  note: 'bg-muted text-muted-foreground',
  default: 'bg-muted text-muted-foreground',
};

export const ROLE_COLORS = {
  frontend_dev: 'bg-blue-600 text-white',
  backend_dev: 'bg-green-600 text-white',
  qa: 'bg-purple-600 text-white',
  architect: 'bg-orange-600 text-white',
  pm: 'bg-pink-600 text-white',
};

export const AGENT_STATUS_COLORS = {
  active: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  inactive: 'bg-muted text-muted-foreground',
  stale: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300',
  offline: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300',
};

export const SERVICE_STATUS_COLORS = {
  healthy: 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  unhealthy: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300',
  unknown: 'bg-muted text-muted-foreground',
};