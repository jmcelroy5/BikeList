from app import app 
import os

PORT = int(os.environ.get("PORT", 5000))
DEBUG = "NO_DEBUG" not in os.environ

if __name__== "__main__":
	app.run(debug = DEBUG, host="0.0.0.0", port=PORT)

