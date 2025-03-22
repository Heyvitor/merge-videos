from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import re
import os
import tempfile
import shutil
from moviepy.editor import VideoFileClip, concatenate_videoclips

app = FastAPI()

# Modelo para validar o corpo do POST
class VideoRequest(BaseModel):
    num_videos: int
    links: list[str]

# Função para extrair o ID do arquivo do link do Google Drive
def extract_file_id(link):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
    if match:
        return match.group(1)
    raise ValueError("Link inválido do Google Drive")

# Função para baixar um vídeo do Google Drive
def download_video(file_id, save_path):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        raise HTTPException(status_code=400, detail="Falha ao baixar o vídeo")

# Função para juntar os vídeos
def merge_videos(video_paths, output_path):
    clips = [VideoFileClip(path) for path in video_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264')

# Endpoint para juntar os vídeos
@app.post("/merge-videos")
async def merge_videos(request: VideoRequest):
    # Validar se o número de vídeos corresponde à quantidade de links
    if len(request.links) != request.num_videos:
        raise HTTPException(status_code=400, detail="Número de links não corresponde ao número de vídeos informado")

    # Criar diretório temporário
    temp_dir = tempfile.mkdtemp()
    video_paths = []

    try:
        # Baixar os vídeos
        for i, link in enumerate(request.links):
            file_id = extract_file_id(link)
            save_path = os.path.join(temp_dir, f"video_{i}.mp4")
            download_video(file_id, save_path)
            video_paths.append(save_path)

        # Juntar os vídeos
        output_path = os.path.join(temp_dir, "merged_video.mp4")
        merge_videos(video_paths, output_path)

        # Mover o arquivo para um local acessível
        final_path = "/tmp/merged_video.mp4"
        shutil.move(output_path, final_path)

        return {"download_link": "/download/merged_video.mp4"}
    finally:
        # Limpar o diretório temporário
        shutil.rmtree(temp_dir)

# Endpoint para baixar o vídeo resultante
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")