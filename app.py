from app import app 
import os

PORT = int(os.environ.get("PORT", 5000))

if __name__== "__main__":
	app.run(debug = True, host="0.0.0.0", port=PORT)

