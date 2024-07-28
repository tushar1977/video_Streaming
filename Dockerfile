
FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app


ENV PORT=8000

ENV FLASK_ENV=production
ENV DB_USERNAME=tushar
ENV DB_PASSWORD=Tushar2005!
ENV DB_HOSTNAME=84.247.185.93
ENV DB_NAME=video_streaming

COPY . .



RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN chmod +x /app/build.sh


ENTRYPOINT ["/app/build.sh"]
