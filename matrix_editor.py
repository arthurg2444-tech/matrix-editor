import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor Sincronizado", layout="wide")
st.title("🎬 Matrix Editor - Legendas Curtas e Sincronizadas")

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

# Função para criar o frame da legenda pequena e elegante
def criar_frame_legenda(texto, largura_video, altura_video):
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tamanho da fonte menor para não poluir (4% da altura do vídeo)
    tamanho_fonte = int(altura_video * 0.045) 
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        font = ImageFont.load_default()

    # Quebra de linha curta (máximo 25 caracteres para não esticar)
    linhas = textwrap.wrap(texto, width=25)
    
    # Altura da legenda (Rodapé alto, 80% da tela)
    total_h = sum([draw.textbbox((0, 0), l, font=font)[3] for l in linhas]) + (len(linhas) * 10)
    y_text = int(altura_video * 0.8) - total_h
    
    for linha in linhas:
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (largura_video - w) / 2
        
        # Sombra preta para destacar o texto
        for off in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            draw.text((x+off[0], y_text+off[1]), linha, font=font, fill="black")
            
        # Texto Branco
        draw.text((x, y_text), linha, font=font, fill="white")
        y_text += h + 15
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_sincronizado.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    if st.button("🚀 Gerar Vídeo Sincronizado"):
        with st.spinner("IA Sincronizando cada palavra..."):
            try:
                # 1. Transcrição com segmentos (essencial para o tempo)
                resultado = modelo.transcribe(temp_path, language="pt", task="transcribe")
                clip_original = VideoFileClip(temp_path)
                
                # Lista para empilhar o vídeo + cada legenda no seu tempo
                clipe_final_lista = [clip_original]

                # 2. Criar cada legenda no tempo exato do Whisper
                for seg in resultado['segments']:
                    texto = seg['text'].strip().upper() # Texto em MAIÚSCULO fica melhor
                    inicio = seg['start']
                    fim = seg['end']
                    duracao = fim - inicio
                    
                    if duracao > 0:
                        # Cria a imagem da frase curta
                        img_legenda = criar_frame_legenda(texto, clip_original.w, clip_original.h)
                        
                        # Cria o clipe dessa frase que SÓ aparece entre 'inicio' e 'fim'
                        txt_clip = (ImageClip(img_legenda)
                                    .set_start(inicio)
                                    .set_duration(duracao)
                                    .set_pos('center'))
                        
                        clipe_final_lista.append(txt_clip)

                # 3. Renderização final
                video_final = CompositeVideoClip(clipe_final_lista)
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo Sincronizado", f, "matrix_final.mp4")

            except Exception as e:
                st.error(f"Erro: {str(e)}")


