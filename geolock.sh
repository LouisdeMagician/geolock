#!/bin/bash

# Start the websocket server in the background
python3 backend/websocket.py &
WEBSOCKET_PID=$!
echo "Started websocket.py with PID $WEBSOCKET_PID"

# Function to handle cleanup of geolock.py
cleanup_geolock() {
    echo "Shutting down geolock.py..."
    kill $GEOLOCK_PID
    echo "geolock.py stopped."
    exit 0
}


# Trap Ctrl+C (SIGINT) to run the cleanup function for geolock.py
trap cleanup_geolock SIGINT

# Start geolock.py in the foreground
python3 backend/geolock.py 
GEOLOCK_PID=$!
wait $GEOLOCK_PID


done
