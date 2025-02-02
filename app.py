from flask import Flask, Response, request
import cv2
import numpy as np

app = Flask(__name__)

# Store the latest frame
latest_frame = None

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    file = request.files.get('frame')

    if file is not None:
        # Convert to OpenCV format
        file_bytes = np.frombuffer(file.read(), np.uint8)
        latest_frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
