#!/usr/bin/env python3
"""
Real-time CLI Dashboard for Headless PM
"""

import time
import os
from datetime import datetime, timedelta
from typing import Dict, List
import requests
import json
from sqlmodel import Session, select
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich import box
from rich.text import Text

from src.models.database import get_session
from src.models.models import Agent, Task, Service, Document, Changelog
from src.models.enums import TaskStatus, AgentRole
from src.models.document_enums import ServiceStatus, DocumentType

class HeadlessPMDashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.setup_layout()
        
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        self.layout["left"].split_column(
            Layout(name="tasks", ratio=1),
            Layout(name="agents", ratio=2)
        )
        
        self.layout["right"].split_column(
            Layout(name="services", ratio=1),
            Layout(name="activity", ratio=2)
        )

    def get_db(self) -> Session:
        """Get database session"""
        return next(get_session())

    def render_header(self) -> Panel:
        """Render the header panel"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = Text("🚀 Headless PM - Real-time Dashboard", style="bold blue")
        subtitle = Text(f"Last updated: {now}", style="dim")
        
        return Panel(
            f"{title}\n{subtitle}",
            box=box.ROUNDED,
            style="blue"
        )

    def render_tasks(self) -> Panel:
        """Render the tasks panel"""
        db = self.get_db()
        
        # Get task counts by status
        task_counts = {}
        for status in TaskStatus:
            count = len(db.exec(select(Task).where(Task.status == status)).all())
            task_counts[status.value] = count
        
        # Get recent tasks
        recent_tasks = db.exec(
            select(Task).order_by(Task.updated_at.desc()).limit(8)
        ).all()
        
        table = Table(title="Tasks", box=box.MINIMAL)
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Recent Task", style="green")
        table.add_column("Assignee", style="yellow")
        
        status_colors = {
            "created": "red",
            "evaluation": "yellow", 
            "approved": "blue",
            "under_work": "magenta",
            "dev_done": "green",
            "qa_done": "cyan",
            "documentation_done": "bright_green",
            "committed": "bright_blue"
        }
        
        for i, (status, count) in enumerate(task_counts.items()):
            status_display = status.replace('_', ' ').title()
            color = status_colors.get(status, "white")
            
            if i < len(recent_tasks):
                task = recent_tasks[i]
                task_title = task.title[:25] + "..." if len(task.title) > 25 else task.title
                assignee = task.target_role.value if task.target_role else "-"
                locked_by = f"🔒 {task.locked_by_agent.agent_id}" if task.locked_by_agent else assignee
            else:
                task_title = "-"
                locked_by = "-"
            
            table.add_row(
                f"[{color}]{status_display}[/{color}]",
                str(count),
                task_title,
                locked_by
            )
        
        return Panel(table, title="Task Overview", border_style="green")

    def render_agents(self) -> Panel:
        """Render the agents panel"""
        db = self.get_db()
        
        agents = db.exec(select(Agent).order_by(Agent.last_seen.desc())).all()
        
        table = Table(title="Active Agents", box=box.MINIMAL)
        table.add_column("Agent", style="cyan")
        table.add_column("Role", style="green")  
        table.add_column("Type", justify="center", style="blue")
        table.add_column("Open Tasks", justify="center", style="magenta")
        table.add_column("Last Seen", style="yellow")
        
        for agent in agents[:10]:  # Show top 10 most recent
            # Count open tasks for this agent
            open_tasks_count = len(db.exec(
                select(Task).where(
                    Task.locked_by_id == agent.id,
                    Task.status != TaskStatus.COMMITTED
                )
            ).all())
            
            last_seen = agent.last_seen
            if last_seen:
                time_diff = datetime.utcnow() - last_seen
                if time_diff < timedelta(minutes=5):
                    status = "🟢 Active"
                elif time_diff < timedelta(minutes=30):
                    status = "🟡 Recent"
                else:
                    status = "🔴 Idle"
                
                time_str = last_seen.strftime("%H:%M")
            else:
                status = "❓ Unknown"
                time_str = "Never"
            
            agent_display = agent.agent_id.replace('_', ' ').title()
            role_display = agent.role.value.replace('_', ' ').title()
            connection_type = getattr(agent, 'connection_type', None)
            type_display = connection_type.value.upper() if connection_type else "CLIENT"
            
            table.add_row(agent_display, role_display, type_display, str(open_tasks_count), f"{status} {time_str}")
        
        return Panel(table, title="Agent Status", border_style="cyan")

    def render_services(self) -> Panel:
        """Render the services panel"""
        db = self.get_db()
        
        services = db.exec(select(Service).order_by(Service.updated_at.desc())).all()
        
        table = Table(title="Services", box=box.MINIMAL)
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Health", style="magenta")
        table.add_column("Port", justify="right")
        table.add_column("Owner", style="yellow")
        
        for service in services[:8]:  # Show top 8 services
            status_icon = {
                ServiceStatus.UP: "🟢",
                ServiceStatus.DOWN: "🔴", 
                ServiceStatus.STARTING: "🟡"
            }.get(service.status, "❓")
            
            # Health check status
            if service.last_ping_at:
                time_since_ping = datetime.utcnow() - service.last_ping_at
                if time_since_ping < timedelta(minutes=2):
                    if service.last_ping_success:
                        health_str = "✅ Healthy"
                    else:
                        health_str = "❌ Failed"
                else:
                    health_str = "⏰ Stale"
            else:
                health_str = "🔍 Never"
            
            port_str = str(service.port) if service.port else "-"
            owner = service.owner_agent_id
            
            table.add_row(
                service.service_name,
                f"{status_icon} {service.status.value}",
                health_str,
                port_str,
                owner
            )
        
        return Panel(table, title="Service Registry", border_style="yellow")


    def render_activity(self) -> Panel:
        """Render the recent activity panel"""
        db = self.get_db()
        
        # Get recent activity from multiple sources
        activities = []
        
        # Recent documents
        recent_docs = db.exec(
            select(Document).order_by(Document.created_at.desc()).limit(5)
        ).all()
        
        for doc in recent_docs:
            icon = {
                DocumentType.STANDUP: "📊",
                DocumentType.CRITICAL_ISSUE: "🚨",
                DocumentType.SERVICE_STATUS: "⚙️",
                DocumentType.UPDATE: "📝"
            }.get(doc.doc_type, "📄")
            
            activities.append({
                "time": doc.created_at,
                "text": f"{icon} {doc.author_id}: {doc.title[:30]}{'...' if len(doc.title) > 30 else ''}",
                "type": "document"
            })
        
        # Recent task changes
        recent_changes = db.exec(
            select(Changelog).order_by(Changelog.changed_at.desc()).limit(5)
        ).all()
        
        for change in recent_changes:
            task = db.get(Task, change.task_id)
            if task:
                activities.append({
                    "time": change.changed_at,
                    "text": f"🔄 {change.changed_by}: {task.title[:25]}{'...' if len(task.title) > 25 else ''} → {change.new_status.value}",
                    "type": "task_change"
                })
        
        # Sort by time
        activities.sort(key=lambda x: x["time"], reverse=True)
        
        table = Table(title="Recent Activity", box=box.MINIMAL)
        table.add_column("Time", style="dim")
        table.add_column("Activity", style="white")
        
        for activity in activities[:10]:  # Show top 10 activities
            time_str = activity["time"].strftime("%H:%M:%S")
            table.add_row(time_str, activity["text"])
        
        return Panel(table, title="Live Activity Feed", border_style="magenta")

    def render_footer(self) -> Panel:
        """Render the footer panel"""
        db = self.get_db()
        
        # Get summary stats
        total_tasks = len(db.exec(select(Task)).all())
        active_agents = len(db.exec(
            select(Agent).where(Agent.last_seen > datetime.utcnow() - timedelta(hours=1))
        ).all())
        active_services = len(db.exec(
            select(Service).where(Service.status == ServiceStatus.UP)
        ).all())
        
        stats = f"📋 {total_tasks} tasks | 👥 {active_agents} active agents | ⚙️ {active_services} services running"
        controls = "Press Ctrl+C to exit | Updates every 2 seconds"
        
        return Panel(
            f"{stats}\n{controls}",
            title="System Status",
            border_style="blue"
        )

    def render_dashboard(self) -> Layout:
        """Render the complete dashboard"""
        self.layout["header"].update(self.render_header())
        self.layout["tasks"].update(self.render_tasks())
        self.layout["agents"].update(self.render_agents())
        self.layout["services"].update(self.render_services())
        self.layout["activity"].update(self.render_activity())
        self.layout["footer"].update(self.render_footer())
        
        return self.layout

    def run(self):
        """Run the live dashboard"""
        self.console.print("🚀 Starting Headless PM Dashboard...", style="bold green")
        self.console.print("Press Ctrl+C to exit", style="dim")
        
        try:
            with Live(self.render_dashboard(), refresh_per_second=0.5, screen=True) as live:
                while True:
                    time.sleep(2)  # Update every 2 seconds
                    live.update(self.render_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n👋 Dashboard stopped. Goodbye!", style="bold blue")

if __name__ == "__main__":
    dashboard = HeadlessPMDashboard()
    dashboard.run()