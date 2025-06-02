"""
🚀 GitHub Issues Manager - Reflex Version
Clean, modern, and fast web application for managing GitHub issues and milestones
"""

import reflex as rx
from .pages import home, upload, manual, cleanup, settings
from .state.app_state import AppState

def create_app() -> rx.App:
    """Create and configure the Reflex application"""
    
    app = rx.App(
        theme=rx.theme(
            appearance="dark",
            has_background=True,
            radius="large",
            scaling="100%",
        ),
        stylesheets=[
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
        ]
    )
    
    # Add routes
    app.add_page(home.page, route="/", title="GitHub Issues Manager")
    app.add_page(upload.page, route="/upload", title="Upload & Convert")
    app.add_page(manual.page, route="/manual", title="Manual Entry")
    app.add_page(cleanup.page, route="/cleanup", title="Repository Cleanup")
    app.add_page(settings.page, route="/settings", title="Settings")
    
    return app

# Global styles
style = {
    "font_family": "Inter, sans-serif",
    "font_size": "16px",
}

app = create_app()