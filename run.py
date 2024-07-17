from myapp import sock, create_app
import argparse
import logging
import ssl

app = create_app()

if __name__ == "__main__":
    sock.run(app, host="0.0.0.0", debug=True)
