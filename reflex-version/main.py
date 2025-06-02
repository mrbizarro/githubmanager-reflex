"""
🚀 GitHub Issues Manager - Reflex Version
Main application entry point
"""

import reflex as rx
from githubmanager_reflex.pages import home, upload, manual, cleanup, settings
from githubmanager_reflex.state.app_state import AppState

# Configure the app
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

# Add pages
app.add_page(home.page, route="/")
app.add_page(upload.page, route="/upload")
app.add_page(manual.page, route="/manual")
app.add_page(cleanup.page, route="/cleanup")
app.add_page(settings.page, route="/settings")

# Run the app
if __name__ == "__main__":
    app.run()
