import streamlit as st
import whisper
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Configuração da página
st.set_page_config(page_title="Matrix Editor", layout="wide")
st.title("🎬 Matrix Editor - Versão Estável")

# Carrega o modelo do Whisper
@st.cache_resource
def carregar_modelo():
    return whisper.load_model("base")

modelo = carregar_modelo()

video_postado = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_postado:
    # Salva o arquivo temporário no servidor
    with open("temp_video.mp4", "wb") as f:
        f.write(video_postado.getbuffer())

    if st.button("Gerar Vídeo com Legenda"):
        with st.spinner("Processando..."):
            try:
                # 1. Transcrição com Whisper
                resultado = modelo.transcribe("temp_video.mp4")
                texto_transcrito = resultado['text'].strip()

                # 2. Edição do Vídeo (Ajuste para não cortar legenda)
                video = VideoFileClip("temp_video.mp4")
                
                txt_clip = TextClip(
                    texto_transcrito,
                    fontsize=40,
                    color='yellow',
                    method='caption',
                    size=(int(video.w * 0.8), None)
                ).set_duration(video.duration).set_position(('center', int(video.h * 0.7)))

                # Junta o vídeo com a legenda
                final_video = CompositeVideoClip([video, txt_clip])
                output_path = "video_final.mp4"
                final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)

                # Exibe o resultado
                st.video(output_path)
                st.success("Vídeo pronto!")
                
                with open(output_path, "rb") as file:
                    st.download_button("Baixar Vídeo", file, "video_legendado.mp4")

            except Exception as e:
                st.error(f"Erro no processamento: {e}")
