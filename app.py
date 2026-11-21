"""Flask layer for japanese-output. Parses requests, calls japanese_output, saves state.

Run:  python app.py   then open http://127.0.0.1:5000
"""

import json
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from japanese_output import state as st
from japanese_output import storage

ROOT = Path(__file__).resolve().parent
AUDIO_EXT = {"audio/webm": ".webm", "audio/ogg": ".ogg", "audio/mp4": ".m4a", "audio/mpeg": ".mp3"}


def create_app(data_file=None, recordings_dir=None):
    app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # room for an hour of audio
    data_file = Path(data_file or ROOT / "data" / "user.json")
    rec_dir = Path(recordings_dir or ROOT / "recordings")

    def today():
        return date.today()

    def respond(s, **extra):
        body = st.summary(s, today())
        storage.save(data_file, s)  # summary may have created today's plan
        body.update(extra)
        return jsonify(body)

    @app.errorhandler(ValueError)
    def bad_request(err):
        return jsonify({"error": str(err)}), 400

    @app.errorhandler(HTTPException)
    def http_error(err):
        return jsonify({"error": err.description}), err.code

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/state")
    def get_state():
        return respond(storage.load(data_file))

    @app.post("/api/level")
    def set_level():
        s = storage.load(data_file)
        st.set_level(s, (request.get_json(silent=True) or {}).get("level"), today())
        return respond(s)

    @app.post("/api/unlock")
    def unlock():
        s = storage.load(data_file)
        st.unlock_topic(s, (request.get_json(silent=True) or {}).get("topic_id"))
        return respond(s)

    @app.post("/api/session")
    def finish_session():
        s = storage.load(data_file)
        form = request.form
        try:
            seconds = int(float(form.get("seconds", "0")))
            grammar_used = json.loads(form.get("grammar_used") or "[]")
            words = json.loads(form.get("words") or "[]")
        except (TypeError, ValueError):
            raise ValueError("bad session data")
        if not isinstance(grammar_used, list) or not isinstance(words, list):
            raise ValueError("bad session data")
        words = [w for w in words if isinstance(w, dict) and isinstance(w.get("word"), str)]

        recording = None
        audio = request.files.get("audio")
        if audio:
            mime = (audio.mimetype or "").split(";")[0]
            rec_dir.mkdir(parents=True, exist_ok=True)
            recording = datetime.now().strftime("%Y%m%d-%H%M%S") + AUDIO_EXT.get(mime, ".webm")
            audio.save(rec_dir / recording)

        result = st.finish_session(
            s, today(), seconds=seconds, grammar_used=grammar_used, words=words,
            recording=recording, source=(form.get("source") or "").strip() or None,
        )
        return respond(s, result=result)

    @app.get("/api/sessions")
    def sessions():
        s = storage.load(data_file)
        return jsonify(list(reversed(s["sessions"])))

    @app.get("/recordings/<path:name>")
    def recording(name):
        return send_from_directory(rec_dir, name)

    return app


if __name__ == "__main__":
    print("japanese-output running at http://127.0.0.1:5000  (Ctrl+C to stop)")
    create_app().run(host="127.0.0.1", port=5000)
