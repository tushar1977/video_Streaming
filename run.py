from myapp import sock, create_app
import os

app = create_app()

if __name__ == "__main__":
    sock.run(app, host="0.0.0.0", debug=True, port=int(os.getenv("PORT", 5001)))
