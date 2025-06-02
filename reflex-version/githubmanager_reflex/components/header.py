"""
Header component with navigation and settings
"""

import reflex as rx
from ..state.app_state import AppState

def header() -> rx.Component:
    """Modern header with gradient background"""
    
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.heading(
                    "🚀 GitHub Issues Manager",
                    size="8",
                    color="white",
                    weight="bold",
                    letter_spacing="-0.025em"
                ),
                rx.text(
                    "AI-powered markdown to GitHub issues converter",
                    size="4",
                    color="white",
                    opacity="0.9"
                ),
                align="center",
                spacing="2"
            ),
            rx.spacer(),
            rx.hstack(
                theme_toggle_button(),
                settings_button(),
                help_button(),
                spacing="2",
                align="center"
            ),
            direction="row",
            align="center",
            width="100%"
        ),
        background="linear-gradient(135deg, var(--accent-9) 0%, #8b5cf6 100%)",
        padding="2rem",
        border_radius="var(--radius-3)",
        margin_bottom="2rem",
        box_shadow="0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    )

def theme_toggle_button() -> rx.Component:
    """Theme toggle button"""
    
    return rx.button(
        rx.cond(
            AppState.dark_mode,
            rx.icon("moon", size=16),
            rx.icon("sun", size=16)
        ),
        on_click=AppState.toggle_theme,
        variant="ghost",
        color_scheme="gray",
        size="2"
    )

def settings_button() -> rx.Component:
    """Settings button"""
    
    return rx.button(
        rx.icon("settings", size=16),
        "Settings",
        on_click=AppState.toggle_settings,
        variant="ghost",
        color_scheme="gray",
        size="2"
    )

def help_button() -> rx.Component:
    """Help button"""
    
    return rx.button(
        rx.icon("help-circle", size=16),
        "Help",
        on_click=AppState.toggle_help,
        variant="ghost",
        color_scheme="gray",
        size="2"
    )

def navigation_tabs() -> rx.Component:
    """Navigation tabs for different pages"""
    
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("🏠 Dashboard", value="home"),
            rx.tabs.trigger("📁 Upload & Convert", value="upload"),
            rx.tabs.trigger("✍️ Manual Entry", value="manual"),
            rx.tabs.trigger("🧹 Cleanup", value="cleanup"),
            default_value="home",
            size="2"
        ),
        margin_bottom="2rem"
    )

def status_indicators() -> rx.Component:
    """Status indicators for GitHub and AI connections"""
    
    return rx.flex(
        # GitHub status
        rx.card(
            rx.flex(
                rx.flex(
                    rx.icon("github", size=18),
                    rx.vstack(
                        rx.text("GitHub", weight="medium", size="2"),
                        rx.text(
                            rx.cond(
                                AppState.github_connected,
                                f"{AppState.repo_owner}/{AppState.repo_name}",
                                "Not configured"
                            ),
                            size="1",
                            color="gray"
                        ),
                        spacing="0",
                        align="start"
                    ),
                    align="center",
                    spacing="3"
                ),
                rx.badge(
                    rx.cond(
                        AppState.github_connected,
                        "Connected",
                        "Disconnected"
                    ),
                    color_scheme=rx.cond(
                        AppState.github_connected,
                        "green",
                        "red"
                    ),
                    variant="soft"
                ),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.flex(
                rx.button(
                    "Test Connection",
                    on_click=AppState.test_github_connection,
                    disabled=~AppState.github_connected,
                    size="1",
                    variant="outline"
                ),
                justify="end",
                margin_top="2"
            ),
            width="100%"
        ),
        
        # AI status
        rx.card(
            rx.flex(
                rx.flex(
                    rx.icon("brain", size=18),
                    rx.vstack(
                        rx.text("DeepSeek AI", weight="medium", size="2"),
                        rx.text(
                            rx.cond(
                                AppState.ai_connected,
                                "API configured",
                                "Not configured"
                            ),
                            size="1",
                            color="gray"
                        ),
                        spacing="0",
                        align="start"
                    ),
                    align="center",
                    spacing="3"
                ),
                rx.badge(
                    rx.cond(
                        AppState.ai_connected,
                        "Connected",
                        "Disconnected"
                    ),
                    color_scheme=rx.cond(
                        AppState.ai_connected,
                        "green",
                        "red"
                    ),
                    variant="soft"
                ),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.flex(
                rx.button(
                    "Test Connection",
                    on_click=AppState.test_ai_connection,
                    disabled=~AppState.ai_connected,
                    size="1",
                    variant="outline"
                ),
                justify="end",
                margin_top="2"
            ),
            width="100%"
        ),
        
        gap="4",
        direction="row",
        wrap="wrap"
    )

def settings_drawer() -> rx.Component:
    """Settings configuration drawer"""
    
    return rx.cond(
        AppState.show_settings,
        rx.card(
            rx.vstack(
                rx.heading("⚙️ Configuration Settings", size="5"),
                
                rx.flex(
                    # GitHub configuration
                    rx.vstack(
                        rx.heading("GitHub Configuration", size="3"),
                        
                        rx.vstack(
                            rx.text("GitHub Token", size="2", weight="medium"),
                            rx.input(
                                placeholder="Enter GitHub personal access token",
                                type="password",
                                value=AppState.github_token,
                                on_change=lambda v: AppState.update_github_config(v, AppState.repo_owner, AppState.repo_name)
                            )
                        ),
                        
                        rx.vstack(
                            rx.text("Repository Owner", size="2", weight="medium"),
                            rx.input(
                                placeholder="GitHub username or organization",
                                value=AppState.repo_owner,
                                on_change=lambda v: AppState.update_github_config(AppState.github_token, v, AppState.repo_name)
                            )
                        ),
                        
                        rx.vstack(
                            rx.text("Repository Name", size="2", weight="medium"),
                            rx.input(
                                placeholder="Repository name",
                                value=AppState.repo_name,
                                on_change=lambda v: AppState.update_github_config(AppState.github_token, AppState.repo_owner, v)
                            )
                        ),
                        
                        spacing="3",
                        align="start",
                        width="100%"
                    ),
                    
                    # AI configuration
                    rx.vstack(
                        rx.heading("AI Configuration", size="3"),
                        
                        rx.vstack(
                            rx.text("DeepSeek API Key", size="2", weight="medium"),
                            rx.input(
                                placeholder="Enter DeepSeek API key",
                                type="password",
                                value=AppState.deepseek_api_key,
                                on_change=AppState.update_ai_config
                            )
                        ),
                        
                        rx.vstack(
                            rx.text("Theme", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(
                                    rx.select.value(
                                        placeholder="Select theme",
                                        default_value=rx.cond(AppState.dark_mode, "dark", "light")
                                    )
                                ),
                                rx.select.content(
                                    rx.select.item("Light", value="light"),
                                    rx.select.item("Dark", value="dark"),
                                    rx.select.item("Auto", value="auto")
                                ),
                                on_value_change=lambda v: setattr(AppState, 'dark_mode', v == "dark")
                            )
                        ),
                        
                        spacing="3",
                        align="start",
                        width="100%"
                    ),
                    
                    gap="6",
                    direction="row",
                    wrap="wrap"
                ),
                
                # Action buttons
                rx.flex(
                    rx.button(
                        "Cancel",
                        on_click=AppState.toggle_settings,
                        variant="outline",
                        color_scheme="gray"
                    ),
                    rx.button(
                        "💾 Save Settings",
                        on_click=AppState.save_settings,
                        color_scheme="blue"
                    ),
                    gap="3",
                    justify="end"
                ),
                
                spacing="4",
                align="start",
                width="100%"
            ),
            margin_top="4"
        )
    )

def help_drawer() -> rx.Component:
    """Help and documentation drawer"""
    
    return rx.cond(
        AppState.show_help,
        rx.card(
            rx.vstack(
                rx.heading("❓ Help & Documentation", size="5"),
                
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Quick Start", value="quickstart"),
                        rx.tabs.trigger("Features", value="features"),
                        rx.tabs.trigger("Troubleshooting", value="troubleshooting")
                    ),
                    
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("🚀 Quick Start Guide", size="4"),
                            rx.text("1. Configure Settings: Click the ⚙️ Settings button and enter your GitHub token and repository details"),
                            rx.text("2. Upload Files: Go to Upload & Convert and drag your markdown files"),
                            rx.text("3. Process: Click 'Process Files' to convert markdown to issues and milestones"),
                            rx.text("4. Review: Edit the generated content as needed"),
                            rx.text("5. Deploy: Click 'Deploy' to create issues in your GitHub repository"),
                            spacing="2",
                            align="start"
                        ),
                        value="quickstart"
                    ),
                    
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("✨ Features Overview", size="4"),
                            rx.text("• 🤖 AI-Powered Parsing: Intelligent conversion of natural markdown"),
                            rx.text("• 📊 Real-time Metrics: Track progress and statistics"),
                            rx.text("• ✏️ Live Editing: Modify content before deployment"),
                            rx.text("• 🗑️ Repository Cleanup: Manage existing issues and milestones"),
                            rx.text("• 🎯 Smart Labels: Automatic label creation and management"),
                            rx.text("• 📋 Manual Entry: Create issues and milestones manually"),
                            spacing="2",
                            align="start"
                        ),
                        value="features"
                    ),
                    
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("🔧 Troubleshooting", size="4"),
                            rx.text("AI Not Working? Check DeepSeek API key in settings, verify internet connection"),
                            rx.text("GitHub Errors? Verify token has repo scope, check repository owner/name spelling"),
                            rx.text("Processing Issues? Check markdown file encoding (UTF-8), try both AI and standard modes"),
                            spacing="2",
                            align="start"
                        ),
                        value="troubleshooting"
                    ),
                    
                    default_value="quickstart"
                ),
                
                rx.button(
                    "Close Help",
                    on_click=AppState.toggle_help,
                    variant="outline",
                    align_self="end"
                ),
                
                spacing="4",
                align="start",
                width="100%"
            ),
            margin_top="4"
        )
    )

def notification_toast() -> rx.Component:
    """Notification toast component"""
    
    return rx.cond(
        AppState.show_notification,
        rx.callout.root(
            rx.callout.icon(
                rx.cond(
                    AppState.notification_type == "success",
                    rx.icon("check-circle"),
                    rx.cond(
                        AppState.notification_type == "error",
                        rx.icon("x-circle"),
                        rx.cond(
                            AppState.notification_type == "warning",
                            rx.icon("alert-triangle"),
                            rx.icon("info")
                        )
                    )
                )
            ),
            rx.callout.text(AppState.notification_message),
            rx.icon_button(
                rx.icon("x", size=14),
                on_click=AppState.hide_notification,
                size="1",
                variant="ghost"
            ),
            color_scheme=rx.cond(
                AppState.notification_type == "success",
                "green",
                rx.cond(
                    AppState.notification_type == "error",
                    "red",
                    rx.cond(
                        AppState.notification_type == "warning",
                        "orange",
                        "blue"
                    )
                )
            ),
            position="fixed",
            top="1rem",
            right="1rem",
            z_index="1000",
            max_width="400px"
        )
    )
