"""
Home/Dashboard page - main landing page with overview and quick actions
"""

import reflex as rx
from ..components.header import header, status_indicators, settings_drawer, help_drawer, notification_toast
from ..components.ui import metric_card, alert, section_header, empty_state, card_grid
from ..state.app_state import AppState
from ..state.file_state import FileState
from ..state.manual_state import ManualState
from ..state.deployment_state import DeploymentState

def quick_stats() -> rx.Component:
    """Quick statistics overview"""
    
    return rx.vstack(
        section_header(
            title="📊 Quick Overview",
            description="Summary of your current projects and activities"
        ),
        
        card_grid([
            metric_card(
                title="Processed Projects",
                value=rx.cond(
                    FileState.processed_projects,
                    len(FileState.processed_projects),
                    0
                ),
                icon="folder",
                description="From uploaded files"
            ),
            
            metric_card(
                title="Manual Entries", 
                value=len(ManualState.manual_milestones),
                icon="edit",
                description="Created manually"
            ),
            
            metric_card(
                title="Last Deployment",
                value=rx.cond(
                    DeploymentState.status == "completed",
                    f"{DeploymentState.created_milestones + DeploymentState.created_issues} items",
                    "None"
                ),
                icon="rocket",
                description=rx.cond(
                    DeploymentState.status == "completed",
                    "Successful",
                    "No deployments yet"
                )
            )
        ], columns=3),
        
        spacing="4",
        width="100%"
    )

def recent_activity() -> rx.Component:
    """Recent activity feed"""
    
    return rx.vstack(
        section_header(
            title="🕐 Recent Activity",
            description="Latest actions and updates"
        ),
        
        rx.cond(
            DeploymentState.logs,
            rx.card(
                rx.vstack(
                    *[
                        rx.flex(
                            rx.text(log.icon, size="3"),
                            rx.flex(
                                rx.text(log.message, size="2"),
                                rx.text(log.timestamp, size="1", color="gray"),
                                direction="column",
                                align="start",
                                flex="1"
                            ),
                            align="center",
                            gap="3",
                            width="100%"
                        )
                        for log in DeploymentState.get_recent_logs(5)
                    ],
                    spacing="3",
                    width="100%"
                )
            ),
            empty_state(
                icon="activity",
                title="No Recent Activity",
                description="Start by uploading files or creating manual entries"
            )
        ),
        
        spacing="4",
        width="100%"
    )

def quick_actions() -> rx.Component:
    """Quick action buttons"""
    
    return rx.vstack(
        section_header(
            title="⚡ Quick Actions",
            description="Jump to common tasks"
        ),
        
        rx.grid(
            # Upload & Convert
            rx.card(
                rx.vstack(
                    rx.icon("upload", size=32, color="var(--accent-9)"),
                    rx.heading("Upload & Convert", size="4"),
                    rx.text(
                        "Upload markdown files and convert them to GitHub issues",
                        size="2",
                        color="gray",
                        text_align="center"
                    ),
                    rx.button(
                        "Get Started",
                        on_click=rx.redirect("/upload"),
                        size="2",
                        width="100%"
                    ),
                    spacing="3",
                    align="center",
                    height="100%"
                ),
                padding="4",
                cursor="pointer",
                _hover={"box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"},
                on_click=rx.redirect("/upload")
            ),
            
            # Manual Entry
            rx.card(
                rx.vstack(
                    rx.icon("edit", size=32, color="var(--accent-9)"),
                    rx.heading("Manual Entry", size="4"),
                    rx.text(
                        "Create milestones and issues manually with full control",
                        size="2",
                        color="gray",
                        text_align="center"
                    ),
                    rx.button(
                        "Create Manually",
                        on_click=rx.redirect("/manual"),
                        size="2",
                        width="100%",
                        variant="outline"
                    ),
                    spacing="3",
                    align="center",
                    height="100%"
                ),
                padding="4",
                cursor="pointer",
                _hover={"box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"},
                on_click=rx.redirect("/manual")
            ),
            
            # Repository Cleanup
            rx.card(
                rx.vstack(
                    rx.icon("trash-2", size=32, color="var(--accent-9)"),
                    rx.heading("Repository Cleanup", size="4"),
                    rx.text(
                        "Manage and clean up existing repository issues",
                        size="2",
                        color="gray",
                        text_align="center"
                    ),
                    rx.button(
                        "Manage Repo",
                        on_click=rx.redirect("/cleanup"),
                        size="2",
                        width="100%",
                        variant="outline"
                    ),
                    spacing="3",
                    align="center",
                    height="100%"
                ),
                padding="4",
                cursor="pointer",
                _hover={"box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"},
                on_click=rx.redirect("/cleanup")
            ),
            
            columns="3",
            gap="4",
            width="100%"
        ),
        
        spacing="4",
        width="100%"
    )

def configuration_status() -> rx.Component:
    """Configuration status and setup prompts"""
    
    return rx.cond(
        AppState.github_connected,
        # Configuration complete
        rx.vstack(
            alert(
                title="✅ Configuration Complete",
                description=f"Connected to {AppState.repo_owner}/{AppState.repo_name}. All features are available.",
                type="success"
            ),
            spacing="2"
        ),
        # Configuration needed
        rx.vstack(
            alert(
                title="⚙️ Setup Required",
                description="Configure your GitHub settings to get started with all features.",
                type="info"
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("🚀 Getting Started", size="4"),
                    rx.text(
                        "Welcome! To use all features of GitHub Issues Manager, you'll need to configure your GitHub API access.",
                        size="2",
                        color="gray"
                    ),
                    
                    rx.vstack(
                        rx.text("1. Click the Settings button above", size="2"),
                        rx.text("2. Enter your GitHub personal access token", size="2"),
                        rx.text("3. Set your repository owner and name", size="2"),
                        rx.text("4. Optionally add DeepSeek API key for AI features", size="2"),
                        rx.text("5. Save settings and start creating!", size="2"),
                        spacing="1",
                        align="start"
                    ),
                    
                    rx.flex(
                        rx.button(
                            "⚙️ Open Settings",
                            on_click=AppState.toggle_settings,
                            size="2"
                        ),
                        rx.button(
                            "👀 Try Demo Mode",
                            on_click=lambda: None,  # Could add demo mode
                            variant="outline",
                            size="2"
                        ),
                        gap="3"
                    ),
                    
                    spacing="4",
                    align="start"
                )
            ),
            
            spacing="4"
        )
    )

def navigation_bar() -> rx.Component:
    """Navigation bar with page links"""
    
    return rx.flex(
        rx.link(
            rx.button(
                rx.icon("home", size=16),
                "Dashboard",
                variant="ghost",
                color_scheme="gray"
            ),
            href="/",
            style={"text_decoration": "none"}
        ),
        rx.link(
            rx.button(
                rx.icon("upload", size=16),
                "Upload & Convert",
                variant="ghost",
                color_scheme="gray"
            ),
            href="/upload",
            style={"text_decoration": "none"}
        ),
        rx.link(
            rx.button(
                rx.icon("edit", size=16),
                "Manual Entry",
                variant="ghost",
                color_scheme="gray"
            ),
            href="/manual",
            style={"text_decoration": "none"}
        ),
        rx.link(
            rx.button(
                rx.icon("trash-2", size=16),
                "Cleanup",
                variant="ghost",
                color_scheme="gray"
            ),
            href="/cleanup",
            style={"text_decoration": "none"}
        ),
        rx.link(
            rx.button(
                rx.icon("settings", size=16),
                "Settings",
                variant="ghost",
                color_scheme="gray"
            ),
            href="/settings",
            style={"text_decoration": "none"}
        ),
        gap="2",
        padding="2",
        border_bottom="1px solid var(--gray-6)",
        margin_bottom="4"
    )

@rx.page(route="/", title="GitHub Issues Manager - Dashboard")
def page() -> rx.Component:
    """Home/Dashboard page"""
    
    return rx.container(
        rx.vstack(
            # Header
            header(),
            
            # Settings and help drawers
            settings_drawer(),
            help_drawer(),
            
            # Navigation
            navigation_bar(),
            
            # Status indicators
            status_indicators(),
            
            # Configuration status
            configuration_status(),
            
            # Main content
            rx.cond(
                AppState.github_connected | (len(FileState.processed_projects) > 0) | (len(ManualState.manual_milestones) > 0),
                # Show dashboard when configured or has data
                rx.vstack(
                    quick_stats(),
                    recent_activity(),
                    quick_actions(),
                    spacing="6"
                ),
                # Show getting started when not configured
                rx.vstack(
                    quick_actions(),
                    spacing="6"
                )
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
