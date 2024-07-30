
FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY . .



RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN chmod +x /app/build.sh


ENTRYPOINT ["/app/build.sh"]
