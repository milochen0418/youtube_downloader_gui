import reflex as rx


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("cloud_download", class_name="h-8 w-8 text-indigo-600 mr-3"),
                rx.el.div(
                    rx.el.h1(
                        "yt-dlp Web GUI",
                        class_name="text-2xl font-bold text-gray-900 leading-tight",
                    ),
                    rx.el.p(
                        "Fetch metadata and download media easily",
                        class_name="text-sm text-gray-500 font-medium",
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
        ),
        class_name="bg-white border-b border-gray-200 shadow-sm",
    )