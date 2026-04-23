import reflex as rx
from youtube_downloader_gui.states.yt_state import YTState


def tab_button(label: str) -> rx.Component:
    is_active = YTState.active_tab == label
    return rx.el.button(
        label,
        on_click=lambda: YTState.set_tab(label),
        class_name=rx.cond(
            is_active,
            "px-4 py-3 text-sm font-semibold text-indigo-600 border-b-2 border-indigo-600 whitespace-nowrap",
            "px-4 py-3 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent whitespace-nowrap transition-colors",
        ),
    )


def metadata_tab() -> rx.Component:
    return rx.el.div(
        rx.cond(
            YTState.thumbnail_url != "",
            rx.el.div(
                rx.image(
                    src=YTState.thumbnail_url,
                    class_name="w-full max-w-sm rounded-xl shadow-sm border border-gray-200 mb-6 object-cover aspect-video",
                ),
                rx.el.h2(
                    YTState.video_title,
                    class_name="text-xl font-bold text-gray-900 mb-2",
                ),
                rx.el.div(
                    rx.el.span(
                        rx.icon("user", class_name="h-4 w-4 mr-1 inline"),
                        YTState.channel,
                        class_name="inline-flex items-center text-gray-600 mr-4 font-medium text-sm",
                    ),
                    rx.el.span(
                        rx.icon("clock", class_name="h-4 w-4 mr-1 inline"),
                        YTState.duration,
                        class_name="inline-flex items-center text-gray-600 mr-4 text-sm",
                    ),
                    rx.el.span(
                        rx.icon("eye", class_name="h-4 w-4 mr-1 inline"),
                        f"{YTState.view_count} views",
                        class_name="inline-flex items-center text-gray-600 mr-4 text-sm",
                    ),
                    rx.el.span(
                        rx.icon("calendar", class_name="h-4 w-4 mr-1 inline"),
                        YTState.upload_date,
                        class_name="inline-flex items-center text-gray-600 text-sm",
                    ),
                    class_name="flex flex-wrap gap-y-2 mb-6",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Description",
                        class_name="text-sm font-semibold text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        rx.cond(
                            YTState.show_full_description,
                            YTState.description,
                            YTState.description[:200] + "...",
                        ),
                        class_name="text-sm text-gray-600 whitespace-pre-wrap break-words",
                    ),
                    rx.cond(
                        YTState.description.length() > 200,
                        rx.el.button(
                            rx.cond(
                                YTState.show_full_description, "Show Less", "Show More"
                            ),
                            on_click=YTState.toggle_description,
                            class_name="text-indigo-600 text-sm font-medium hover:text-indigo-800 mt-2",
                        ),
                        rx.el.div(),
                    ),
                    class_name="bg-gray-50 p-4 rounded-xl border border-gray-100",
                ),
                class_name="animate-fade-in",
            ),
            rx.el.div(),
        )
    )


def formats_tab() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                f"Found {YTState.formats.length()} formats",
                class_name="bg-indigo-100 text-indigo-800 text-xs font-semibold px-2.5 py-1 rounded-full mb-4 inline-block",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "ID",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider rounded-tl-lg",
                            ),
                            rx.el.th(
                                "Ext",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Resolution",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Video",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Audio",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Size",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Note",
                                class_name="px-4 py-3 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider rounded-tr-lg",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            YTState.formats,
                            lambda fmt: rx.el.tr(
                                rx.el.td(
                                    fmt["format_id"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.td(
                                    fmt["ext"],
                                    class_name="px-4 py-3 text-sm text-gray-500",
                                ),
                                rx.el.td(
                                    fmt["resolution"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.td(
                                    fmt["vcodec"],
                                    class_name="px-4 py-3 text-sm text-gray-500 truncate max-w-[100px]",
                                ),
                                rx.el.td(
                                    fmt["acodec"],
                                    class_name="px-4 py-3 text-sm text-gray-500 truncate max-w-[100px]",
                                ),
                                rx.el.td(
                                    fmt["filesize"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.td(
                                    fmt["format_note"],
                                    class_name="px-4 py-3 text-sm text-gray-500",
                                ),
                                class_name="border-t border-gray-100 hover:bg-gray-50 transition-colors even:bg-gray-50/50",
                            ),
                        )
                    ),
                    class_name="min-w-full",
                ),
                class_name="overflow-x-auto border border-gray-200 rounded-lg",
            ),
            class_name="animate-fade-in",
        )
    )


def raw_output_tab() -> rx.Component:
    return rx.el.div(
        rx.el.pre(
            rx.el.code(
                YTState.raw_output, class_name="text-xs text-gray-800 font-mono"
            ),
            class_name="bg-gray-50 p-4 rounded-xl border border-gray-200 overflow-x-auto max-h-[600px] overflow-y-auto",
        ),
        class_name="animate-fade-in",
    )


def download_log_tab() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4 mr-2"),
                "Clear Log",
                on_click=YTState.clear_log,
                class_name="text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1.5 rounded-lg flex items-center mb-3 transition-colors font-medium",
            ),
            class_name="flex justify-end",
        ),
        rx.scroll_area(
            rx.el.pre(
                rx.foreach(
                    YTState.download_log,
                    lambda line: rx.el.div(line, class_name="min-h-[1.2rem]"),
                ),
                class_name="text-xs text-gray-300 font-mono p-4",
            ),
            type="always",
            scrollbars="vertical",
            class_name="bg-gray-900 rounded-xl border border-gray-800 h-[500px]",
        ),
        class_name="animate-fade-in",
    )


def subtitles_tab() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("music", class_name="h-8 w-8 text-indigo-600 mr-3"),
                rx.el.div(
                    rx.el.h2(
                        "Lyrics & Subtitles",
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Extract lyrics and captions from this video",
                        class_name="text-sm text-gray-500",
                    ),
                ),
                class_name="flex items-center mb-6",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("music-4", class_name="h-5 w-5 mr-2"),
                    rx.el.div(
                        rx.el.span(
                            "Get Lyrics (Auto-Captions)",
                            class_name="block font-semibold",
                        ),
                        rx.el.span(
                            "Best for music videos — fetches auto-generated captions in English",
                            class_name="block text-xs font-normal opacity-90 mt-1",
                        ),
                        class_name="text-left",
                    ),
                    on_click=YTState.fetch_auto_lyrics,
                    class_name="w-full flex items-start bg-indigo-600 text-white p-4 rounded-xl hover:bg-indigo-700 transition-colors shadow-sm",
                ),
                rx.el.button(
                    rx.icon("captions", class_name="h-5 w-5 mr-2"),
                    rx.el.div(
                        rx.el.span(
                            "Get Manual Subtitles", class_name="block font-semibold"
                        ),
                        rx.el.span(
                            "Fetches human-uploaded subtitles if available",
                            class_name="block text-xs font-normal mt-1",
                        ),
                        class_name="text-left",
                    ),
                    on_click=YTState.fetch_manual_lyrics,
                    class_name="w-full flex items-start bg-white text-indigo-600 border border-indigo-200 p-4 rounded-xl hover:bg-indigo-50 transition-colors shadow-sm",
                ),
                rx.el.button(
                    rx.icon("globe", class_name="h-5 w-5 mr-2"),
                    rx.el.div(
                        rx.el.span("Choose Language", class_name="block font-semibold"),
                        rx.el.span(
                            "Pick a specific language from available options",
                            class_name="block text-xs font-normal mt-1",
                        ),
                        class_name="text-left",
                    ),
                    on_click=YTState.toggle_language_picker,
                    class_name="w-full flex items-start bg-white text-gray-700 border border-gray-200 p-4 rounded-xl hover:bg-gray-50 transition-colors shadow-sm",
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6",
            ),
            rx.cond(
                YTState.show_language_picker,
                rx.el.div(
                    rx.el.label(
                        "Select Language:",
                        class_name="text-sm font-semibold text-gray-700 mr-3",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                YTState.subtitles + YTState.auto_captions,
                                lambda lang: rx.el.option(lang, value=lang),
                            ),
                            value=YTState.selected_subtitle_lang,
                            on_change=YTState.set_selected_subtitle_lang,
                            class_name="appearance-none w-48 p-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                        ),
                        class_name="relative mr-3",
                    ),
                    rx.el.button(
                        "Fetch",
                        on_click=lambda: YTState.fetch_lyrics_by_lang(
                            YTState.selected_subtitle_lang
                        ),
                        class_name="bg-gray-800 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-900 transition-colors",
                    ),
                    class_name="flex items-center bg-gray-50 p-4 rounded-xl border border-gray-100 mb-6 animate-fade-in",
                ),
                rx.el.div(),
            ),
            rx.cond(
                YTState.is_fetching_lyrics,
                rx.el.div(
                    rx.icon(
                        "loader",
                        class_name="animate-spin h-6 w-6 text-indigo-600 mx-auto mb-2",
                    ),
                    rx.el.p(
                        "Fetching lyrics...",
                        class_name="text-sm text-gray-500 text-center",
                    ),
                    class_name="py-12",
                ),
                rx.cond(
                    YTState.lyrics_content != "",
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                YTState.lyrics_source,
                                class_name="bg-indigo-100 text-indigo-800 text-xs font-semibold px-2.5 py-1 rounded-full",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("copy", class_name="h-4 w-4 mr-1.5"),
                                    "Copy",
                                    on_click=YTState.copy_lyrics,
                                    class_name="flex items-center text-xs font-medium text-gray-600 hover:text-indigo-600 mr-4 transition-colors",
                                ),
                                rx.el.button(
                                    rx.icon("x", class_name="h-4 w-4 mr-1.5"),
                                    "Clear",
                                    on_click=YTState.clear_lyrics,
                                    class_name="flex items-center text-xs font-medium text-gray-600 hover:text-red-600 transition-colors",
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="flex justify-between items-center bg-gray-50 p-3 border-b border-gray-200",
                        ),
                        rx.scroll_area(
                            rx.el.pre(
                                YTState.lyrics_content,
                                class_name="text-sm text-gray-800 font-sans whitespace-pre-wrap leading-relaxed p-6",
                            ),
                            type="always",
                            scrollbars="vertical",
                            class_name="h-[500px]",
                        ),
                        class_name="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm mb-6 animate-fade-in",
                    ),
                    rx.el.div(),
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.el.span(
                        "Available Languages",
                        class_name="text-sm font-semibold text-gray-700",
                    ),
                    rx.cond(
                        YTState.show_available_langs,
                        rx.icon("chevron-up", class_name="h-4 w-4 text-gray-500"),
                        rx.icon("chevron-down", class_name="h-4 w-4 text-gray-500"),
                    ),
                    on_click=YTState.toggle_available_langs,
                    class_name="flex justify-between items-center w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-colors mb-3",
                ),
                rx.cond(
                    YTState.show_available_langs,
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Manual Subtitles",
                                class_name="text-xs font-semibold text-gray-500 uppercase mb-2",
                            ),
                            rx.cond(
                                YTState.subtitles.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        YTState.subtitles,
                                        lambda lang: rx.el.span(
                                            lang,
                                            class_name="bg-indigo-50 text-indigo-700 text-xs font-semibold px-2 py-1 rounded-md border border-indigo-100",
                                        ),
                                    ),
                                    class_name="flex flex-wrap gap-2",
                                ),
                                rx.el.p(
                                    "None available", class_name="text-sm text-gray-400"
                                ),
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Auto-Generated Captions",
                                class_name="text-xs font-semibold text-gray-500 uppercase mb-2",
                            ),
                            rx.cond(
                                YTState.auto_captions.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        YTState.auto_captions,
                                        lambda lang: rx.el.span(
                                            lang,
                                            class_name="bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-1 rounded-md border border-gray-200",
                                        ),
                                    ),
                                    class_name="flex flex-wrap gap-2",
                                ),
                                rx.el.p(
                                    "None available", class_name="text-sm text-gray-400"
                                ),
                            ),
                        ),
                        class_name="p-4 border border-t-0 border-gray-200 rounded-b-xl -mt-4 bg-white",
                    ),
                    rx.el.div(),
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.el.span(
                        "Advanced Download Options",
                        class_name="text-sm font-semibold text-gray-700",
                    ),
                    rx.cond(
                        YTState.show_advanced_subtitle_options,
                        rx.icon("chevron-up", class_name="h-4 w-4 text-gray-500"),
                        rx.icon("chevron-down", class_name="h-4 w-4 text-gray-500"),
                    ),
                    on_click=YTState.toggle_advanced_subtitle_options,
                    class_name="flex justify-between items-center w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-colors",
                ),
                rx.cond(
                    YTState.show_advanced_subtitle_options,
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                rx.el.input(
                                    type="checkbox",
                                    checked=YTState.subtitle_write_subs,
                                    on_change=YTState.set_subtitle_write_subs,
                                    class_name="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2",
                                ),
                                "Include manual subtitles (--write-subs)",
                                class_name="flex items-center text-sm font-medium text-gray-700 cursor-pointer",
                            ),
                            rx.el.label(
                                rx.el.input(
                                    type="checkbox",
                                    checked=YTState.subtitle_write_auto_subs,
                                    on_change=YTState.set_subtitle_write_auto_subs,
                                    class_name="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2",
                                ),
                                "Include auto-generated subtitles (--write-auto-subs)",
                                class_name="flex items-center text-sm font-medium text-gray-700 cursor-pointer",
                            ),
                            class_name="flex flex-col gap-3 mb-5",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Languages (--sub-langs)",
                                    class_name="block text-xs font-semibold text-gray-500 uppercase mb-2",
                                ),
                                rx.el.input(
                                    type="text",
                                    placeholder="e.g. en,es,de",
                                    on_change=YTState.set_subtitle_langs,
                                    class_name="w-full p-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm",
                                    default_value=YTState.subtitle_langs,
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Format (--sub-format)",
                                    class_name="block text-xs font-semibold text-gray-500 uppercase mb-2",
                                ),
                                rx.el.div(
                                    rx.el.select(
                                        rx.el.option("srt", value="srt"),
                                        rx.el.option("vtt", value="vtt"),
                                        rx.el.option("ass", value="ass"),
                                        rx.el.option("json3", value="json3"),
                                        value=YTState.subtitle_format,
                                        on_change=YTState.set_subtitle_format,
                                        class_name="appearance-none w-full p-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm",
                                    ),
                                    rx.icon(
                                        "chevron-down",
                                        class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                    ),
                                    class_name="relative",
                                ),
                                class_name="w-48",
                            ),
                            class_name="flex flex-col sm:flex-row gap-4",
                        ),
                        class_name="p-5 border border-t-0 border-gray-200 rounded-b-xl -mt-2 bg-white",
                    ),
                    rx.el.div(),
                ),
            ),
        ),
        class_name="animate-fade-in",
    )


def playlist_tab() -> rx.Component:
    return rx.cond(
        YTState.is_playlist,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    YTState.playlist_title,
                    class_name="text-xl font-bold text-gray-900 mb-1",
                ),
                rx.el.p(
                    rx.icon("list-video", class_name="h-4 w-4 inline mr-1"),
                    f"{YTState.playlist_count} videos in playlist",
                    class_name="text-sm text-gray-600 flex items-center",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.h3(
                    "Download Options",
                    class_name="text-sm font-semibold text-gray-900 mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Start Index",
                            class_name="block text-xs font-semibold text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            min="1",
                            on_change=YTState.set_playlist_start,
                            class_name="w-24 p-2 bg-white border border-gray-300 rounded-lg text-sm",
                            default_value=YTState.playlist_start.to_string(),
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "End Index (0=All)",
                            class_name="block text-xs font-semibold text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            min="0",
                            on_change=YTState.set_playlist_end,
                            class_name="w-24 p-2 bg-white border border-gray-300 rounded-lg text-sm",
                            default_value=YTState.playlist_end.to_string(),
                        ),
                    ),
                    rx.el.button(
                        rx.cond(
                            YTState.is_downloading,
                            rx.el.div(
                                rx.icon(
                                    "loader",
                                    class_name="animate-spin h-4 w-4 mr-2 inline",
                                ),
                                "Downloading...",
                            ),
                            rx.el.div(
                                rx.icon("download", class_name="h-4 w-4 mr-2 inline"),
                                "Download Range",
                            ),
                        ),
                        on_click=YTState.start_playlist_download,
                        disabled=YTState.is_downloading,
                        class_name="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors self-end disabled:opacity-70 disabled:cursor-not-allowed flex items-center",
                    ),
                    class_name="flex items-end gap-4",
                ),
                class_name="bg-gray-50 p-4 rounded-xl border border-gray-100 mb-6",
            ),
            rx.cond(
                YTState.is_playlist_loading,
                rx.el.div(
                    rx.icon(
                        "loader",
                        class_name="animate-spin h-6 w-6 text-indigo-600 mx-auto mb-2",
                    ),
                    rx.el.p(
                        "Loading playlist entries...",
                        class_name="text-sm text-gray-500 text-center",
                    ),
                    class_name="py-12",
                ),
                rx.el.div(
                    rx.foreach(
                        YTState.playlist_entries,
                        lambda entry: rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    entry["index"],
                                    class_name="text-xs font-bold text-gray-400 w-8 flex-shrink-0",
                                ),
                                rx.el.div(
                                    rx.el.h4(
                                        entry["title"],
                                        class_name="text-sm font-semibold text-gray-900 truncate",
                                    ),
                                    rx.el.p(
                                        entry["uploader"],
                                        class_name="text-xs text-gray-500",
                                    ),
                                    class_name="flex-1 min-w-0 mr-4",
                                ),
                                rx.el.span(
                                    rx.icon("clock", class_name="h-3 w-3 inline mr-1"),
                                    entry["duration"],
                                    class_name="text-xs font-medium text-gray-500 flex items-center flex-shrink-0",
                                ),
                                class_name="flex items-center p-3 hover:bg-gray-50 transition-colors",
                            ),
                            class_name="border-b border-gray-100 last:border-0",
                        ),
                    ),
                    class_name="border border-gray-200 rounded-xl overflow-hidden max-h-[400px] overflow-y-auto bg-white",
                ),
            ),
            class_name="animate-fade-in",
        ),
        rx.el.div(
            rx.icon("list-x", class_name="h-12 w-12 text-gray-300 mx-auto mb-4"),
            rx.el.h3(
                "Not a Playlist", class_name="text-lg font-medium text-gray-900 mb-1"
            ),
            rx.el.p(
                "This URL does not appear to be a playlist.",
                class_name="text-sm text-gray-500",
            ),
            class_name="flex flex-col items-center justify-center py-16 text-center animate-fade-in",
        ),
    )


def results_panel() -> rx.Component:
    return rx.el.div(
        rx.cond(
            YTState.video_title == "",
            rx.el.div(
                rx.icon("youtube", class_name="h-16 w-16 text-gray-200 mx-auto mb-4"),
                rx.el.h3(
                    "No Video Loaded",
                    class_name="text-xl font-semibold text-gray-900 mb-2",
                ),
                rx.el.p(
                    "Enter a YouTube URL to get started fetching metadata and formats.",
                    class_name="text-gray-500 text-center max-w-md mx-auto",
                ),
                class_name="flex flex-col items-center justify-center h-full min-h-[400px] bg-white rounded-2xl shadow-sm border border-gray-200 p-8",
            ),
            rx.el.div(
                rx.el.div(
                    tab_button("Metadata"),
                    tab_button("Formats"),
                    tab_button("Download Log"),
                    tab_button("Subtitles"),
                    tab_button("Playlist"),
                    tab_button("Raw Output"),
                    class_name="flex overflow-x-auto border-b border-gray-200 scrollbar-hide mb-6",
                ),
                rx.match(
                    YTState.active_tab,
                    ("Metadata", metadata_tab()),
                    ("Formats", formats_tab()),
                    ("Download Log", download_log_tab()),
                    ("Raw Output", raw_output_tab()),
                    ("Subtitles", subtitles_tab()),
                    ("Playlist", playlist_tab()),
                    rx.el.div(),
                ),
                class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-200",
            ),
        )
    )