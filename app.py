from flask import Flask, Response, request
import cv2
import numpy as np
import os
import time

app = Flask(__name__)

# Set max upload size (2MB) to prevent large file abuse
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  

# Store the latest frame globally
latest_frame = None

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    file = request.files.get('frame')

    if file is not None:
        # Convert uploaded file to OpenCV format
        file_bytes = np.frombuffer(file.read(), np.uint8)
        decoded_frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if decoded_frame is None:
            return "Invalid frame", 400  # Prevents crashes if decoding fails

        latest_frame = decoded_frame
        return "Frame received", 200
    return "No frame received", 400

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            _, buffer = cv2.imencode('.jpg', latest_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.05)  # Prevents 100% CPU usage

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Supports dynamic port assignment for deployment
    app.run(host='0.0.0.0', port=port)
