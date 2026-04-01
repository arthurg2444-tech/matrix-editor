import streamlit as st
import whisper
import os
import re
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# 1. CORREÇÃO DE SEGURANÇA DO IMAGEMAGICK (Resolve o erro "policy.xml")
policy_path = "/etc/ImageMagick-6/policy.xml"
if not os.path.exists(policy_path):
    policy_path = "/etc/ImageMagick-7/policy.xml"

if os.path.exists(policy_path):
    with open(policy_path, "r") as f:
        policy_content = f.read()
    
    # Desativa a restrição de leitura/escrita para textos
    new_policy = re.sub(r'<policy domain="path" rights="none" pattern="@\*"\s?/>', 
                        '<policy domain="path" rights="read|write" pattern="@*"/>', 
                        policy_content)
    
    with open("/tmp/policy.xml", "w") as f:
        f.write(new_policy)
    
    os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp"

# 2. CONFIGURAÇÃO DO BINÁRIO
if os.path.exists("/usr/bin/convert"):
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# --- INÍCIO DO APP ---
st.set_page_config(page_title="Matrix Editor", layout="wide")
st.title("🎬 Matrix Editor - Versão Final")

@st.cache_resource
def carregar_modelo():
    return whisper.load_model("base")

modelo = carregar_modelo()

video_postado = st.file_uploader("Suba seu vídeo", type=["mp4", "mov", "avi"])

if video_postado:
    with open("temp_video.mp4", "wb") as f:
        f.write(video_postado.getbuffer())

    if st.button("Gerar Vídeo com Legenda"):
        with st.spinner("Processando..."):
            try:
                # Transcrição
                resultado = modelo.transcribe("temp_video.mp4")
                texto = resultado['text'].strip()

                video = VideoFileClip("temp_video.mp4")
                
                # LEGENDA CORRIGIDA (Amarela, Centralizada e sem cortes)
                txt_clip = TextClip(
                    texto,
                    fontsize=45,
                    color='yellow',
                    font='DejaVu-Sans-Bold',
                    method='caption',
                    size=(int(video.w * 0.8), None),
                    align='center'
                ).set_duration(video.duration).set_position(('center', int(video.h * 0.72)))

                final = CompositeVideoClip([video, txt_clip])
                output = "video_legendado.mp4"
                final.write_videofile(output, codec="libx264", audio_codec="aac", fps=video.fps)

                st.video(output)
                st.success("Sucesso!")
                
                with open(output, "rb") as file:
                    st.download_button("Baixar Vídeo", file, "matrix_final.mp4")

            except Exception as e:
                st.error(f"Erro: {e}")

