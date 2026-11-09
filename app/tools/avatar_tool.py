# app/tools/avatar_tool.py
"""
D-ID Talking Avatar Engine for F.R.I.D.A.Y.
Generates a real lip-synced talking head video from TTS audio using D-ID API.
Falls back gracefully to static frame lip-sync if D-ID is unavailable.
"""

import os
import time
import requests
from app.config import config

DID_API_KEY = os.getenv("DID_API_KEY", "")
DID_API_URL = "https://api.d-id.com"

# Your FRIDAY face image — host this on any public URL or use D-ID's image upload
FRIDAY_FACE_URL = os.getenv("FRIDAY_FACE_URL", "")


def _get_headers():
    import base64
    token = base64.b64encode(f"{DID_API_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }


def generate_talking_avatar(audio_path: str, output_path: str = "") -> str:
    """
    Sends FRIDAY's TTS audio to D-ID and gets back a lip-synced talking head video.
    Returns path to the output video file, or empty string on failure.
    """
    if not DID_API_KEY or not FRIDAY_FACE_URL:
        return ""

    if not os.path.exists(audio_path):
        return ""

    try:
        # Step 1: Upload audio to D-ID
        with open(audio_path, "rb") as f:
            upload_resp = requests.post(
                f"{DID_API_URL}/audios",
                headers={"Authorization": _get_headers()["Authorization"]},
                files={"audio": (os.path.basename(audio_path), f, "audio/mpeg")}
            )
        if upload_resp.status_code not in (200, 201):
            return ""

        audio_url = upload_resp.json().get("url", "")
        if not audio_url:
            return ""

        # Step 2: Create talk request
        payload = {
            "source_url": FRIDAY_FACE_URL,
            "script": {
                "type": "audio",
                "audio_url": audio_url
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0,
                "stitch": True
            }
        }

        create_resp = requests.post(
            f"{DID_API_URL}/talks",
            headers=_get_headers(),
            json=payload
        )
        if create_resp.status_code not in (200, 201):
            return ""

        talk_id = create_resp.json().get("id", "")
        if not talk_id:
            return ""

        # Step 3: Poll for completion (max 15s)
        for _ in range(15):
            time.sleep(1)
            status_resp = requests.get(
                f"{DID_API_URL}/talks/{talk_id}",
                headers=_get_headers()
            )
            data = status_resp.json()
            if data.get("status") == "done":
                video_url = data.get("result_url", "")
                if not video_url:
                    return ""

                # Step 4: Download video
                out_path = output_path or os.path.join(
                    os.environ.get("TEMP", "."),
                    f"friday_avatar_{talk_id[:8]}.mp4"
                )
                video_data = requests.get(video_url).content
                with open(out_path, "wb") as vf:
                    vf.write(video_data)
                return out_path

            elif data.get("status") == "error":
                return ""

    except Exception as e:
        print(f"[D-ID Avatar Error] {e}")

    return ""
