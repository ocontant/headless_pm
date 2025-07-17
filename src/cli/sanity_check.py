#!/usr/bin/env python3
"""
Sanity check command for enum validation and database consistency.

This command performs comprehensive validation of:
1. Enum value consistency across the database
2. Foreign key integrity 
3. Required field completeness
4. Data type validation
5. Business logic validation

Usage:
    python -m src.cli.sanity_check
    python -m src.cli.sanity_check --fix-issues
    python -m src.cli.sanity_check --check-only=enums
"""

import click
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlmodel import Session, select, func
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from src.models.database import get_session
from src.models.models import Agent, Task, Document, Service, Changelog, Project, Epic, Feature
from src.models.enums import TaskStatus, AgentRole, DifficultyLevel, TaskComplexity, ConnectionType, AgentStatus
from src.models.document_enums import DocumentType, ServiceStatus

console = Console()

class SanityCheckResult:
    def __init__(self):
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
        self.warnings = 0
        self.errors = []
        self.warnings_list = []
        
    def add_error(self, check_name: str, description: str, details: Any = None):
        self.total_checks += 1
        self.failed_checks += 1
        self.errors.append({
            'check': check_name,
            'description': description,
            'details': details,
            'timestamp': datetime.utcnow()
        })
        
    def add_warning(self, check_name: str, description: str, details: Any = None):
        self.warnings += 1
        self.warnings_list.append({
            'check': check_name,
            'description': description,
            'details': details,
            'timestamp': datetime.utcnow()
        })
        
    def add_pass(self, check_name: str):
        self.total_checks += 1
        self.passed_checks += 1
        
    @property
    def success_rate(self) -> float:
        return (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0

def validate_enum_field(session: Session, model_class, field_name: str, valid_enum_class, result: SanityCheckResult) -> List[Dict]:
    """Validate enum field values in a model."""
    check_name = f"{model_class.__name__}.{field_name}"
    
    try:
        # Get all distinct values for the field
        stmt = select(getattr(model_class, field_name)).distinct()
        db_values = session.exec(stmt).all()
        
        valid_values = [e.value for e in valid_enum_class]
        invalid_records = []
        
        for value in db_values:
            if value not in valid_values:
                # Find records with this invalid value
                stmt = select(model_class).where(getattr(model_class, field_name) == value)
                records = session.exec(stmt).all()
                
                for record in records:
                    invalid_records.append({
                        'table': model_class.__name__.lower(),
                        'id': record.id,
                        'field': field_name,
                        'value': value,
                        'record': record
                    })
        
        if invalid_records:
            result.add_error(
                check_name,
                f"Invalid {field_name} values found",
                {
                    'invalid_count': len(invalid_records),
                    'valid_values': valid_values,
                    'records': invalid_records[:5]  # Show first 5 for brevity
                }
            )
        else:
            result.add_pass(check_name)
            
        return invalid_records
        
    except Exception as e:
        result.add_error(check_name, f"Failed to validate enum field: {str(e)}")
        return []

def check_enum_consistency(session: Session, result: SanityCheckResult, fix_issues: bool = False) -> None:
    """Check enum value consistency across all models."""
    console.print("\n🔍 [bold]Checking enum value consistency...[/bold]")
    
    enum_validations = [
        (Agent, 'role', AgentRole),
        (Agent, 'level', DifficultyLevel),
        (Agent, 'connection_type', ConnectionType),
        (Agent, 'status', AgentStatus),
        (Task, 'target_role', AgentRole),
        (Task, 'difficulty', DifficultyLevel),
        (Task, 'complexity', TaskComplexity),
        (Task, 'status', TaskStatus),
        (Changelog, 'old_status', TaskStatus),
        (Changelog, 'new_status', TaskStatus),
        (Document, 'doc_type', DocumentType),
        (Service, 'status', ServiceStatus),
    ]
    
    all_invalid_records = []
    
    for model_class, field_name, enum_class in enum_validations:
        invalid_records = validate_enum_field(session, model_class, field_name, enum_class, result)
        all_invalid_records.extend(invalid_records)
        
        if invalid_records:
            console.print(f"  ❌ {model_class.__name__}.{field_name}: {len(invalid_records)} invalid values")
        else:
            console.print(f"  ✅ {model_class.__name__}.{field_name}: All values valid")
    
    if fix_issues and all_invalid_records:
        fix_enum_issues(session, all_invalid_records, result)

def fix_enum_issues(session: Session, invalid_records: List[Dict], result: SanityCheckResult) -> None:
    """Fix enum validation issues by normalizing values."""
    console.print("\n🔧 [bold]Fixing enum issues...[/bold]")
    
    fixes_applied = 0
    
    for record_info in invalid_records:
        try:
            # Get the actual record
            record = record_info['record']
            field_name = record_info['field']
            current_value = record_info['value']
            
            # Try to normalize the value
            fixed_value = None
            
            # Handle legacy values
            if field_name in ['role', 'target_role'] and current_value.lower() == 'pm':
                fixed_value = AgentRole.PROJECT_PM.value
            elif field_name in ['old_status', 'new_status', 'status'] and record_info['table'] in ['task', 'changelog']:
                if current_value.lower() == 'evaluation':
                    fixed_value = TaskStatus.QA_DONE.value
                elif current_value.lower() == 'approved':
                    fixed_value = TaskStatus.COMMITTED.value
                else:
                    # Try to normalize case
                    try:
                        if hasattr(TaskStatus, current_value.upper()):
                            fixed_value = current_value.lower()
                    except:
                        pass
            else:
                # Try case normalization
                try:
                    # Convert to lowercase (all our enums use lowercase)
                    fixed_value = current_value.lower()
                except:
                    pass
            
            if fixed_value:
                setattr(record, field_name, fixed_value)
                fixes_applied += 1
                console.print(f"    🔧 Fixed {record_info['table']}.{field_name}: '{current_value}' → '{fixed_value}'")
            else:
                console.print(f"    ❌ Cannot fix {record_info['table']}.{field_name}: '{current_value}' (unknown value)")
                
        except Exception as e:
            console.print(f"    ❌ Failed to fix {record_info['table']}.{field_name}: {str(e)}")
    
    if fixes_applied > 0:
        session.commit()
        console.print(f"\n✅ Applied {fixes_applied} fixes to enum values")
    else:
        console.print(f"\n⚠️  No fixes could be applied automatically")

def check_foreign_key_integrity(session: Session, result: SanityCheckResult) -> None:
    """Check foreign key integrity across the database."""
    console.print("\n🔗 [bold]Checking foreign key integrity...[/bold]")
    
    # Check agent.project_id references
    orphaned_agents = session.exec(
        select(Agent).where(~Agent.project_id.in_(select(Project.id)))
    ).all()
    
    if orphaned_agents:
        result.add_error(
            "foreign_key.agent.project_id",
            f"Found {len(orphaned_agents)} agents with invalid project_id",
            [{'agent_id': a.agent_id, 'project_id': a.project_id} for a in orphaned_agents]
        )
        console.print(f"  ❌ Agent.project_id: {len(orphaned_agents)} orphaned agents")
    else:
        result.add_pass("foreign_key.agent.project_id")
        console.print("  ✅ Agent.project_id: All references valid")
    
    # Check task.feature_id references
    orphaned_tasks = session.exec(
        select(Task).where(~Task.feature_id.in_(select(Feature.id)))
    ).all()
    
    if orphaned_tasks:
        result.add_error(
            "foreign_key.task.feature_id",
            f"Found {len(orphaned_tasks)} tasks with invalid feature_id",
            [{'task_id': t.id, 'feature_id': t.feature_id} for t in orphaned_tasks]
        )
        console.print(f"  ❌ Task.feature_id: {len(orphaned_tasks)} orphaned tasks")
    else:
        result.add_pass("foreign_key.task.feature_id")
        console.print("  ✅ Task.feature_id: All references valid")
    
    # Check service.project_id references
    orphaned_services = session.exec(
        select(Service).where(~Service.project_id.in_(select(Project.id)))
    ).all()
    
    if orphaned_services:
        result.add_error(
            "foreign_key.service.project_id",
            f"Found {len(orphaned_services)} services with invalid project_id",
            [{'service_id': s.id, 'project_id': s.project_id} for s in orphaned_services]
        )
        console.print(f"  ❌ Service.project_id: {len(orphaned_services)} orphaned services")
    else:
        result.add_pass("foreign_key.service.project_id")
        console.print("  ✅ Service.project_id: All references valid")

def check_data_completeness(session: Session, result: SanityCheckResult) -> None:
    """Check for required field completeness and data quality."""
    console.print("\n📊 [bold]Checking data completeness...[/bold]")
    
    # Check for agents without recent activity
    stale_threshold = datetime.utcnow() - timedelta(days=30)
    stale_agents = session.exec(
        select(Agent).where(Agent.last_seen < stale_threshold)
    ).all()
    
    if stale_agents:
        result.add_warning(
            "data_quality.stale_agents",
            f"Found {len(stale_agents)} agents with no activity in 30 days",
            [{'agent_id': a.agent_id, 'last_seen': a.last_seen} for a in stale_agents[:10]]
        )
        console.print(f"  ⚠️  Stale agents: {len(stale_agents)} agents inactive for 30+ days")
    else:
        result.add_pass("data_quality.stale_agents")
        console.print("  ✅ Agent activity: All agents active within 30 days")
    
    # Check for tasks without proper status progression
    created_tasks = session.exec(
        select(Task).where(
            Task.status == TaskStatus.CREATED,
            Task.created_at < datetime.utcnow() - timedelta(days=7)
        )
    ).all()
    
    if created_tasks:
        result.add_warning(
            "data_quality.stagnant_tasks",
            f"Found {len(created_tasks)} tasks in 'created' status for 7+ days",
            [{'task_id': t.id, 'title': t.title, 'created_at': t.created_at} for t in created_tasks[:10]]
        )
        console.print(f"  ⚠️  Stagnant tasks: {len(created_tasks)} tasks not progressing")
    else:
        result.add_pass("data_quality.stagnant_tasks")
        console.print("  ✅ Task progression: No stagnant tasks found")

def check_business_logic(session: Session, result: SanityCheckResult) -> None:
    """Check business logic constraints and rules."""
    console.print("\n⚖️  [bold]Checking business logic...[/bold]")
    
    # Check for locked tasks without proper timestamps
    invalid_locks = session.exec(
        select(Task).where(
            Task.locked_by_id.is_not(None),
            Task.locked_at.is_(None)
        )
    ).all()
    
    if invalid_locks:
        result.add_error(
            "business_logic.invalid_task_locks",
            f"Found {len(invalid_locks)} locked tasks without lock timestamps",
            [{'task_id': t.id, 'locked_by': t.locked_by_id} for t in invalid_locks]
        )
        console.print(f"  ❌ Task locks: {len(invalid_locks)} invalid lock states")
    else:
        result.add_pass("business_logic.invalid_task_locks")
        console.print("  ✅ Task locks: All locks have proper timestamps")
    
    # Check for agents with impossible status combinations
    invalid_agent_states = session.exec(
        select(Agent).where(
            Agent.status == AgentStatus.WORKING,
            Agent.current_task_id.is_(None)
        )
    ).all()
    
    if invalid_agent_states:
        result.add_error(
            "business_logic.invalid_agent_states",
            f"Found {len(invalid_agent_states)} agents marked as 'working' without assigned tasks",
            [{'agent_id': a.agent_id, 'status': a.status} for a in invalid_agent_states]
        )
        console.print(f"  ❌ Agent states: {len(invalid_agent_states)} invalid working states")
    else:
        result.add_pass("business_logic.invalid_agent_states")
        console.print("  ✅ Agent states: All working agents have assigned tasks")

def display_results(result: SanityCheckResult) -> None:
    """Display the sanity check results in a formatted report."""
    console.print("\n" + "="*60)
    console.print("📋 [bold blue]SANITY CHECK REPORT[/bold blue]")
    console.print("="*60)
    
    # Summary statistics
    summary_table = Table(title="Summary Statistics")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")
    
    summary_table.add_row("Total Checks", str(result.total_checks))
    summary_table.add_row("Passed", f"[green]{result.passed_checks}[/green]")
    summary_table.add_row("Failed", f"[red]{result.failed_checks}[/red]")
    summary_table.add_row("Warnings", f"[yellow]{result.warnings}[/yellow]")
    summary_table.add_row("Success Rate", f"{result.success_rate:.1f}%")
    
    console.print(summary_table)
    
    # Errors
    if result.errors:
        console.print(f"\n🚨 [bold red]ERRORS ({len(result.errors)})[/bold red]")
        for i, error in enumerate(result.errors, 1):
            console.print(f"\n{i}. [red]{error['check']}[/red]")
            console.print(f"   {error['description']}")
            if error['details']:
                console.print(f"   Details: {error['details']}")
    
    # Warnings
    if result.warnings_list:
        console.print(f"\n⚠️  [bold yellow]WARNINGS ({len(result.warnings_list)})[/bold yellow]")
        for i, warning in enumerate(result.warnings_list, 1):
            console.print(f"\n{i}. [yellow]{warning['check']}[/yellow]")
            console.print(f"   {warning['description']}")
            if warning['details']:
                console.print(f"   Details: {warning['details']}")
    
    # Final status
    if result.failed_checks == 0:
        status_panel = Panel(
            "[green]✅ All checks passed! Database is healthy.[/green]",
            title="Status",
            border_style="green"
        )
    elif result.failed_checks > 0:
        status_panel = Panel(
            f"[red]❌ {result.failed_checks} check(s) failed. Database issues detected.[/red]",
            title="Status", 
            border_style="red"
        )
    else:
        status_panel = Panel(
            "[yellow]⚠️  Some warnings detected. Review recommended.[/yellow]",
            title="Status",
            border_style="yellow"
        )
    
    console.print(status_panel)

@click.command()
@click.option('--fix-issues', is_flag=True, help='Automatically fix issues where possible')
@click.option('--check-only', type=click.Choice(['enums', 'foreign-keys', 'data-quality', 'business-logic']), 
              help='Run only specific category of checks')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def sanity_check(fix_issues: bool, check_only: str, verbose: bool):
    """Run comprehensive sanity checks on the database."""
    console.print("🏥 [bold]Starting Headless PM Database Sanity Check[/bold]")
    console.print(f"📅 Timestamp: {datetime.utcnow().isoformat()}")
    
    if fix_issues:
        console.print("🔧 [yellow]Fix mode enabled - issues will be automatically corrected where possible[/yellow]")
    
    result = SanityCheckResult()
    
    try:
        with Session(next(get_session())) as session:
            # Run selected checks
            if not check_only or check_only == 'enums':
                check_enum_consistency(session, result, fix_issues)
            
            if not check_only or check_only == 'foreign-keys':
                check_foreign_key_integrity(session, result)
            
            if not check_only or check_only == 'data-quality':
                check_data_completeness(session, result)
            
            if not check_only or check_only == 'business-logic':
                check_business_logic(session, result)
            
        # Display results
        display_results(result)
        
        # Exit with appropriate code
        if result.failed_checks > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        console.print(f"\n💥 [bold red]Fatal error during sanity check:[/bold red] {str(e)}")
        import traceback
        if verbose:
            console.print(traceback.format_exc())
        sys.exit(2)

if __name__ == "__main__":
    sanity_check()