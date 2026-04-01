import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor Pro", layout="wide")
st.title("🎬 Matrix Editor - Legendas Dinâmicas")

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

# Função para criar o frame da legenda (Visual profissional)
def criar_frame_legenda(texto, largura_video, altura_video):
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tamanho da fonte menor (ajustado para legendas)
    tamanho_fonte = int(altura_video * 0.05) 
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        font = ImageFont.load_default()

    # Quebra de linha automática
    import textwrap
    linhas = textwrap.wrap(texto, width=35)
    
    # Posiciona no rodapé (85% da altura do vídeo)
    y_text = int(altura_video * 0.85)
    
    for linha in linhas:
        # Calcula largura para centralizar
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (largura_video - w) / 2
        
        # Contorno preto (Stroke) para legibilidade total
        for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            draw.text((x+offset[0], y_text+offset[1]), linha, font=font, fill="black")
            
        # Texto Branco (estilo Netflix/YouTube)
        draw.text((x, y_text), linha, font=font, fill="white")
        y_text += h + 10
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_final_matrix.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    if st.button("🚀 Gerar Vídeo com Legendas Dinâmicas"):
        with st.spinner("IA Processando e Sincronizando..."):
            try:
                # 1. Transcrição detalhada com marcação de tempo (SEGMENTOS)
                resultado = modelo.transcribe(temp_path, verbose=False, language="pt")
                clip_original = VideoFileClip(temp_path)
                
                lista_legendas = []
                lista_legendas.append(clip_original)

                # 2. Criar um clipe de texto para cada frase dita
                for segmento in resultado['segments']:
                    inicio = segmento['start']
                    fim = segmento['end']
                    texto = segmento['text'].strip()

                    # Gera a imagem da legenda para este tempo específico
                    img_legenda = criar_frame_legenda(texto, clip_original.w, clip_original.h)
                    
                    # Cria o clipe dessa frase
                    txt_clip = (ImageClip(img_legenda)
                                .set_start(inicio)
                                .set_duration(fim - inicio)
                                .set_pos('center'))
                    
                    lista_legendas.append(txt_clip)

                # 3. Junta tudo
                video_final = CompositeVideoClip(lista_legendas)
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo Editado", f, "matrix_editado.mp4")

            except Exception as e:
                st.error(f"Erro na edição: {str(e)}")


