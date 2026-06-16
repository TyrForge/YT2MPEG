FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System deps: X11/Qt6 runtime, VNC, noVNC, ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    xvfb \
    x11vnc \
    websockify \
    novnc \
    # Qt6 / PySide6 runtime requirements
    libgl1 \
    libglib2.0-0 \
    libdbus-1-3 \
    libegl1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy app
COPY src/ /app/src/
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 6080

ENV DOWNLOAD_DIR=/downloads

ENTRYPOINT ["/start.sh"]
