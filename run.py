from myapp import sock, create_app

app = create_app()

if __name__ == "__main__":
    sock.run(app, debug=True)
