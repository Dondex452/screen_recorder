# PC Screen Recorder

A lightweight, optimized screen recording application for Windows, built with Python. Perfect for gamers, educators, professionals, content creators, and programmers.

## Features

- **Screen Recording:** Capture full screen, specific windows, or custom regions
- **Audio Recording:** Record microphone and system audio (separately or mixed)
- **Text Annotations:** Add text during or after recording
- **Video Editing:** Basic trimming, cutting, and merging capabilities
- **Resolution Options:** Customizable video resolution (480p, 720p, 1080p)
- **Multiple Export Formats:** Save in MP4, AVI, and MOV formats

## Installation

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install FFmpeg (required for audio/video processing):
   - Download FFmpeg from the official website
   - Add FFmpeg to your system PATH

## Usage

Run the application:
```bash
python main.py
```

## Development

The project structure is organized as follows:
```
screen_recorder/
├── main.py                  # Entry point
├── screen_capture.py        # Screen recording functionality
├── audio_capture.py         # Audio recording functionality
├── video_processing.py      # Video editing and processing
├── annotations.py           # Text annotations
├── gui.py                   # User interface
├── utils/                   # Utility functions
│   ├── file_utils.py
│   ├── resolution_utils.py
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

## License

MIT License
