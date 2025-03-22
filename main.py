from fastapi import FastAPI, HTTPException
from pytube import YouTube
import ffmpeg
import cv2
import os
from typing import List

app = FastAPI()

@app.post("/merge_videos")
async def merge_videos(urls: List[str]):
    video_files = []
    for url in urls:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        video_url = soup.find('video', {'id': 'player7'}).get('src')
        ffmpeg.input(video_url).output(f'{os.getcwd()}/{os.path.basename(video_url)}').run()
        video_files.append(f'{os.getcwd()}/{os.path.basename(video_url)}')

    output_file = f'{os.getcwd()}/output.mp4'
    (
        ffmpeg
        .input(*video_files)
        .output(output_file, vcodec='copy', acodec='aac')
        .run()
    )

    return {"url": f'/output.mp4'}