from flask import Flask
import parakeet

app = Flask(__name__)

@app.route("/")
def hello_world():
    text = "Hello, world!" # test()
    return f"<p>{text}</p>"