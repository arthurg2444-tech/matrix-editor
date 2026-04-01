import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor V5", layout="wide")
st.title("🎬 Matrix Editor - Versão Estável")

# 1. Modelo 'small' para maior precisão nas palavras
@st.cache_resource
def load_whisper():
    return whisper.load_model("small")

modelo = load_whisper()

def criar_frame_legenda(texto, largura_video, altura_video):
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonte pequena (2.8% da altura)
    tamanho_fonte = int(altura_video * 0.028) 
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        font = ImageFont.load_default()

    linhas = textwrap.wrap(texto.upper(), width=20)
    
    # Posição no rodapé (88% para baixo)
    y_base = int(altura_video * 0.88)
    
    for linha in reversed(linhas):
        # CORREÇÃO DO ERRO DE TUPLE/FLOAT:
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (largura_video - w) / 2
        
        # Contorno Preto
        for off in [(-1,-1), (1,-1), (-1,1), (1,1)]:
            draw.text((x+off, y_base+off), linha, font=font, fill="black")
            
        # Texto Branco
        draw.text((x, y_base), linha, font=font, fill="white")
        y_base -= (h + 10) 
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_final.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    if st.button("🚀 Gerar Vídeo Final"):
        with st.spinner("IA Processando..."):
            try:
                # Transcrição precisa
                resultado = modelo.transcribe(
                    temp_path, 
                    language="pt", 
                    word_timestamps=True,
                    initial_prompt="Português brasileiro, termos do dia a dia."
                )
                
                clip_original = VideoFileClip(temp_path)
                clipe_final_lista = [clip_original]

                for seg in resultado['segments']:
                    palavras = seg['text'].strip().split()
                    if not palavras: continue
                    
                    # Agrupa de 2 em 2 palavras
                    num_grupos = max(1, len(palavras) // 2)
                    for i in range(0, len(palavras), 2):
                        trecho = " ".join(palavras[i:i+2])
                        
                        duracao_seg = seg['end'] - seg['start']
                        inicio_t = seg['start'] + (i / len(palavras)) * duracao_seg
                        fim_t = seg['start'] + (min(i+2, len(palavras)) / len(palavras)) * duracao_seg
                        
                        img_legenda = criar_frame_legenda(trecho, clip_original.w, clip_original.h)
                        
                        txt_clip = (ImageClip(img_legenda)
                                    .set_start(inicio_t)
                                    .set_duration(max(0.1, fim_t - inicio_t))
                                    .set_position(('center', 'center')))
                        
                        clipe_final_lista.append(txt_clip)

                video_final = CompositeVideoClip(clipe_final_lista)
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo", f, "matrix_final.mp4")

            except Exception as e:
                st.error(f"Erro detalhado: {str(e)}")


