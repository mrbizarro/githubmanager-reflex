"""
Repository Cleanup page - simplified version
"""

import reflex as rx
from ..components.header import header, settings_drawer, help_drawer, notification_toast
from ..components.ui import alert, section_header, loading_spinner, empty_state
from ..state.app_state import AppState

# Simple cleanup state for demo
class CleanupState(rx.State):
    loading_data: bool = False
    
    async def load_repository_data(self):
        self.loading_data = True
        import asyncio
        await asyncio.sleep(2)  # Simulate loading
        self.loading_data = False
        
        from .app_state import AppState
        app_state = await self.get_state(AppState)
        app_state.show_notification_message("Repository data loaded!", "success")

@rx.page(route="/cleanup", title="Repository Cleanup - GitHub Issues Manager")
def page() -> rx.Component:
    """Repository Cleanup page"""
    
    return rx.container(
        rx.vstack(
            # Header
            header(),
            
            # Settings and help drawers
            settings_drawer(),
            help_drawer(),
            
            # Navigation
            rx.flex(
                rx.link(
                    rx.button(
                        rx.icon("arrow-left", size=16),
                        "Back to Dashboard",
                        variant="ghost"
                    ),
                    href="/",
                    style={"text_decoration": "none"}
                ),
                justify="start",
                margin_bottom="4"
            ),
            
            # Cleanup Section
            rx.vstack(
                section_header(
                    title="🧹 Repository Cleanup",
                    description="Manage and clean up existing GitHub issues and milestones"
                ),
                
                # Load Data Section
                rx.card(
                    rx.vstack(
                        rx.heading("🔄 Load Repository Data", size="4"),
                        
                        rx.cond(
                            AppState.github_connected,
                            alert(
                                title="Ready to Load",
                                description=f"Will load data from {AppState.repo_owner}/{AppState.repo_name}",
                                type="success"
                            ),
                            alert(
                                title="GitHub Configuration Required",
                                description="Please configure GitHub settings to load repository data",
                                type="error"
                            )
                        ),
                        
                        rx.button(
                            "🔄 Load Repository Data",
                            on_click=CleanupState.load_repository_data,
                            disabled=(~AppState.github_connected) | CleanupState.loading_data,
                            size="3"
                        ),
                        
                        rx.cond(
                            CleanupState.loading_data,
                            loading_spinner("Loading repository data..."),
                            rx.text("")
                        ),
                        
                        spacing="4",
                        width="100%"
                    )
                ),
                
                # Placeholder for data
                empty_state(
                    icon="database",
                    title="No Data Loaded",
                    description="Load repository data to see issues and milestones here",
                    action_button=rx.button(
                        "Load Data",
                        on_click=CleanupState.load_repository_data,
                        disabled=~AppState.github_connected
                    )
                ),
                
                spacing="4",
                width="100%"
            ),
            
            # Notification toast
            notification_toast(),
            
            spacing="6",
            width="100%",
            min_height="100vh"
        ),
        max_width="1200px",
        padding="2rem"
    )
