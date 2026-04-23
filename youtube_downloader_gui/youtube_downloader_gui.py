import reflex as rx
from youtube_downloader_gui.components.header import header
from youtube_downloader_gui.components.input_panel import input_panel
from youtube_downloader_gui.components.results_panel import results_panel


def index() -> rx.Component:
    return rx.el.div(
        header(),
        rx.el.main(
            rx.el.div(
                rx.el.div(input_panel(), class_name="w-full lg:w-[40%] flex-shrink-0"),
                rx.el.div(results_panel(), class_name="w-full lg:w-[60%] flex-grow"),
                class_name="flex flex-col lg:flex-row gap-6 lg:gap-8",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
        ),
        class_name="min-h-screen bg-gray-50 font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")