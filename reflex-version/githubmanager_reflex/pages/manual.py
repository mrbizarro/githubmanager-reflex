"""
Manual Entry page - simplified version
"""

import reflex as rx
from ..components.header import header, settings_drawer, help_drawer, notification_toast
from ..components.ui import alert, section_header, labeled_input, labeled_textarea
from ..state.app_state import AppState
from ..state.manual_state import ManualState

@rx.page(route="/manual", title="Manual Entry - GitHub Issues Manager")
def page() -> rx.Component:
    """Manual Entry page"""
    
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
            
            # Manual Entry Section
            rx.vstack(
                section_header(
                    title="✍️ Manual Entry",
                    description="Create milestones and issues manually for precise control"
                ),
                
                # Create Milestone
                rx.card(
                    rx.vstack(
                        rx.heading("➕ Create New Milestone", size="4"),
                        
                        labeled_input(
                            label="Milestone Title",
                            placeholder="Enter milestone name",
                            value=ManualState.new_milestone_title,
                            on_change=lambda v: setattr(ManualState, 'new_milestone_title', v),
                            required=True
                        ),
                        
                        labeled_textarea(
                            label="Milestone Description",
                            placeholder="Describe the goals and scope",
                            value=ManualState.new_milestone_desc,
                            on_change=lambda v: setattr(ManualState, 'new_milestone_desc', v)
                        ),
                        
                        rx.button(
                            "➕ Add Milestone",
                            on_click=ManualState.add_milestone,
                            disabled=~ManualState.new_milestone_title.strip(),
                            size="3"
                        ),
                        
                        spacing="4",
                        width="100%"
                    )
                ),
                
                # Add Issue (if milestones exist)
                rx.cond(
                    ManualState.manual_milestones,
                    rx.card(
                        rx.vstack(
                            rx.heading("📋 Add Issue", size="4"),
                            
                            rx.select.root(
                                rx.select.trigger(
                                    rx.select.value(placeholder="Choose milestone")
                                ),
                                rx.select.content(
                                    *[
                                        rx.select.item(name, value=name)
                                        for name in ManualState.get_milestone_options()
                                    ]
                                ),
                                on_value_change=lambda v: setattr(ManualState, 'selected_milestone', v)
                            ),
                            
                            labeled_input(
                                label="Issue Title",
                                placeholder="Enter issue title",
                                value=ManualState.new_issue_title,
                                on_change=lambda v: setattr(ManualState, 'new_issue_title', v),
                                required=True
                            ),
                            
                            labeled_textarea(
                                label="Issue Description",
                                placeholder="Describe the issue in detail...",
                                value=ManualState.new_issue_body,
                                on_change=lambda v: setattr(ManualState, 'new_issue_body', v)
                            ),
                            
                            rx.button(
                                "➕ Add Issue",
                                on_click=ManualState.add_issue,
                                disabled=(~ManualState.new_issue_title.strip()) | (~ManualState.selected_milestone),
                                size="3"
                            ),
                            
                            spacing="4",
                            width="100%"
                        )
                    )
                ),
                
                # Deploy Section
                rx.cond(
                    ManualState.manual_milestones,
                    rx.card(
                        rx.vstack(
                            rx.heading("🚀 Deploy Manual Entries", size="4"),
                            
                            rx.cond(
                                AppState.github_connected,
                                alert(
                                    title="Ready for Deployment",
                                    description=f"Will deploy to {AppState.repo_owner}/{AppState.repo_name}",
                                    type="success"
                                ),
                                alert(
                                    title="GitHub Configuration Required",
                                    description="Please configure your GitHub settings",
                                    type="error"
                                )
                            ),
                            
                            rx.flex(
                                rx.button(
                                    "🗑️ Clear All",
                                    on_click=ManualState.clear_all_entries,
                                    variant="outline",
                                    color_scheme="red"
                                ),
                                
                                rx.button(
                                    "🚀 Deploy to GitHub",
                                    on_click=lambda: ManualState.deploy_manual_entries(False, True),
                                    disabled=~AppState.github_connected,
                                    size="3"
                                ),
                                
                                gap="3",
                                justify="end",
                                width="100%"
                            ),
                            
                            spacing="4",
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
