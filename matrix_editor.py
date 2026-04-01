import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor V3", layout="wide")
st.title("🎬 Matrix Editor - Legendas Curtas (Estilo Reels)")

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

def criar_frame_legenda(texto, largura_video, altura_video):
    # Cria imagem transparente do tamanho total do vídeo
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonte MENOR (3.5% da altura) para não ocupar a tela toda
    tamanho_fonte = int(altura_video * 0.035) 
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        font = ImageFont.load_default()

    # Quebra de linha MUITO CURTA (Max 15 caracteres)
    linhas = textwrap.wrap(texto.upper(), width=15)
    
    # POSIÇÃO FIXA NO RODAPÉ (80% para baixo)
    # Calculamos de baixo para cima para garantir que fique no rodapé
    y_base = int(altura_video * 0.85)
    
    for linha in reversed(linhas):
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (largura_video - w) / 2
        
        # Contorno Preto Grosso para legibilidade
        for off in [(-3,-3), (3,-3), (-3,3), (3,3), (0,3), (0,-3), (3,0), (-3,0)]:
            draw.text((x+off[0], y_base+off[1]), linha, font=font, fill="black")
            
        # Texto Branco
        draw.text((x, y_base), linha, font=font, fill="white")
        y_base -= (h + 15) # Sobe para a próxima linha (se houver)
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_final.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    if st.button("🚀 Gerar Vídeo"):
        with st.spinner("Sincronizando frases curtas..."):
            try:
                # Transcrição com precisão de tempo
                resultado = modelo.transcribe(temp_path, language="pt", word_timestamps=True)
                clip_original = VideoFileClip(temp_path)
                
                clipe_final_lista = [clip_original]

                # Percorre os segmentos e CRIA SUB-SEGMENTOS se a frase for longa
                for seg in resultado['segments']:
                    texto_completo = seg['text'].strip()
                    palavras = texto_completo.split()
                    
                    # Agrupa de 3 em 3 palavras para a legenda ser rápida e pequena
                    for i in range(0, len(palavras), 3):
                        trecho = " ".join(palavras[i:i+3])
                        
                        # Distribui o tempo do segmento proporcionalmente entre as palavras
                        duracao_total = seg['end'] - seg['start']
                        inicio_trecho = seg['start'] + (i / len(palavras)) * duracao_total
                        fim_trecho = seg['start'] + ((i+3) / len(palavras)) * duracao_total
                        if fim_trecho > seg['end']: fim_trecho = seg['end']

                        img_legenda = criar_frame_legenda(trecho, clip_original.w, clip_original.h)
                        
                        txt_clip = (ImageClip(img_legenda)
                                    .set_start(inicio_trecho)
                                    .set_duration(fim_trecho - inicio_trecho)
                                    .set_position(('center', 'center'))) # PIL já posicionou no rodapé
                        
                        clipe_final_lista.append(txt_clip)

                video_final = CompositeVideoClip(clipe_final_lista)
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo", f, "matrix_final.mp4")

            except Exception as e:
                st.error(f"Erro: {str(e)}")


