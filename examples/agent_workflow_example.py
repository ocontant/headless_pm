#!/usr/bin/env python3
"""
Example agent workflow demonstration
Shows how an agent would interact with the Headless PM API
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:6969/api/v1"
API_KEY = "development-key"

class HeadlessPMAgent:
    def __init__(self, agent_id, role, level):
        self.agent_id = agent_id
        self.role = role
        self.level = level
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        self.last_poll_time = datetime.utcnow().isoformat() + "Z"
    
    def register(self):
        """Register agent with the system"""
        print(f"🚀 Registering agent: {self.agent_id}")
        
        response = requests.post(
            f"{BASE_URL}/register",
            headers=self.headers,
            json={
                "agent_id": self.agent_id,
                "role": self.role,
                "level": self.level
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Registered successfully!")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    
    def get_context(self):
        """Get project context"""
        print("📋 Getting project context...")
        
        response = requests.get(f"{BASE_URL}/context", headers=self.headers)
        
        if response.status_code == 200:
            context = response.json()
            print(f"📁 Project: {context['project_name']}")
            print(f"📖 Instructions: {context['instructions_path']}")
            return context
        else:
            print(f"❌ Failed to get context: {response.text}")
            return None
    
    def get_next_task(self):
        """Get next available task for this agent"""
        print(f"🔍 Looking for tasks for {self.role} (level: {self.level})...")
        
        response = requests.get(
            f"{BASE_URL}/tasks/next",
            headers=self.headers,
            params={"role": self.role, "level": self.level}
        )
        
        if response.status_code == 200:
            task = response.json()
            if task:
                print(f"📝 Found task: {task['title']} (ID: {task['id']})")
                print(f"   Status: {task['status']}")
                print(f"   Complexity: {task['complexity']}")
                print(f"   Branch: {task['branch']}")
                return task
            else:
                print("😴 No tasks available")
                return None
        else:
            print(f"❌ Failed to get tasks: {response.text}")
            return None
    
    def lock_task(self, task_id):
        """Lock a task to prevent duplicate work"""
        print(f"🔒 Locking task {task_id}...")
        
        response = requests.post(
            f"{BASE_URL}/tasks/{task_id}/lock",
            headers=self.headers,
            params={"agent_id": self.agent_id}
        )
        
        if response.status_code == 200:
            print("✅ Task locked successfully!")
            return True
        else:
            print(f"❌ Failed to lock task: {response.text}")
            return False
    
    def update_task_status(self, task_id, status, notes=None):
        """Update task status"""
        print(f"🔄 Updating task {task_id} to status: {status}")
        
        data = {"status": status}
        if notes:
            data["notes"] = notes
        
        response = requests.put(
            f"{BASE_URL}/tasks/{task_id}/status",
            headers=self.headers,
            params={"agent_id": self.agent_id},
            json=data
        )
        
        if response.status_code == 200:
            print(f"✅ Task status updated to: {status}")
            return True
        else:
            print(f"❌ Failed to update status: {response.text}")
            return False
    
    def post_update(self, doc_type, title, content):
        """Post a document update"""
        print(f"📝 Posting {doc_type}: {title}")
        
        response = requests.post(
            f"{BASE_URL}/documents",
            headers=self.headers,
            params={"author_id": self.agent_id},
            json={
                "doc_type": doc_type,
                "title": title,
                "content": content
            }
        )
        
        if response.status_code == 200:
            doc = response.json()
            print(f"✅ Document posted (ID: {doc['id']})")
            if doc['mentions']:
                print(f"   Mentioned: {', '.join(doc['mentions'])}")
            return doc
        else:
            print(f"❌ Failed to post document: {response.text}")
            return None
    
    def poll_for_changes(self):
        """Poll for changes since last check"""
        print(f"🔄 Polling for changes since {self.last_poll_time}")
        
        response = requests.get(
            f"{BASE_URL}/changes",
            headers=self.headers,
            params={
                "since": self.last_poll_time,
                "agent_id": self.agent_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            changes = data['changes']
            
            if changes:
                print(f"📢 Found {len(changes)} changes:")
                for change in changes:
                    print(f"   {change['type']}: {change['data']}")
            else:
                print("😴 No new changes")
            
            self.last_poll_time = data['last_timestamp']
            return changes
        else:
            print(f"❌ Failed to poll changes: {response.text}")
            return []

def simulate_frontend_developer():
    """Simulate a frontend developer agent workflow"""
    print("=" * 60)
    print("🎨 FRONTEND DEVELOPER AGENT SIMULATION")
    print("=" * 60)
    
    agent = HeadlessPMAgent("frontend_dev_demo_001", "frontend_dev", "senior")
    
    # Step 1: Register
    if not agent.register():
        return
    
    # Step 2: Get context
    agent.get_context()
    
    # Step 3: Look for work
    task = agent.get_next_task()
    
    if task:
        # Step 4: Lock the task
        if agent.lock_task(task['id']):
            
            # Step 5: Start work
            agent.update_task_status(task['id'], "under_work", "Starting implementation")
            
            # Step 6: Simulate work progress
            print("⚙️ Simulating development work...")
            time.sleep(2)
            
            # Step 7: Post progress update
            if task['complexity'] == 'major':
                git_workflow = """
## Development Progress

Working on: **{title}**

### Git Workflow (Major Task)
```bash
git checkout -b {branch}
# ... implementing feature ...
git add .
git commit -m "feat: {title}"
git push origin {branch}
# Will create PR when ready
```

### Progress
- ✅ Component structure created
- ✅ Basic styling implemented
- 🔄 Adding interactive functionality
- ⏳ Writing unit tests

@qa_senior_001 will be ready for testing soon
                """.format(title=task['title'], branch=task['branch'])
            else:
                git_workflow = """
## Development Progress

Working on: **{title}**

### Git Workflow (Minor Task)
```bash
git checkout main
git pull
# ... making changes ...
git add .
git commit -m "fix: {title}"
git push origin main
```

### Progress
- ✅ Issue identified
- ✅ Fix implemented
- ✅ Tested locally

Ready to commit directly to main branch.
                """.format(title=task['title'])
            
            agent.post_update("update", f"Progress on {task['title']}", git_workflow)
            
            # Step 8: Complete work
            print("⚙️ Completing work...")
            time.sleep(1)
            agent.update_task_status(task['id'], "dev_done", "Implementation complete, ready for QA")
            
            # Step 9: Final update
            completion_msg = f"""
# Task Completed: {task['title']}

## Summary
- Feature implemented successfully
- All requirements met
- {'PR created for review' if task['complexity'] == 'major' else 'Changes committed to main branch'}
- Ready for QA testing

## Next Steps
- @qa_senior_001 please test the changes
- {f"Review PR: {task['branch']}" if task['complexity'] == 'major' else "Changes are live on main branch"}
            """
            agent.post_update("update", f"Completed: {task['title']}", completion_msg)
    
    # Step 10: Poll for changes
    print("\n🔄 Checking for updates...")
    agent.poll_for_changes()
    
    print("\n✅ Frontend developer workflow complete!")

def simulate_architect():
    """Simulate an architect evaluating tasks"""
    print("\n" + "=" * 60)
    print("🏗️  ARCHITECT AGENT SIMULATION")
    print("=" * 60)
    
    agent = HeadlessPMAgent("architect_demo_001", "architect", "principal")
    
    # Register and get context
    agent.register()
    agent.get_context()
    
    # Look for tasks to evaluate
    task = agent.get_next_task()
    
    if task and task['status'] == 'created':
        print(f"📋 Evaluating task: {task['title']}")
        
        # Lock task for evaluation
        if agent.lock_task(task['id']):
            # Simulate evaluation process
            print("🔍 Reviewing task requirements...")
            time.sleep(1)
            
            # Approve the task
            response = requests.post(
                f"{BASE_URL}/tasks/{task['id']}/evaluate",
                headers=agent.headers,
                params={"agent_id": agent.agent_id},
                json={
                    "approved": True,
                    "comment": "Task looks good. Clear requirements and appropriate scope. Ready for implementation."
                }
            )
            
            if response.status_code == 200:
                print("✅ Task approved!")
                
                # Post architectural guidance
                guidance = f"""
# Task Approved: {task['title']}

## Architecture Review
- ✅ Requirements are clear and well-defined
- ✅ Task scope is appropriate for {task['difficulty']} level
- ✅ Complexity marked as {task['complexity']} - correct workflow applies

## Implementation Guidance
- Follow established patterns in the codebase
- Ensure comprehensive testing
- {"Create feature branch and submit PR" if task['complexity'] == 'major' else "Can commit directly to main branch"}

## Technical Notes
- Use existing component library where possible
- Follow accessibility guidelines
- Consider performance implications

@{task['target_role']}_senior_001 you can proceed with implementation
                """
                
                agent.post_update("update", f"Architecture Review: {task['title']}", guidance)
    
    print("\n✅ Architect workflow complete!")

if __name__ == "__main__":
    print("🚀 Headless PM Agent Workflow Demonstration")
    print("This script simulates how agents interact with the API")
    print()
    
    try:
        # Run frontend developer simulation
        simulate_frontend_developer()
        
        # Run architect simulation  
        simulate_architect()
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE!")
        print("Check the dashboard to see all the activity:")
        print("python -m src.cli.main dashboard")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")