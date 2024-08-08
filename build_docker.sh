#!/bin/bash
sudo docker login
echo "building"
sudo docker build -t video_streaming .
sudo docker tag video_stream tushar2005d/video_stream
echo "pushing image"
sudo docker push tushar2005d/video_stream
