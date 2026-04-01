import streamlit as st
import os
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Matrix Editor V7", layout="wide")
st.title("🎬 Matrix Editor - Versão Final Sem Erros")

@st.cache_resource
def load_whisper():
    # Modelo 'small' para evitar erros de português
    return whisper.load_model("small")

modelo = load_whisper()

def criar_frame_legenda(texto, largura_video, altura_video):
    # Cria tela transparente
    img = Image.new('RGBA', (largura_video, altura_video), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonte pequena (2.5% da altura)
    tamanho_fonte = int(altura_video * 0.025) 
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        font = ImageFont.load_default()

    # Quebra de linha curta (máximo 18 letras)
    texto_formatado = textwrap.fill(texto.upper(), width=18)
    
    # POSIÇÃO FIXA NO RODAPÉ (Ponto X central, Ponto Y a 90% da tela)
    # Usando 'anchor=mm' para centralizar sem precisar de cálculos manuais de tupla
    x_centro = largura_video / 2
    y_rodape = altura_video * 0.90
    
    # Desenha Contorno Preto (Stroke)
    for off_x in [-2, 0, 2]:
        for off_y in [-2, 0, 2]:
            draw.text((x_centro + off_x, y_rodape + off_y), texto_formatado, 
                      font=font, fill="black", anchor="mm", align="center")
            
    # Desenha Texto Branco por cima
    draw.text((x_centro, y_rodape), texto_formatado, 
              font=font, fill="white", anchor="mm", align="center")
        
    return np.array(img)

video_file = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_final.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    if st.button("🚀 Gerar Vídeo"):
        with st.spinner("IA Sincronizando palavras..."):
            try:
                # Transcrição precisa com marcação de tempo por palavra
                resultado = modelo.transcribe(
                    temp_path, 
                    language="pt", 
                    word_timestamps=True,
                    initial_prompt="Português brasileiro, legendas curtas e rápidas."
                )
                
                clip_original = VideoFileClip(temp_path)
                clipe_final_lista = [clip_original]

                for seg in resultado['segments']:
                    palavras = seg['text'].strip().split()
                    if not palavras: continue
                    
                    # Agrupa de 2 em 2 palavras para o vídeo ficar dinâmico
                    for i in range(0, len(palavras), 2):
                        trecho = " ".join(palavras[i:i+2])
                        
                        duracao_total = seg['end'] - seg['start']
                        inicio_t = seg['start'] + (i / len(palavras)) * duracao_total
                        fim_t = seg['start'] + (min(i+2, len(palavras)) / len(palavras)) * duracao_total
                        
                        img_legenda = criar_frame_legenda(trecho, clip_original.w, clip_original.h)
                        
                        txt_clip = (ImageClip(img_legenda)
                                    .set_start(inicio_t)
                                    .set_duration(max(0.1, fim_t - inicio_t))
                                    .set_position(('center', 'center'))) # Posicionado pelo PIL no rodapé
                        
                        clipe_final_lista.append(txt_clip)

                video_final = CompositeVideoClip(clipe_final_lista)
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Vídeo", f, "matrix_pro.mp4")

            except Exception as e:
                st.error(f"Erro: {str(e)}")


