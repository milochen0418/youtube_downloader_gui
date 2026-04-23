# yt-dlp Web GUI Application

## Design Direction
- Clean, modern two-column layout: input/controls on left, results/output on right
- Indigo-600 accent color, white cards with subtle borders on gray-50 background
- Inter font, flat surfaces, strong typography, minimal chrome
- Responsive design with clear section separation using tabs

## Phase 1: Core Layout, URL Input, Metadata Fetching & Display ✅
- [x] Install yt-dlp dependency
- [x] Build two-column responsive layout with header, URL input field, and submit button
- [x] Implement async metadata fetching using yt-dlp --dump-json via background task
- [x] Display video metadata: title, duration, thumbnail, description, channel, view count
- [x] Show available formats in a sortable/filterable table (resolution, codec, filesize, format ID)
- [x] Add loading states, error handling for invalid URLs, and raw command output panel

## Phase 2: Format Selection, Download Simulation & Progress Display ✅
- [x] Build format selection UI with checkboxes/dropdown for quality presets (best, audio-only, specific resolution)
- [x] Implement download initiation with real-time progress updates via background task
- [x] Show download progress bar with percentage, speed, ETA, and file size
- [x] Add raw CLI output log area that streams yt-dlp stdout in real-time
- [x] Implement error states and cancellation feedback

## Phase 3: Advanced Features - Subtitles, Playlist Handling & Output Management ✅
- [x] Implement subtitle/caption extraction toggle with display of available subtitle languages
- [x] Add playlist detection and handling: show playlist info, video range selector
- [x] Build tabbed interface for organizing metadata, formats, subtitles, playlist, and raw output
- [x] Add download history section showing completed downloads with details
- [x] Polish UI with responsive design, hover states, empty states, and final styling pass
