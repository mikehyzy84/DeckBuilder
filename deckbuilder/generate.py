"""Visual asset sourcing and generation.

Order of preference for every visual brief (see CLAUDE.md, Visuals):
  1. Native PowerPoint (chart, table, shapes, icons). Free, editable.
  2. Stock photo: Pexels, then Pixabay. Free, real photography.
  3. Runway image (gen4_image) for anything stock cannot supply.
  4. Runway image-to-video for short motion clips.
  5. Veo (Gemini API) for hero video.

Nothing in 3 to 5 runs without Mike approving the asset list and credit estimate.
Every asset written gets a sidecar <file>.json with source, prompt or query, license, and URL.
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import requests

UA = {"User-Agent": "DeckBuilder/0.1"}


def _key(*names: str) -> str:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    raise SystemExit(f"Missing API key. Set one of {', '.join(names)} in .env")


def _sidecar(path: Path, meta: dict) -> None:
    Path(str(path) + ".json").write_text(json.dumps(meta, indent=1))


def _download(url: str, out: Path, headers: dict | None = None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=headers or UA, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
    return out


# ---------------- stock photography ----------------

def pexels_search(query: str, orientation: str = "landscape", per_page: int = 10) -> list[dict]:
    r = requests.get("https://api.pexels.com/v1/search", timeout=30,
                     headers={"Authorization": _key("PEXELS_API_KEY"), **UA},
                     params={"query": query, "orientation": orientation, "per_page": per_page, "size": "large"})
    r.raise_for_status()
    return [{"source": "pexels", "id": p["id"], "url": p["src"]["original"], "preview": p["src"]["medium"],
             "width": p["width"], "height": p["height"], "alt": p.get("alt", ""),
             "photographer": p["photographer"], "page": p["url"], "license": "Pexels License"}
            for p in r.json().get("photos", [])]


def pixabay_search(query: str, orientation: str = "horizontal", per_page: int = 10) -> list[dict]:
    r = requests.get("https://pixabay.com/api/", timeout=30, headers=UA,
                     params={"key": _key("PIXABAY_API_KEY"), "q": query, "orientation": orientation,
                             "image_type": "photo", "per_page": max(3, per_page), "safesearch": "true"})
    r.raise_for_status()
    return [{"source": "pixabay", "id": h["id"], "url": h.get("largeImageURL"), "preview": h.get("webformatURL"),
             "width": h["imageWidth"], "height": h["imageHeight"], "alt": h.get("tags", ""),
             "photographer": h.get("user"), "page": h["pageURL"], "license": "Pixabay Content License"}
            for h in r.json().get("hits", [])]


def stock_search(query: str, n: int = 8) -> list[dict]:
    """Pexels first, Pixabay to fill. Returns candidates; Claude reviews previews before download."""
    out: list[dict] = []
    for fn in (pexels_search, pixabay_search):
        try:
            out += fn(query, per_page=n)
        except SystemExit:
            continue
        except requests.RequestException as e:  # never print the URL: Pixabay puts the key in it
            code = getattr(getattr(e, "response", None), "status_code", type(e).__name__)
            print(f"{fn.__name__} failed: {code}")
        if len(out) >= n:
            break
    return out[:n]


def stock_download(candidate: dict, out: Path) -> Path:
    _download(candidate["url"], out)
    _sidecar(out, candidate)
    return out


# ---------------- Runway ----------------

def _runway_headers(cfg: dict) -> dict:
    return {"Authorization": f"Bearer {_key('RUNWAY_API_KEY', 'RUNWAYML_API_SECRET')}",
            "X-Runway-Version": cfg["RUNWAY"]["api_version"], "Content-Type": "application/json"}


def _runway_wait(cfg: dict, task_id: str, timeout: int = 900) -> dict:
    base = cfg["RUNWAY"]["api_base"]
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f"{base}/tasks/{task_id}", headers=_runway_headers(cfg), timeout=30)
        r.raise_for_status()
        task = r.json()
        if task.get("status") == "SUCCEEDED":
            return task
        if task.get("status") in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Runway task {task_id} {task.get('status')}: {task.get('failure')}")
        time.sleep(5)
    raise TimeoutError(f"Runway task {task_id} did not finish in {timeout}s")


def _data_uri(path: str) -> str:
    p = Path(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def runway_image(cfg: dict, prompt: str, out: Path, ratio: str = "1920:1080") -> Path:
    base = cfg["RUNWAY"]["api_base"]
    body = {"model": cfg["RUNWAY"]["image_model"], "promptText": prompt, "ratio": ratio}
    r = requests.post(f"{base}/text_to_image", headers=_runway_headers(cfg), json=body, timeout=60)
    r.raise_for_status()
    task = _runway_wait(cfg, r.json()["id"])
    _download(task["output"][0], out)
    _sidecar(out, {"source": "runway", "model": body["model"], "prompt": prompt, "ratio": ratio, "task": task["id"]})
    return out


def runway_video(cfg: dict, prompt: str, out: Path, image: str | None, duration: int = 5, ratio: str = "1280:720") -> Path:
    if not image:
        raise SystemExit("Runway video needs a start frame (--image). Generate or source the still first.")
    base = cfg["RUNWAY"]["api_base"]
    img = image if image.startswith("http") else _data_uri(image)
    body = {"model": cfg["RUNWAY"]["video_model"], "promptImage": img, "promptText": prompt,
            "duration": duration, "ratio": ratio}
    r = requests.post(f"{base}/image_to_video", headers=_runway_headers(cfg), json=body, timeout=60)
    r.raise_for_status()
    task = _runway_wait(cfg, r.json()["id"])
    _download(task["output"][0], out)
    _sidecar(out, {"source": "runway", "model": body["model"], "prompt": prompt, "duration": duration,
                   "start_frame": image, "task": task["id"]})
    return out


# ---------------- Veo (Gemini API / AI Studio) ----------------

def veo_video(cfg: dict, prompt: str, out: Path, image: str | None = None) -> Path:
    from google import genai
    from google.genai import types
    vc = cfg["VEO"]
    if vc.get("provider") == "vertex":
        client = genai.Client(vertexai=True, project=_key("GOOGLE_CLOUD_PROJECT"), location=vc.get("vertex_location", "us-central1"))
    else:
        client = genai.Client(api_key=_key("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    kwargs = {"model": vc["model"], "prompt": prompt,
              "config": types.GenerateVideosConfig(aspect_ratio="16:9", number_of_videos=1)}
    if image:
        p = Path(image)
        kwargs["image"] = types.Image(image_bytes=p.read_bytes(), mime_type="image/png" if p.suffix == ".png" else "image/jpeg")
    op = client.models.generate_videos(**kwargs)
    while not op.done:
        time.sleep(10)
        op = client.operations.get(op)
    video = op.response.generated_videos[0].video
    out.parent.mkdir(parents=True, exist_ok=True)
    client.files.download(file=video)
    video.save(str(out))
    _sidecar(out, {"source": "veo", "model": vc["model"], "prompt": prompt, "start_frame": image})
    return out
