"""
Shared UI components and utilities
"""

import reflex as rx
from typing import Any, Optional, List, Dict, Union

def alert(
    title: str,
    description: str,
    type: str = "info",
    icon: Optional[str] = None
) -> rx.Component:
    """Modern alert component"""
    
    # Icon mapping
    icon_map = {
        'success': 'check-circle',
        'warning': 'alert-triangle', 
        'error': 'x-circle',
        'info': 'info'
    }
    
    # Color scheme mapping
    color_map = {
        'success': 'green',
        'warning': 'orange',
        'error': 'red',
        'info': 'blue'
    }
    
    alert_icon = icon or icon_map.get(type, 'info')
    color_scheme = color_map.get(type, 'blue')
    
    return rx.callout.root(
        rx.callout.icon(rx.icon(alert_icon)),
        rx.callout.text(
            rx.vstack(
                rx.text(title, weight="medium", size="2"),
                rx.text(description, size="1", color="gray"),
                spacing="1",
                align="start"
            )
        ),
        color_scheme=color_scheme,
        margin="2"
    )

def metric_card(
    title: str,
    value: Union[str, int],
    icon: str,
    description: Optional[str] = None
) -> rx.Component:
    """Metric display card"""
    
    return rx.card(
        rx.flex(
            rx.flex(
                rx.vstack(
                    rx.text(title, size="1", color="gray"),
                    rx.heading(str(value), size="5", weight="bold"),
                    rx.cond(
                        description,
                        rx.text(description, size="1", color="gray"),
                        rx.text("")
                    ),
                    spacing="1",
                    align="start"
                ),
                flex="1"
            ),
            rx.flex(
                rx.icon(icon, size=24, color="var(--accent-9)"),
                justify="end"
            ),
            direction="row",
            align="start",
            width="100%"
        ),
        min_height="120px"
    )

def progress_bar(
    value: int,
    max_value: int = 100,
    show_percentage: bool = True,
    color: str = "blue"
) -> rx.Component:
    """Progress bar component"""
    
    percentage = min(100, max(0, (value / max_value) * 100)) if max_value > 0 else 0
    
    return rx.vstack(
        rx.cond(
            show_percentage,
            rx.flex(
                rx.text(f"{percentage:.0f}%", size="2", weight="medium"),
                justify="end",
                width="100%"
            ),
            rx.text("")
        ),
        rx.progress(
            value=percentage,
            color_scheme=color,
            size="2"
        ),
        spacing="1",
        width="100%"
    )

def status_badge(
    status: str,
    color_scheme: Optional[str] = None
) -> rx.Component:
    """Status badge component"""
    
    # Default color schemes for common statuses
    default_colors = {
        'connected': 'green',
        'disconnected': 'red',
        'processing': 'blue',
        'completed': 'green',
        'error': 'red',
        'pending': 'gray',
        'running': 'blue'
    }
    
    color = color_scheme or default_colors.get(status.lower(), 'gray')
    
    return rx.badge(
        status.title(),
        color_scheme=color,
        variant="soft"
    )

def file_upload_zone(
    on_upload: Any,
    accept: str = ".md,.markdown,.txt",
    multiple: bool = True,
    max_size: int = 10  # MB
) -> rx.Component:
    """File upload drop zone"""
    
    return rx.upload(
        rx.vstack(
            rx.icon("upload", size=48, color="var(--gray-9)"),
            rx.heading("Drop files here or click to browse", size="4", color="var(--gray-11)"),
            rx.text(
                f"Supported formats: {accept.replace(',', ', ')}",
                size="2",
                color="var(--gray-9)"
            ),
            rx.text(
                f"Maximum file size: {max_size}MB",
                size="1",
                color="var(--gray-8)"
            ),
            spacing="2",
            align="center"
        ),
        border="2px dashed var(--gray-7)",
        border_radius="var(--radius-3)",
        padding="3rem",
        text_align="center",
        background="var(--gray-2)",
        transition="all 0.2s ease",
        _hover={
            "border_color": "var(--accent-8)",
            "background": "var(--accent-2)"
        },
        id="upload",
        on_upload=on_upload,
        accept=accept,
        multiple=multiple,
        max_files=20 if multiple else 1,
        max_size=max_size * 1024 * 1024  # Convert to bytes
    )

def data_table(
    headers: List[str],
    rows: List[List[Any]],
    actions: Optional[List[rx.Component]] = None
) -> rx.Component:
    """Simple data table component"""
    
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[rx.table.column_header_cell(header) for header in headers],
                rx.cond(
                    actions,
                    rx.table.column_header_cell("Actions"),
                    rx.text("")
                )
            )
        ),
        rx.table.body(
            *[
                rx.table.row(
                    *[rx.table.cell(str(cell)) for cell in row],
                    rx.cond(
                        actions,
                        rx.table.cell(
                            rx.flex(*actions, gap="2") if actions else rx.text("")
                        ),
                        rx.text("")
                    )
                )
                for row in rows
            ]
        ),
        variant="surface",
        size="2"
    )

def loading_spinner(
    text: str = "Loading...",
    size: str = "3"
) -> rx.Component:
    """Loading spinner component"""
    
    return rx.flex(
        rx.spinner(size=size),
        rx.text(text, size="2", color="gray"),
        direction="column",
        align="center",
        gap="3"
    )

def empty_state(
    icon: str,
    title: str,
    description: str,
    action_button: Optional[rx.Component] = None
) -> rx.Component:
    """Empty state component"""
    
    return rx.flex(
        rx.icon(icon, size=64, color="var(--gray-8)"),
        rx.vstack(
            rx.heading(title, size="5", color="var(--gray-11)"),
            rx.text(description, size="3", color="var(--gray-9)", text_align="center"),
            spacing="2",
            align="center"
        ),
        rx.cond(
            action_button,
            action_button,
            rx.text("")
        ),
        direction="column",
        align="center",
        gap="4",
        padding="4rem",
        text_align="center"
    )

def confirmation_dialog(
    title: str,
    description: str,
    on_confirm: Any,
    on_cancel: Any,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    danger: bool = False
) -> rx.Component:
    """Confirmation dialog component"""
    
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(title),
            rx.alert_dialog.description(description),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        cancel_text,
                        variant="outline",
                        color_scheme="gray"
                    )
                ),
                rx.alert_dialog.action(
                    rx.button(
                        confirm_text,
                        color_scheme="red" if danger else "blue",
                        on_click=on_confirm
                    )
                ),
                gap="3",
                justify="end"
            ),
            style={"max_width": 450}
        )
    )

def section_header(
    title: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    actions: Optional[List[rx.Component]] = None
) -> rx.Component:
    """Section header with optional actions"""
    
    return rx.flex(
        rx.flex(
            rx.cond(
                icon,
                rx.icon(icon, size=24),
                rx.text("")
            ),
            rx.vstack(
                rx.heading(title, size="6"),
                rx.cond(
                    description,
                    rx.text(description, size="2", color="gray"),
                    rx.text("")
                ),
                spacing="1",
                align="start"
            ),
            align="center",
            gap="3"
        ),
        rx.cond(
            actions,
            rx.flex(*actions, gap="2") if actions else rx.text(""),
            rx.text("")
        ),
        justify="between",
        align="center",
        width="100%",
        margin_bottom="4"
    )

def card_grid(
    items: List[rx.Component],
    columns: int = 3
) -> rx.Component:
    """Grid layout for cards"""
    
    return rx.grid(
        *items,
        columns=str(columns),
        gap="4",
        width="100%"
    )

def labeled_input(
    label: str,
    placeholder: str = "",
    value: Any = "",
    on_change: Any = None,
    type: str = "text",
    required: bool = False,
    help_text: Optional[str] = None
) -> rx.Component:
    """Labeled input component"""
    
    return rx.vstack(
        rx.flex(
            rx.text(label, size="2", weight="medium"),
            rx.cond(
                required,
                rx.text("*", color="red"),
                rx.text("")
            ),
            gap="1"
        ),
        rx.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            type=type,
            required=required
        ),
        rx.cond(
            help_text,
            rx.text(help_text, size="1", color="gray"),
            rx.text("")
        ),
        spacing="1",
        align="start",
        width="100%"
    )

def labeled_textarea(
    label: str,
    placeholder: str = "",
    value: Any = "",
    on_change: Any = None,
    rows: int = 3,
    required: bool = False,
    help_text: Optional[str] = None
) -> rx.Component:
    """Labeled textarea component"""
    
    return rx.vstack(
        rx.flex(
            rx.text(label, size="2", weight="medium"),
            rx.cond(
                required,
                rx.text("*", color="red"),
                rx.text("")
            ),
            gap="1"
        ),
        rx.text_area(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            rows=rows,
            required=required,
            resize="vertical"
        ),
        rx.cond(
            help_text,
            rx.text(help_text, size="1", color="gray"),
            rx.text("")
        ),
        spacing="1",
        align="start",
        width="100%"
    )
