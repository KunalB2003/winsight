from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

print("Connecting Webcam")
camera = cv2.VideoCapture(2)
print("Webcam Connected")

def gen_color_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            color_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + color_bytes + b'\r\n')

def gen_altered_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
            ret, thresholded_frame = cv2.threshold(blurred_frame, 150, 255, cv2.THRESH_BINARY)        
            # contoured_frame, _ = cv2.findContours(thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            ret, buffer = cv2.imencode('.jpg', thresholded_frame)
            altered_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + altered_bytes + b'\r\n')

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_color_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_altered')
def video_feed_altered():
    return Response(gen_altered_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)