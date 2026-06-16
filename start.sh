#!/bin/bash
set -e

DISPLAY_NUM=:1
SCREEN_RES="${RESOLUTION:-1280x800x24}"
VNC_PORT=5900
NOVNC_PORT=6080

# Create download dir if needed
mkdir -p "${DOWNLOAD_DIR:-/downloads}"

# Start virtual display
Xvfb $DISPLAY_NUM -screen 0 $SCREEN_RES -ac +extension GLX +render -noreset &
sleep 1

# Start VNC server (no password, localhost only)
x11vnc -display $DISPLAY_NUM -forever -nopw -shared -localhost -quiet &

# Start noVNC websocket proxy
websockify --web /opt/novnc $NOVNC_PORT localhost:$VNC_PORT &

echo "noVNC available at http://localhost:${NOVNC_PORT}/vnc.html"

# Launch the app
DISPLAY=$DISPLAY_NUM python3 /app/src/main.py
