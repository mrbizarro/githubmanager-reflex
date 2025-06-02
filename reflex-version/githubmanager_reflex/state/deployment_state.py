"""
GitHub deployment state management
"""

import reflex as rx
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

class DeploymentLogEntry(rx.Base):
    """Log entry for deployment process"""
    timestamp: str
    icon: str
    message: str

class DeploymentState(rx.State):
    """State for GitHub deployment operations"""
    
    # Deployment status
    status: str = "pending"  # pending, running, completed, error
    progress: int = 0
    current_action: str = ""
    
    # Metrics
    created_milestones: int = 0
    created_issues: int = 0
    
    # Logs and errors
    logs: List[DeploymentLogEntry] = []
    errors: List[str] = []
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Options
    dry_run: bool = False
    create_labels: bool = True
    
    def reset_deployment(self):
        """Reset deployment state to initial values"""
        self.status = "pending"
        self.progress = 0
        self.current_action = ""
        self.created_milestones = 0
        self.created_issues = 0
        self.logs = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def set_deployment_options(self, dry_run: bool = False, create_labels: bool = True):
        """Set deployment options"""
        self.dry_run = dry_run
        self.create_labels = create_labels
    
    def add_log(self, icon: str, message: str):
        """Add entry to deployment log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = DeploymentLogEntry(
            timestamp=timestamp,
            icon=icon,
            message=message
        )
        self.logs.append(log_entry)
    
    def add_error(self, error_message: str):
        """Add error to deployment state"""
        self.errors.append(error_message)
    
    def update_progress(self, progress: int, action: str = ""):
        """Update deployment progress"""
        self.progress = max(0, min(100, progress))
        if action:
            self.current_action = action
    
    async def deploy_projects(self, projects: Dict[str, Any]):
        """Deploy projects to GitHub"""
        if not projects:
            from .app_state import AppState
            app_state = await self.get_state(AppState)
            app_state.show_notification_message("No projects to deploy", "error")
            return
        
        # Check GitHub connection
        from .app_state import AppState
        app_state = await self.get_state(AppState)
        if not app_state.github_connected:
            app_state.show_notification_message("GitHub not configured", "error")
            return
        
        # Reset deployment state
        self.reset_deployment()
        
        # Initialize deployment
        self.status = "running"
        self.progress = 0
        self.start_time = datetime.now()
        
        action_text = "Testing deployment" if self.dry_run else "Deployment started"
        self.add_log('ℹ️', action_text)
        self.current_action = f'{"Testing" if self.dry_run else "Starting"} deployment...'
        
        try:
            await self.simulate_github_deployment(projects)
        except Exception as e:
            self.status = "error"
            self.end_time = datetime.now()
            error_msg = f"{'Test' if self.dry_run else 'Deployment'} failed: {str(e)}"
            self.add_error(error_msg)
            self.add_log('❌', error_msg)
            
            app_state.show_notification_message(
                f"{'Test' if self.dry_run else 'Deployment'} failed: {str(e)}", 
                "error"
            )
    
    async def simulate_github_deployment(self, projects: Dict[str, Any]):
        """Simulate GitHub API deployment process"""
        total_milestones = len(projects)
        total_issues = sum(len(m.get('issues', [])) for m in projects.values())
        total_steps = total_milestones + total_issues
        current_step = 0
        
        # Process each milestone and its issues
        for milestone_name, milestone_data in projects.items():
            current_step += 1
            progress = int((current_step / total_steps) * 100)
            
            # Update progress
            action = f"{'Testing' if self.dry_run else 'Creating'} milestone: {milestone_name}"
            self.update_progress(progress, action)
            self.add_log('🎯', action)
            
            # Simulate API delay
            await asyncio.sleep(1)
            
            # Update milestone count
            if not self.dry_run:
                self.created_milestones += 1
            
            success_msg = f"{'Would create' if self.dry_run else 'Created'} milestone: {milestone_name}"
            self.add_log('✅', success_msg)
            
            # Process issues
            for issue in milestone_data.get('issues', []):
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                
                issue_title = issue.get('title', 'Untitled Issue')
                short_title = issue_title[:40] + '...' if len(issue_title) > 40 else issue_title
                
                action = f"{'Testing' if self.dry_run else 'Creating'} issue: {short_title}"
                self.update_progress(progress, action)
                self.add_log('📋', action)
                
                # Simulate API delay
                await asyncio.sleep(1)
                
                # Update issue count
                if not self.dry_run:
                    self.created_issues += 1
                
                success_msg = f"{'Would create' if self.dry_run else 'Created'} issue: {short_title}"
                self.add_log('✅', success_msg)
        
        # Deployment completed
        self.status = "completed"
        self.progress = 100
        self.current_action = ""
        self.end_time = datetime.now()
        
        completion_msg = f"{'Test completed' if self.dry_run else 'Deployment completed'}! {'Would create' if self.dry_run else 'Created'} {self.created_milestones} milestones and {self.created_issues} issues"
        self.add_log('✅', completion_msg)
        
        # Show success notification
        from .app_state import AppState
        app_state = await self.get_state(AppState)
        app_state.show_notification_message(
            f"{'Test deployment' if self.dry_run else 'Deployment'} completed successfully!", 
            "success"
        )
    
    def get_deployment_duration(self) -> str:
        """Get deployment duration as formatted string"""
        if not self.start_time:
            return "Not started"
        
        end = self.end_time or datetime.now()
        duration = end - self.start_time
        
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_recent_logs(self, count: int = 20) -> List[DeploymentLogEntry]:
        """Get recent log entries"""
        return self.logs[-count:] if len(self.logs) > count else self.logs
    
    def get_recent_errors(self, count: int = 5) -> List[str]:
        """Get recent errors"""
        return self.errors[-count:] if len(self.errors) > count else self.errors
