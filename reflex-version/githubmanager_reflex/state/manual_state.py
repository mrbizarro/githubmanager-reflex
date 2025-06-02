"""
Manual entry state management
"""

import reflex as rx
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, date

class ManualIssue(rx.Base):
    """Manual issue data structure"""
    title: str
    body: str
    labels: List[str] = []
    assignees: List[str] = []
    priority: str = "normal"
    created_at: str

class ManualMilestone(rx.Base):
    """Manual milestone data structure"""
    description: str
    due_date: Optional[str] = None
    state: str = "open"
    issues: List[ManualIssue] = []
    created_at: str

class ManualState(rx.State):
    """State for manual milestone and issue creation"""
    
    # Manual data
    manual_milestones: Dict[str, ManualMilestone] = {}
    
    # Form state for new milestone
    new_milestone_title: str = ""
    new_milestone_desc: str = ""
    new_milestone_due_date: Optional[str] = None
    new_milestone_state: str = "open"
    
    # Form state for new issue
    selected_milestone: str = ""
    new_issue_title: str = ""
    new_issue_body: str = ""
    new_issue_labels: str = ""
    new_issue_assignees: str = ""
    new_issue_priority: str = "normal"
    
    # UI state
    view_mode: str = "compact"  # compact, detailed
    show_summary: bool = False
    
    # Editing state
    editing_milestone: str = ""
    editing_issue_index: int = -1
    
    def clear_all_entries(self):
        """Clear all manual entries"""
        self.manual_milestones = {}
        self.clear_milestone_form()
        self.clear_issue_form()
        
        from .app_state import AppState
        self.get_state(AppState).show_notification_message("All manual entries cleared!", "info")
    
    def clear_milestone_form(self):
        """Clear milestone form"""
        self.new_milestone_title = ""
        self.new_milestone_desc = ""
        self.new_milestone_due_date = None
        self.new_milestone_state = "open"
    
    def clear_issue_form(self):
        """Clear issue form"""
        self.new_issue_title = ""
        self.new_issue_body = ""
        self.new_issue_labels = ""
        self.new_issue_assignees = ""
        self.new_issue_priority = "normal"
    
    def set_view_mode(self, mode: str):
        """Set view mode for preview"""
        self.view_mode = mode
    
    def toggle_summary(self):
        """Toggle summary view"""
        self.show_summary = not self.show_summary
    
    def add_milestone(self):
        """Add new milestone"""
        if not self.new_milestone_title.strip():
            from .app_state import AppState
            self.get_state(AppState).show_notification_message("Please enter a milestone title", "error")
            return
        
        if self.new_milestone_title in self.manual_milestones:
            from .app_state import AppState
            self.get_state(AppState).show_notification_message(
                f"Milestone '{self.new_milestone_title}' already exists!", "error"
            )
            return
        
        # Create milestone
        milestone = ManualMilestone(
            description=self.new_milestone_desc,
            due_date=self.new_milestone_due_date,
            state=self.new_milestone_state,
            issues=[],
            created_at=datetime.now().isoformat()
        )
        
        self.manual_milestones[self.new_milestone_title] = milestone
        
        from .app_state import AppState
        self.get_state(AppState).show_notification_message(
            f"Added milestone: {self.new_milestone_title}", "success"
        )
        
        # Clear form
        self.clear_milestone_form()
    
    def delete_milestone(self, milestone_name: str):
        """Delete milestone"""
        if milestone_name in self.manual_milestones:
            del self.manual_milestones[milestone_name]
            
            from .app_state import AppState
            self.get_state(AppState).show_notification_message(
                f"Deleted milestone: {milestone_name}", "success"
            )
    
    def add_issue(self):
        """Add new issue to selected milestone"""
        if not self.new_issue_title.strip():
            from .app_state import AppState
            self.get_state(AppState).show_notification_message("Please enter an issue title", "error")
            return
        
        if not self.selected_milestone or self.selected_milestone not in self.manual_milestones:
            from .app_state import AppState
            self.get_state(AppState).show_notification_message("Please select a milestone", "error")
            return
        
        # Process labels and assignees
        labels = [l.strip() for l in self.new_issue_labels.split(',') if l.strip()]
        assignees = [a.strip() for a in self.new_issue_assignees.split(',') if a.strip()]
        
        # Add priority label if not normal
        if self.new_issue_priority != 'normal':
            labels.append(f'priority-{self.new_issue_priority}')
        
        # Create issue
        issue = ManualIssue(
            title=self.new_issue_title,
            body=self.new_issue_body,
            labels=labels,
            assignees=assignees,
            priority=self.new_issue_priority,
            created_at=datetime.now().isoformat()
        )
        
        # Add to milestone
        self.manual_milestones[self.selected_milestone].issues.append(issue)
        
        from .app_state import AppState
        self.get_state(AppState).show_notification_message(
            f"Added issue '{self.new_issue_title}' to {self.selected_milestone}", "success"
        )
        
        # Clear form
        self.clear_issue_form()
    
    def delete_issue(self, milestone_name: str, issue_index: int):
        """Delete issue from milestone"""
        if (milestone_name in self.manual_milestones and 
            0 <= issue_index < len(self.manual_milestones[milestone_name].issues)):
            
            issue_title = self.manual_milestones[milestone_name].issues[issue_index].title
            del self.manual_milestones[milestone_name].issues[issue_index]
            
            from .app_state import AppState
            self.get_state(AppState).show_notification_message(
                f"Deleted issue: {issue_title}", "success"
            )
    
    def get_milestone_options(self) -> List[str]:
        """Get list of milestone names for selection"""
        return list(self.manual_milestones.keys())
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total_milestones = len(self.manual_milestones)
        total_issues = sum(len(m.issues) for m in self.manual_milestones.values())
        avg_issues = round(total_issues / total_milestones, 1) if total_milestones > 0 else 0
        
        return {
            'total_milestones': total_milestones,
            'total_issues': total_issues,
            'avg_issues_per_milestone': avg_issues,
            'entry_mode': 'Manual'
        }
    
    def get_priority_icon(self, priority: str) -> str:
        """Get icon for priority level"""
        priority_icons = {
            'low': '🟢',
            'normal': '🔵',
            'high': '🟡',
            'critical': '🔴'
        }
        return priority_icons.get(priority, '🔵')
    
    def export_data(self) -> str:
        """Export manual data as JSON"""
        # Convert to serializable format
        export_data = {}
        for name, milestone in self.manual_milestones.items():
            export_data[name] = {
                'description': milestone.description,
                'due_date': milestone.due_date,
                'state': milestone.state,
                'created_at': milestone.created_at,
                'issues': [
                    {
                        'title': issue.title,
                        'body': issue.body,
                        'labels': issue.labels,
                        'assignees': issue.assignees,
                        'priority': issue.priority,
                        'created_at': issue.created_at
                    }
                    for issue in milestone.issues
                ]
            }
        
        return json.dumps(export_data, indent=2)
    
    def convert_to_deployment_format(self) -> Dict[str, Any]:
        """Convert manual data to deployment format"""
        deployment_data = {}
        
        for name, milestone in self.manual_milestones.items():
            deployment_data[name] = {
                'description': milestone.description,
                'due_date': milestone.due_date,
                'state': milestone.state,
                'issues': [
                    {
                        'title': issue.title,
                        'body': issue.body,
                        'labels': issue.labels,
                        'assignees': issue.assignees
                    }
                    for issue in milestone.issues
                ]
            }
        
        return deployment_data
    
    async def deploy_manual_entries(self, dry_run: bool = False, create_labels: bool = True):
        """Deploy manual entries using deployment state"""
        if not self.manual_milestones:
            from .app_state import AppState
            self.get_state(AppState).show_notification_message("No entries to deploy", "error")
            return
        
        # Convert to deployment format
        deployment_data = self.convert_to_deployment_format()
        
        # Use deployment state
        from .deployment_state import DeploymentState
        deployment_state = await self.get_state(DeploymentState)
        deployment_state.set_deployment_options(dry_run, create_labels)
        await deployment_state.deploy_projects(deployment_data)
    
    def update_milestone_form(self, title: str, desc: str, due_date: Optional[str], state: str):
        """Update milestone form fields"""
        self.new_milestone_title = title
        self.new_milestone_desc = desc
        self.new_milestone_due_date = due_date
        self.new_milestone_state = state
    
    def update_issue_form(self, milestone: str, title: str, body: str, labels: str, assignees: str, priority: str):
        """Update issue form fields"""
        self.selected_milestone = milestone
        self.new_issue_title = title
        self.new_issue_body = body
        self.new_issue_labels = labels
        self.new_issue_assignees = assignees
        self.new_issue_priority = priority
