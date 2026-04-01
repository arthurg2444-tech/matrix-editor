import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor IA", layout="wide")
st.title("🎬 Matrix Editor IA (Versão Sem Erros)")

# 1. Carregar Whisper
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

# Função para criar a legenda usando Pillow (evita o erro do ImageMagick)
def criar_legenda_pil(texto, largura_video, altura_video):
    # Cria uma imagem transparente
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tenta carregar uma fonte padrão do Linux, se falhar usa a básica
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Quebra o texto para caber na tela
    import textwrap
    linhas = textwrap.wrap(texto, width=40)
    y_text = altura_video // 2
    
    for linha in linhas:
        # Desenha contorno preto para ler melhor
        bbox = draw.textbbox((0, 0), linha, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (largura_video - w) / 2
        
        # Sombra/Contorno
        draw.text((x-2, y_text-2), linha, font=font, fill="black")
        draw.text((x+2, y_text+2), linha, font=font, fill="black")
        # Texto Amarelo
        draw.text((x, y_text), linha, font=font, fill="yellow")
        y_text += h + 10
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_editado.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    st.info("Processando transcrição...")
    resultado = modelo.transcribe(temp_path, fp16=False, language="pt")
    texto_transcrito = resultado["text"]
    st.success("Texto detectado!")

    if st.button("🚀 Gerar Vídeo"):
        with st.spinner("Renderizando com tecnologia anti-erro..."):
            try:
                clip = VideoFileClip(temp_path)
                
                # Criar a imagem da legenda com Pillow
                legenda_array = criar_legenda_pil(texto_transcrito, clip.w, clip.h)
                
                # Transforma a imagem do Pillow em um clip do MoviePy
                legenda_clip = ImageClip(legenda_array).set_duration(clip.duration).set_pos('center')

                video_final = CompositeVideoClip([clip, legenda_clip])
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo", f, "video_final.mp4")
            except Exception as e:
                st.error(f"Erro: {str(e)}")


