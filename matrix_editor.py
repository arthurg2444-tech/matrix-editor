import streamlit as st
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

# Configuração da página
st.set_page_config(page_title="Matrix Editor Elite", layout="wide")
st.title("🎬 Matrix Editor - Legendas Automáticas")

# Carrega o modelo do Whisper (base é rápido e bom)
@st.cache_resource
def load_model():
    return whisper.load_model("base")

modelo = load_model()

video_postado = st.file_uploader("Upload do Vídeo", type=["mp4", "mov", "avi"])

if video_postado:
    # 1. Salva o vídeo temporariamente
    with open("temp_video.mp4", "wb") as f:
        f.write(video_postado.getbuffer())

    if st.button("Gerar Vídeo com Legenda"):
        with st.spinner("Transcrevendo e Editando..."):
            # 2. Transcrição
            resultado = modelo.transcribe("temp_video.mp4", initial_prompt="Vídeo em português brasileiro, alta retenção.")
            
            # 3. Edição do Vídeo
            video = VideoFileClip("temp_video.mp4")
            
            # CONFIGURAÇÃO DA LEGENDA (CORREÇÃO DO CORTE)
            def gerar_legenda(txt):
                return TextClip(
                    txt,
                    fontsize=40,
                    color='yellow',
                    font='Arial-Bold',
                    method='caption',      # Quebra linha automático
                    size=(video.w * 0.8, None), # Largura de 80% do vídeo (evita corte lateral)
                    align='center'
                ).set_duration(video.duration).set_position(('center', video.h * 0.75)) # Posição a 75% da altura (sobe a legenda)

            # Criando o clipe de texto com o resultado do Whisper
            texto_transcrito = resultado['text'].strip()
            txt_clip = gerar_legenda(texto_transcrito)

            # Sobreposição
            final_video = CompositeVideoClip([video, txt_clip])
            final_video.write_videofile("video_legendado.mp4", codec="libx264", audio_codec="aac")

            # Exibe o resultado
            st.success("Pronto!")
            st.video("video_legendado.mp4")
            
            with open("video_legendado.mp4", "rb") as file:
                st.download_button("Baixar Vídeo Legendado", file, "video_final.mp4")




