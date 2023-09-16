from flask import Flask, render_template, Response
import cv2
import numpy as np
from roboflow import Roboflow

app = Flask(__name__)
camera = cv2.VideoCapture(0)

rf = Roboflow(api_key="3nUG3gBfitus0Ympj3Y2")
project = rf.workspace().project("playing-cards-ow27d")
model = project.version(4).model

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
            ret, buffer = cv2.imencode('.jpg', frame)
            color_bytes = buffer.tobytes()

            predictions = model.predict(frame, confidence=40, overlap=30).json()["predictions"]
            print(len(predictions))
            for prediction in predictions:
                print(prediction["class"])

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + color_bytes + b'\r\n')


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