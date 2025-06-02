"""
File processing and upload state management
"""

import reflex as rx
from typing import List, Dict, Any, Optional
import json
import time
import asyncio
from datetime import datetime

class FileState(rx.State):
    """State for file upload and processing"""
    
    # Upload state
    uploaded_files: List[Dict[str, Any]] = []
    ai_enabled: bool = True
    upload_mode: str = "single"  # single, batch
    
    # Processing state
    processing_status: str = "idle"  # idle, processing, completed, error
    processing_progress: int = 0
    processing_message: str = ""
    
    # Results
    processed_projects: Dict[str, Any] = {}
    
    # UI state
    show_summary: bool = False
    view_mode: str = "compact"  # compact, detailed
    
    def clear_files(self):
        """Clear uploaded files and reset state"""
        self.uploaded_files = []
        self.processed_projects = {}
        self.processing_status = "idle"
        self.processing_progress = 0
        self.processing_message = ""
        self.show_summary = False
    
    def set_ai_mode(self, enabled: bool):
        """Set AI processing mode"""
        self.ai_enabled = enabled
    
    def set_upload_mode(self, mode: str):
        """Set upload mode (single/batch)"""
        self.upload_mode = mode
    
    def toggle_summary(self):
        """Toggle summary view"""
        self.show_summary = not self.show_summary
    
    def set_view_mode(self, mode: str):
        """Set preview view mode"""
        self.view_mode = mode
    
    async def handle_file_upload(self, files: List[Dict[str, Any]]):
        """Handle file upload from frontend"""
        self.uploaded_files = files
        
        # Basic validation
        if not files:
            return
        
        # Update UI
        file_count = len(files)
        total_size = sum(len(f.get('content', '').encode()) for f in files) / 1024
        
        # Show file info notification
        from .app_state import AppState
        app_state = await self.get_state(AppState)
        app_state.show_notification_message(
            f"{file_count} file(s) uploaded, {total_size:.1f} KB total", 
            "info"
        )
    
    async def process_files(self):
        """Process uploaded markdown files"""
        if not self.uploaded_files:
            from .app_state import AppState
            app_state = await self.get_state(AppState)
            app_state.show_notification_message("No files to process", "error")
            return
        
        # Start processing
        self.processing_status = "processing"
        self.processing_progress = 0
        self.processing_message = "Starting file processing..."
        
        try:
            all_projects = {}
            total_files = len(self.uploaded_files)
            
            for i, file_data in enumerate(self.uploaded_files):
                # Update progress
                progress = int((i / total_files) * 100)
                self.processing_progress = progress
                self.processing_message = f"Processing {file_data.get('name', 'file')}..."
                
                # Process file content
                content = file_data.get('content', '')
                filename = file_data.get('name', 'unknown.md')
                
                # Use AI or standard parsing
                from .app_state import AppState
                app_state = await self.get_state(AppState)
                
                if self.ai_enabled and app_state.ai_connected:
                    parsed_project = await self.ai_parse_content(content, filename)
                else:
                    parsed_project = self.standard_parse_content(content, filename)
                
                if parsed_project:
                    # Add file prefix for multiple files
                    if total_files > 1:
                        file_prefix = filename.replace('.md', '').replace('.markdown', '').replace('.txt', '')
                        prefixed_project = {
                            f"[{file_prefix}] {name}": data 
                            for name, data in parsed_project.items()
                        }
                        all_projects.update(prefixed_project)
                    else:
                        all_projects.update(parsed_project)
                
                # Simulate processing delay
                await asyncio.sleep(0.5)
            
            # Complete processing
            self.processing_status = "completed"
            self.processing_progress = 100
            self.processing_message = "Processing completed successfully!"
            self.processed_projects = all_projects
            
            # Show success notification
            app_state.show_notification_message(
                f"Processed {total_files} files successfully!", 
                "success"
            )
            
        except Exception as e:
            self.processing_status = "error"
            self.processing_message = f"Processing failed: {str(e)}"
            
            # Show error notification
            from .app_state import AppState
            app_state = await self.get_state(AppState)
            app_state.show_notification_message(f"Processing failed: {str(e)}", "error")
    
    async def ai_parse_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse content using AI (simulated for now)"""
        # This would integrate with actual DeepSeek API
        # For now, return a mock structure
        
        await asyncio.sleep(1)  # Simulate API call
        
        mock_project = {
            f"AI Parsed Project from {filename}": {
                'description': 'Intelligently parsed project structure using AI',
                'issues': [
                    {
                        'title': 'Setup project foundation',
                        'body': 'Initialize project structure and dependencies',
                        'labels': ['setup', 'foundation'],
                        'assignees': []
                    },
                    {
                        'title': 'Implement core features',
                        'body': 'Build the main functionality based on requirements',
                        'labels': ['feature', 'core'],
                        'assignees': []
                    },
                    {
                        'title': 'Add documentation',
                        'body': 'Create comprehensive documentation for users and developers',
                        'labels': ['documentation'],
                        'assignees': []
                    }
                ]
            }
        }
        
        return mock_project
    
    def standard_parse_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse content using standard regex patterns"""
        # This would implement actual regex parsing
        # For now, return a mock structure
        
        mock_project = {
            f"Standard Parsed Project from {filename}": {
                'description': 'Parsed using traditional regex patterns',
                'issues': [
                    {
                        'title': 'Standard issue 1',
                        'body': 'First issue from standard parsing',
                        'labels': ['standard', 'parsed'],
                        'assignees': []
                    },
                    {
                        'title': 'Standard issue 2',
                        'body': 'Second issue from standard parsing',
                        'labels': ['standard', 'feature'],
                        'assignees': []
                    }
                ]
            }
        }
        
        return mock_project
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary statistics of processed projects"""
        if not self.processed_projects:
            return {
                'total_milestones': 0,
                'total_issues': 0,
                'avg_issues_per_milestone': 0,
                'parsing_mode': 'AI' if self.ai_enabled else 'Standard'
            }
        
        total_milestones = len(self.processed_projects)
        total_issues = sum(len(m.get('issues', [])) for m in self.processed_projects.values())
        avg_issues = round(total_issues / total_milestones, 1) if total_milestones > 0 else 0
        
        return {
            'total_milestones': total_milestones,
            'total_issues': total_issues,
            'avg_issues_per_milestone': avg_issues,
            'parsing_mode': 'AI' if self.ai_enabled else 'Standard'
        }
    
    def update_project(self, milestone_name: str, milestone_data: Dict[str, Any]):
        """Update a specific project/milestone"""
        if milestone_name in self.processed_projects:
            self.processed_projects[milestone_name] = milestone_data
    
    def delete_project(self, milestone_name: str):
        """Delete a specific project/milestone"""
        if milestone_name in self.processed_projects:
            del self.processed_projects[milestone_name]
    
    def get_export_data(self) -> str:
        """Get processed projects as JSON for export"""
        return json.dumps(self.processed_projects, indent=2)
