from flask import Flask, url_for, render_template, request
import cv2
import numpy

app = Flask(__name__)

app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    imagefile = request.files.get('myfile', '')
    imagefile.save("flask_imagefile.png")

    img = cv2.imread("flask_imagefile.png")
    print(img)
    return "submitted"

if __name__ == '__main__':
    app.run()