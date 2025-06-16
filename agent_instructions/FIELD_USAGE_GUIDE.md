# Field Usage Guide for All Agents

## Important Update: Enhanced Description Fields

All description, notes, comment, and content fields in the Headless PM system now support **unlimited text** (TEXT type instead of VARCHAR(255)). This enhancement allows agents to provide comprehensive, detailed information without space constraints.

## Why This Matters

- **Reduce Communication Overhead**: Detailed descriptions minimize back-and-forth clarifications
- **Better Context**: Other agents can understand tasks fully without additional queries
- **Self-Contained Work Items**: Tasks and documents should contain all necessary information
- **Improved Efficiency**: Less time spent asking for clarifications, more time doing actual work

## Fields That Support Extended Content

### Task Fields
- **description**: Use this for comprehensive task details including:
  - Detailed requirements and acceptance criteria
  - Technical specifications and constraints
  - API endpoints, data structures, dependencies
  - UI/UX requirements with mockup descriptions
  - Performance requirements and benchmarks
  - Security considerations
  - Testing requirements
  - Migration or backward compatibility notes

- **notes**: Use for:
  - Implementation suggestions
  - Warnings or gotchas
  - Related documentation links
  - Historical context
  - Decisions made during development

### Document Fields
- **content**: Provide exhaustive details including:
  - Complete technical specifications
  - Detailed bug reports with reproduction steps
  - Comprehensive status updates
  - Full architectural decisions with rationale
  - Complete test results and analysis

### Evaluation Fields
- **comment**: When evaluating tasks, provide:
  - Detailed feedback on what needs improvement
  - Specific code locations that need changes
  - Architectural concerns with examples
  - Performance analysis with metrics
  - Security audit findings

## Best Practices

1. **Assume No Prior Context**: Write descriptions as if the reader has no previous knowledge of the discussion
2. **Include Examples**: Provide code snippets, API examples, or UI mockups where relevant
3. **Structure Your Content**: Use markdown formatting for clarity:
   - Headers for sections
   - Bullet points for lists
   - Code blocks for technical details
   - Tables for comparisons

4. **Be Specific**: Instead of "Fix the bug in authentication", write:
   ```
   Fix JWT token expiration bug in /api/auth/refresh endpoint
   
   ## Problem
   The refresh token endpoint returns 401 even with valid refresh tokens when accessed exactly at token expiration time.
   
   ## Root Cause
   Race condition between token validation and expiration check in auth.service.ts:142
   
   ## Required Changes
   1. Add 5-second grace period to token validation
   2. Update tests to cover edge case
   3. Add retry logic to frontend auth interceptor
   
   ## Testing
   - Unit test for grace period logic
   - Integration test for concurrent refresh attempts
   - E2E test for token refresh during active session
   ```

5. **Think Long-Term**: Your descriptions will be referenced by:
   - Other agents working on related tasks
   - QA agents writing test cases
   - Future agents maintaining the code
   - PM agents tracking progress

## Examples by Role

### PM Creating Tasks
```markdown
## Task: Implement User Dashboard Analytics Widget

### Overview
Create a new analytics widget for the user dashboard showing key metrics with real-time updates via WebSocket.

### Requirements
1. Display metrics: Active users, API calls/min, Error rate, Response time
2. Real-time updates every 5 seconds via WebSocket subscription
3. Responsive design: Mobile (320px), Tablet (768px), Desktop (1200px+)
4. Accessibility: WCAG 2.1 AA compliant, keyboard navigable, screen reader friendly

### Technical Specifications
- Component: `AnalyticsWidget.tsx` in `/src/components/dashboard/`
- WebSocket channel: `analytics.user.{userId}`
- State management: Use existing Redux slice `analytics`
- Charts: Use Recharts library (already in package.json)

### API Integration
- Endpoint: `GET /api/v1/users/{userId}/analytics`
- WebSocket: Subscribe to `analytics.updates` channel
- Data format: `{ timestamp, activeUsers, apiCalls, errorRate, avgResponseTime }`

### Performance Requirements
- Initial load: < 200ms
- Update rendering: < 50ms
- Memory usage: < 10MB for 1 hour of data

### Error Handling
- Show skeleton loader during initial fetch
- Display cached data if WebSocket disconnects
- Graceful degradation to polling if WebSocket unavailable
```

### QA Reporting Bugs
```markdown
## Bug: Payment Processing Fails for Amounts Over $999.99

### Environment
- Version: 2.3.4-beta
- Browser: Chrome 122.0.6261.112, Safari 17.2.1
- OS: macOS 14.2.1, Windows 11
- Server: Production (api.example.com)
- User Role: Premium subscriber

### Reproduction Steps
1. Login as premium user (test account: premium.test@example.com)
2. Navigate to Settings > Billing > Make Payment
3. Enter amount: $1,000.00
4. Select payment method: Visa ending in 4242
5. Click "Process Payment"
6. Observe error: "Invalid amount format"

### Test Data
- User ID: 12345
- Subscription ID: sub_1234567890
- Payment method ID: pm_1234567890
- Timestamp: 2024-03-14T10:30:00Z

### Expected Result
Payment should process successfully for any amount up to $10,000 limit

### Actual Result
- Error message: "Invalid amount format"
- Console error: `TypeError: Cannot read property 'toFixed' of null at formatCurrency (billing.js:234)`
- Network request: POST /api/payments returns 400 Bad Request
- Request payload: `{ amount: "1,000.00", currency: "USD" }` (note the comma)

### Root Cause Analysis
The frontend is sending formatted currency string with comma separators, but the API expects a numeric value.

### Impact
- Severity: High
- Affected users: All users attempting payments over $999.99
- Business impact: Blocking high-value transactions
- Frequency: 100% reproducible

### Additional Evidence
- HAR file: payment_error_trace.har
- Console logs: console_output.txt
- Video recording: bug_reproduction.mp4
- Backend logs correlation ID: 550e8400-e29b-41d4-a716-446655440000

### Suggested Fix
In `/src/utils/payment.js` line 45:
```javascript
// Current
const amount = formatCurrency(value); // Returns "1,000.00"

// Suggested
const amount = parseFloat(value.replace(/,/g, '')); // Returns 1000.00
```

### Regression Notes
- Last working version: 2.3.2
- Likely introduced in PR #456 "Add currency formatting"
- Related tickets: BUG-789, BUG-790
```

## Remember

The goal is to make every task, document, and evaluation self-contained. Another agent should be able to pick up your work without needing to ask you any questions. Use the unlimited space wisely to provide comprehensive, well-structured information that accelerates the entire team's productivity.