from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    num_videos: int
    links: List[str]

def download_video(link, save_path):
    response = requests.get(link, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

@app.post("/merge-videos")
async def merge_videos_endpoint(request: VideoRequest):
    if len(request.links) != request.num_videos:
        raise HTTPException(status_code=400, detail="Number of links does not match number of videos")

    # Download videos from links
    video_paths = []
    for i, link in enumerate(request.links):
        save_path = f"/tmp/video_{i}.mp4"
        download_video(link, save_path)
        video_paths.append(save_path)

    # Merge videos
    output_path = "/tmp/output.mp4"
    merge_videos(video_paths, output_path)
    return {"message": "Videos merged successfully", "output": output_path}