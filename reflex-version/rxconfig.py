import reflex as rx

config = rx.Config(
    app_name="githubmanager_reflex",
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        scaling="100%",
    ),
    frontend_packages=[
        "react-dropzone",
        "lucide-react",
    ],
)