"""
Upload & Convert page - simplified version
"""

import reflex as rx
from ..components.header import header, settings_drawer, help_drawer, notification_toast
from ..components.ui import alert, section_header, status_badge, labeled_input
from ..state.app_state import AppState
from ..state.file_state import FileState

@rx.page(route="/upload", title="Upload & Convert - GitHub Issues Manager")
def page() -> rx.Component:
    """Upload & Convert page"""
    
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
            
            # Upload Section
            rx.vstack(
                section_header(
                    title="📁 Upload & Convert Markdown",
                    description="Upload markdown files to convert them to GitHub issues and milestones"
                ),
                
                # AI mode toggle
                rx.flex(
                    rx.switch(
                        checked=FileState.ai_enabled,
                        on_change=FileState.set_ai_mode,
                        disabled=~AppState.ai_connected
                    ),
                    rx.text("🤖 AI Parsing Mode", weight="medium"),
                    status_badge(
                        rx.cond(
                            FileState.ai_enabled & AppState.ai_connected,
                            "AI Mode",
                            "Standard Mode"
                        )
                    ),
                    justify="between",
                    align="center",
                    width="100%"
                ),
                
                # File upload area
                rx.card(
                    rx.vstack(
                        rx.icon("upload", size=48, color="var(--gray-9)"),
                        rx.heading("Drop files here or click to browse", size="4"),
                        rx.text("Supported: .md, .markdown, .txt"),
                        rx.button(
                            "Select Files",
                            on_click=FileState.handle_file_upload,
                            size="3"
                        ),
                        spacing="3",
                        align="center"
                    ),
                    border="2px dashed var(--gray-7)",
                    padding="3rem",
                    text_align="center"
                ),
                
                # Process button
                rx.button(
                    "🚀 Process Files",
                    on_click=FileState.process_files,
                    disabled=FileState.processing_status == "processing",
                    size="3",
                    width="100%"
                ),
                
                # Processing status
                rx.cond(
                    FileState.processing_status == "processing",
                    rx.card(
                        rx.vstack(
                            status_badge(FileState.processing_status),
                            rx.text(FileState.processing_message),
                            rx.progress(
                                value=FileState.processing_progress,
                                size="2"
                            ),
                            spacing="3",
                            width="100%"
                        )
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
