from flask import Flask
import socket

app = Flask(__name__)

@app.route("/")
def index():
	return socket.gethostname() + "<br>" + "Abid Waqar" + " I16-0229"
	
if __name__ == "__main__":
	app.run(debug=True, host= '0.0.0.0')
