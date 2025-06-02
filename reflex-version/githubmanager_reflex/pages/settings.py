"""
Settings page - comprehensive configuration management
"""

import reflex as rx
from ..components.header import header, notification_toast
from ..components.ui import alert, section_header, labeled_input, status_badge, card_grid, metric_card
from ..state.app_state import AppState

@rx.page(route="/settings", title="Settings - GitHub Issues Manager")
def page() -> rx.Component:
    """Settings page"""
    
    return rx.container(
        rx.vstack(
            # Header
            header(),
            
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
            
            # Configuration Status Overview
            rx.card(
                rx.vstack(
                    rx.heading("🚀 Configuration Status", size="4"),
                    
                    card_grid([
                        rx.card(
                            rx.vstack(
                                rx.flex(
                                    rx.icon("github", size=20),
                                    rx.text("GitHub", weight="medium", size="2"),
                                    align="center",
                                    gap="2"
                                ),
                                status_badge(
                                    rx.cond(AppState.github_connected, "Configured", "Not Configured"),
                                    rx.cond(AppState.github_connected, "green", "red")
                                ),
                                rx.text(
                                    rx.cond(
                                        AppState.github_connected,
                                        f"{AppState.repo_owner}/{AppState.repo_name}",
                                        "API access required"
                                    ),
                                    size="1",
                                    color="gray",
                                    text_align="center"
                                ),
                                spacing="2",
                                align="center",
                                width="100%"
                            )
                        ),
                        
                        rx.card(
                            rx.vstack(
                                rx.flex(
                                    rx.icon("brain", size=20),
                                    rx.text("AI Service", weight="medium", size="2"),
                                    align="center",
                                    gap="2"
                                ),
                                status_badge(
                                    rx.cond(AppState.ai_connected, "Enabled", "Disabled"),
                                    rx.cond(AppState.ai_connected, "green", "gray")
                                ),
                                rx.text(
                                    rx.cond(
                                        AppState.ai_connected,
                                        "DeepSeek connected",
                                        "Standard parsing only"
                                    ),
                                    size="1",
                                    color="gray",
                                    text_align="center"
                                ),
                                spacing="2",
                                align="center",
                                width="100%"
                            )
                        ),
                        
                        rx.card(
                            rx.vstack(
                                rx.flex(
                                    rx.icon("check-circle", size=20),
                                    rx.text("App Status", weight="medium", size="2"),
                                    align="center",
                                    gap="2"
                                ),
                                status_badge(
                                    rx.cond(
                                        AppState.github_connected,
                                        "Ready",
                                        "Setup Required"
                                    ),
                                    rx.cond(
                                        AppState.github_connected,
                                        "green",
                                        "orange"
                                    )
                                ),
                                rx.text(
                                    rx.cond(
                                        AppState.github_connected,
                                        "All features available",
                                        "Configuration needed"
                                    ),
                                    size="1",
                                    color="gray",
                                    text_align="center"
                                ),
                                spacing="2",
                                align="center",
                                width="100%"
                            )
                        )
                    ], columns=3),
                    
                    spacing="4",
                    width="100%"
                )
            ),
            
            # GitHub Settings
            rx.vstack(
                section_header(
                    title="🐙 GitHub Configuration",
                    description="Configure your GitHub API access and repository settings"
                ),
                
                rx.card(
                    rx.vstack(
                        # Connection status
                        rx.flex(
                            rx.text("Connection Status", weight="medium", size="3"),
                            rx.flex(
                                status_badge(
                                    rx.cond(AppState.github_connected, "Connected", "Disconnected"),
                                    rx.cond(AppState.github_connected, "green", "red")
                                ),
                                rx.cond(
                                    AppState.github_connected,
                                    rx.button(
                                        "Test Connection",
                                        on_click=AppState.test_github_connection,
                                        variant="outline",
                                        size="1"
                                    ),
                                    rx.text("")
                                ),
                                gap="2"
                            ),
                            justify="between",
                            align="center",
                            width="100%"
                        ),
                        
                        # Configuration form
                        labeled_input(
                            label="GitHub Personal Access Token",
                            placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                            value=AppState.github_token,
                            on_change=lambda v: setattr(AppState, 'github_token', v),
                            type="password",
                            required=True,
                            help_text="Generate a token at https://github.com/settings/tokens with 'repo' scope"
                        ),
                        
                        rx.grid(
                            labeled_input(
                                label="Repository Owner",
                                placeholder="your-username-or-org",
                                value=AppState.repo_owner,
                                on_change=lambda v: setattr(AppState, 'repo_owner', v),
                                required=True,
                                help_text="GitHub username or organization name"
                            ),
                            
                            labeled_input(
                                label="Repository Name",
                                placeholder="your-repository-name",
                                value=AppState.repo_name,
                                on_change=lambda v: setattr(AppState, 'repo_name', v),
                                required=True,
                                help_text="Name of the target repository"
                            ),
                            
                            columns="2",
                            gap="4"
                        ),
                        
                        spacing="4",
                        width="100%"
                    )
                ),
                
                spacing="4",
                width="100%"
            ),
            
            # AI Settings
            rx.vstack(
                section_header(
                    title="🤖 AI Configuration",
                    description="Configure DeepSeek AI for intelligent markdown parsing"
                ),
                
                rx.card(
                    rx.vstack(
                        # Connection status
                        rx.flex(
                            rx.text("AI Service Status", weight="medium", size="3"),
                            rx.flex(
                                status_badge(
                                    rx.cond(AppState.ai_connected, "Connected", "Disconnected"),
                                    rx.cond(AppState.ai_connected, "green", "red")
                                ),
                                rx.cond(
                                    AppState.ai_connected,
                                    rx.button(
                                        "Test Connection",
                                        on_click=AppState.test_ai_connection,
                                        variant="outline",
                                        size="1"
                                    ),
                                    rx.text("")
                                ),
                                gap="2"
                            ),
                            justify="between",
                            align="center",
                            width="100%"
                        ),
                        
                        # Configuration form
                        labeled_input(
                            label="DeepSeek API Key",
                            placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                            value=AppState.deepseek_api_key,
                            on_change=lambda v: setattr(AppState, 'deepseek_api_key', v),
                            type="password",
                            required=False,
                            help_text="Get your API key from https://platform.deepseek.com/"
                        ),
                        
                        spacing="4",
                        width="100%"
                    )
                ),
                
                spacing="4",
                width="100%"
            ),
            
            # App Settings
            rx.vstack(
                section_header(
                    title="⚙️ Application Settings",
                    description="Customize your application experience"
                ),
                
                rx.card(
                    rx.vstack(
                        # Theme settings
                        rx.vstack(
                            rx.text("Theme Preferences", weight="medium", size="2"),
                            rx.flex(
                                rx.switch(
                                    checked=AppState.dark_mode,
                                    on_change=lambda v: setattr(AppState, 'dark_mode', v)
                                ),
                                rx.vstack(
                                    rx.text("Dark Mode", weight="medium", size="2"),
                                    rx.text("Use dark theme for better readability", size="1", color="gray"),
                                    spacing="0",
                                    align="start"
                                ),
                                align="center",
                                gap="3"
                            ),
                            spacing="2",
                            align="start",
                            width="100%"
                        ),
                        
                        rx.separator(),
                        
                        # Application info
                        rx.vstack(
                            rx.text("Application Information", weight="medium", size="2"),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Version", size="1", color="gray"),
                                    rx.text(AppState.version, size="2"),
                                    spacing="0",
                                    align="start"
                                ),
                                rx.vstack(
                                    rx.text("Framework", size="1", color="gray"),
                                    rx.text("Reflex", size="2"),
                                    spacing="0",
                                    align="start"
                                ),
                                rx.vstack(
                                    rx.text("Environment", size="1", color="gray"),
                                    rx.text("Production", size="2"),
                                    spacing="0",
                                    align="start"
                                ),
                                columns="3",
                                gap="4"
                            ),
                            spacing="2",
                            align="start",
                            width="100%"
                        ),
                        
                        spacing="4",
                        width="100%"
                    )
                ),
                
                spacing="4",
                width="100%"
            ),
            
            # Save Settings
            rx.separator(),
            
            rx.card(
                rx.vstack(
                    rx.text("💾 Save Configuration", weight="medium", size="3"),
                    rx.text("Save your settings to .env file for persistence", size="2", color="gray"),
                    
                    rx.flex(
                        rx.button(
                            "Reset to Defaults",
                            variant="outline",
                            color_scheme="gray"
                        ),
                        
                        rx.button(
                            "💾 Save Settings",
                            on_click=AppState.save_settings,
                            size="3",
                            disabled=(~AppState.github_token.strip()) | (~AppState.repo_owner.strip()) | (~AppState.repo_name.strip())
                        ),
                        
                        gap="3",
                        justify="end",
                        width="100%"
                    ),
                    
                    spacing="3",
                    width="100%"
                ),
                background="var(--accent-2)",
                border="1px solid var(--accent-6)"
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
