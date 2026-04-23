import reflex as rx
from youtube_downloader_gui.states.yt_state import YTState


def input_panel() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "YouTube URL",
                    class_name="block text-sm font-semibold text-gray-700 mb-2",
                ),
                rx.el.input(
                    type="url",
                    name="url",
                    placeholder="Paste YouTube URL here...",
                    required=True,
                    class_name="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 shadow-sm text-gray-900 placeholder-gray-400 mb-4",
                ),
                rx.el.button(
                    rx.cond(
                        YTState.is_loading,
                        rx.el.div(
                            rx.icon(
                                "loader",
                                class_name="animate-spin h-5 w-5 mr-2 inline-block",
                            ),
                            "Fetching...",
                            class_name="flex items-center justify-center",
                        ),
                        "Fetch Info",
                    ),
                    type="submit",
                    disabled=YTState.is_loading,
                    class_name="w-full bg-indigo-600 text-white py-3 px-4 rounded-xl hover:bg-indigo-700 transition-colors font-medium shadow-md disabled:opacity-70 disabled:cursor-not-allowed",
                ),
                class_name="mb-4",
            ),
            on_submit=YTState.handle_submit,
            reset_on_submit=False,
        ),
        rx.cond(
            YTState.error_message != "",
            rx.el.div(
                rx.icon("circle_alert", class_name="h-5 w-5 text-red-500 mr-2"),
                rx.el.p(
                    YTState.error_message, class_name="text-sm text-red-700 font-medium"
                ),
                class_name="flex items-start bg-red-50 p-4 rounded-xl border border-red-100 mb-4",
            ),
            rx.el.div(),
        ),
        rx.cond(
            YTState.video_title != "",
            rx.el.div(
                rx.el.h3(
                    "Download Options",
                    class_name="text-lg font-bold text-gray-900 mb-4 border-t border-gray-100 pt-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Quality Preset",
                        class_name="block text-sm font-semibold text-gray-700 mb-2",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("Best Video + Audio (merged)", value="best"),
                            rx.el.option("Best Audio Only (M4A)", value="audio_m4a"),
                            rx.el.option("Best Audio Only (MP3)", value="audio_mp3"),
                            rx.el.option("720p MP4", value="720p"),
                            rx.el.option("480p MP4", value="480p"),
                            rx.el.option("360p MP4", value="360p"),
                            rx.el.option("Custom Format ID", value="custom"),
                            value=YTState.selected_preset,
                            on_change=YTState.set_preset,
                            disabled=YTState.is_downloading,
                            class_name="appearance-none w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 text-sm shadow-sm",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-3 top-3.5 h-5 w-5 text-gray-400 pointer-events-none",
                        ),
                        class_name="relative mb-4",
                    ),
                    rx.cond(
                        YTState.selected_preset == "custom",
                        rx.el.input(
                            type="text",
                            placeholder="Enter format ID (e.g. 137+140)",
                            on_change=YTState.set_custom_format,
                            disabled=YTState.is_downloading,
                            class_name="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4 text-sm",
                            default_value=YTState.custom_format_id,
                        ),
                        rx.el.div(),
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                YTState.is_downloading,
                                rx.el.div(
                                    rx.icon(
                                        "loader",
                                        class_name="animate-spin h-5 w-5 mr-2 inline-block",
                                    ),
                                    "Downloading...",
                                    class_name="flex items-center justify-center",
                                ),
                                "Start Download",
                            ),
                            on_click=YTState.start_download,
                            disabled=YTState.is_downloading,
                            class_name="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-xl hover:bg-indigo-700 transition-colors font-medium shadow-md disabled:opacity-70 disabled:cursor-not-allowed",
                        ),
                        rx.cond(
                            YTState.is_downloading,
                            rx.el.button(
                                rx.icon("x", class_name="h-5 w-5"),
                                on_click=YTState.cancel_download,
                                class_name="bg-red-500 text-white py-3 px-4 rounded-xl hover:bg-red-600 transition-colors shadow-md flex-shrink-0",
                            ),
                            rx.el.div(),
                        ),
                        class_name="flex gap-2 mb-4",
                    ),
                    rx.cond(
                        (YTState.download_status != "") | YTState.is_downloading,
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    YTState.download_status,
                                    class_name="text-sm font-semibold text-gray-700",
                                ),
                                rx.el.span(
                                    f"{YTState.download_progress:.1f}%",
                                    class_name="text-sm font-bold text-indigo-600",
                                ),
                                class_name="flex justify-between mb-2",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name=rx.cond(
                                        YTState.download_status == "Error",
                                        "bg-red-500 h-2 rounded-full transition-all duration-300",
                                        rx.cond(
                                            YTState.download_status == "Cancelled",
                                            "bg-yellow-500 h-2 rounded-full transition-all duration-300",
                                            "bg-indigo-600 h-2 rounded-full transition-all duration-300",
                                        ),
                                    ),
                                    style={"width": f"{YTState.download_progress}%"},
                                ),
                                class_name="w-full bg-gray-200 rounded-full h-2 mb-2 overflow-hidden",
                            ),
                            rx.el.div(
                                rx.cond(
                                    YTState.download_speed != "",
                                    rx.el.span(
                                        rx.icon(
                                            "activity", class_name="h-3 w-3 inline mr-1"
                                        ),
                                        YTState.download_speed,
                                        class_name="flex items-center",
                                    ),
                                    rx.el.span(),
                                ),
                                rx.cond(
                                    YTState.download_eta != "",
                                    rx.el.span(
                                        rx.icon(
                                            "clock", class_name="h-3 w-3 inline mr-1"
                                        ),
                                        YTState.download_eta,
                                        class_name="flex items-center",
                                    ),
                                    rx.el.span(),
                                ),
                                rx.cond(
                                    YTState.download_size != "",
                                    rx.el.span(
                                        rx.icon(
                                            "hard-drive",
                                            class_name="h-3 w-3 inline mr-1",
                                        ),
                                        YTState.download_size,
                                        class_name="flex items-center",
                                    ),
                                    rx.el.span(),
                                ),
                                class_name="flex justify-between text-xs text-gray-500 font-medium",
                            ),
                            class_name="bg-gray-50 p-4 rounded-xl border border-gray-100 mb-6",
                        ),
                        rx.el.div(),
                    ),
                ),
                rx.cond(
                    YTState.download_history.length() > 0,
                    rx.el.div(
                        rx.el.h4(
                            "Download History",
                            class_name="text-sm font-bold text-gray-900 mb-3",
                        ),
                        rx.el.div(
                            rx.foreach(
                                YTState.download_history,
                                lambda hist: rx.el.div(
                                    rx.el.div(
                                        rx.el.p(
                                            hist["title"],
                                            class_name="text-sm font-medium text-gray-900 truncate max-w-[200px]",
                                        ),
                                        rx.el.span(
                                            hist["status"],
                                            class_name=rx.cond(
                                                hist["status"] == "Complete",
                                                "text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium",
                                                "text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium",
                                            ),
                                        ),
                                        class_name="flex justify-between items-center mb-1",
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            hist["format"],
                                            class_name="text-xs text-gray-500",
                                        ),
                                        rx.el.span(
                                            hist["timestamp"],
                                            class_name="text-xs text-gray-400",
                                        ),
                                        class_name="flex justify-between",
                                    ),
                                    class_name="p-3 bg-white border border-gray-100 rounded-lg shadow-sm",
                                ),
                            ),
                            class_name="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1",
                        ),
                        class_name="mt-6 pt-4 border-t border-gray-100",
                    ),
                    rx.el.div(),
                ),
            ),
            rx.el.div(),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 h-fit",
    )