from aiortc.rtcpeerconnection import (
    RTCPeerConnection,
    RTCSessionDescription,
    asyncio,
    uuid,
)
from flask import (
    Blueprint,
    send_from_directory,
    jsonify,
    render_template,
    request,
    Response,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user
from flask_socketio import emit
from werkzeug.utils import secure_filename
import os
from . import db, sock
from .models import Video
import logging
import json
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaStreamTrack
from aiohttp import web
import cv2
from av.video.frame import VideoFrame
import av

video = Blueprint("video", __name__)
ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()

VIDEO_FILE = "/home/tushar/video_Streaming/myapp/temp/SampleVideo_1280x720_1mb.mp4"


class VideoFileTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, file_path):
        super().__init__()
        self.file = av.open(file_path)
        self.video_stream = next(s for s in self.file.streams if s.type == "video")
        self.iterator = self.file.decode(video=0)

    async def recv(self):
        frame = next(self.iterator)
        return frame


def get_file_path(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return os.path.join(upload_folder, filename)


def create_local_tracks(play_from):
    if not os.path.exists(play_from):
        logging.error(f"Media file {play_from} does not exist")
        return None
    player = MediaPlayer(play_from)
    video = player.video
    if video:
        logging.info("Successfully created video track")
    else:
        logging.error("Failed to create video track")
    return video


@video.route("/offer", methods=["POST"])
async def handle_offer():
    offer_data = request.json
    logging.info(f"Received offer: {offer_data}")

    try:
        offer = RTCSessionDescription(sdp=offer_data["sdp"], type=offer_data["type"])
    except KeyError as e:
        logging.error(f"Invalid offer data: {e}")
        return jsonify({"error": "Invalid offer data"}), 400

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logging.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()

    @pc.on("track")
    def on_track(track):
        logging.info(f"Track {track.kind} received")
        if track.kind == "video":
            logging.info("Received video track. Adding our video track.")

    logging.info(f"Checking video file: {VIDEO_FILE}")
    if os.path.isfile(VIDEO_FILE):
        try:
            video_track = create_local_tracks(VIDEO_FILE)

            transceiver = pc.addTransceiver("video", direction="sendonly")

            transceiver.sender.replaceTrack(video_track)

            logging.info("Video track added to PeerConnection")
        except Exception as e:
            logging.error(f"Error adding video track: {e}")
            return jsonify({"error": "Failed to add video track"}), 500
    else:
        logging.error(f"Video file not found at {VIDEO_FILE}")
        return jsonify({"error": "Video file not found"}), 500

    logging.info("Setting remote description")
    await pc.setRemoteDescription(offer)

    logging.info("Creating answer")
    answer = await pc.createAnswer()

    logging.info("Setting local description")
    await pc.setLocalDescription(answer)

    response = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    logging.info(f"Sending answer: {response}")
    return jsonify(response)


@video.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        video_title = request.form.get("video_title")
        video_desc = request.form.get("video_desc")
        file = request.files.get("file")
        if file:
            filename = secure_filename(file.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext.lower() in current_app.config["UPLOAD_EXTENSIONS"]:
                    file_path = get_file_path(filename)
                    try:
                        # Ensure the upload folder exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        # Save the file
                        file.save(file_path)
                        # Create a new Video object
                        new_video = Video(
                            video_title=video_title,
                            video_desc=video_desc,
                            file_name=filename,
                            file_path=file_path,
                            user_id=current_user.id,
                        )
                        # Add to database and commit
                        db.session.add(new_video)
                        db.session.commit()
                        print("Upload successful")
                        return redirect(url_for("home.profile", video_id=new_video.id))
                    except Exception as e:
                        print(f"Error saving file: {e}")
                        return "Internal server error", 500
                else:
                    return "Invalid file extension", 400
            else:
                return "No file selected", 400
    return render_template("upload.html")


@video.route("/stream")
@login_required
def stream():
    return render_template("stream.html")


@sock.on("connect")
def on_connect():
    print("Client connected")


@sock.on("disconnect")
def on_disconnect():
    print("Client disconnected")


async def on_shutdown():
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
