import streamlit as st
import os
import whisper
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# =======================================================
# FIX DEFINITIVO: DESTRAVAR IMAGEMAGICK E FONTES
# =======================================================
def fix_imagemagick():
    # 1. Localiza a política de segurança
    policy_path = "/etc/ImageMagick-6/policy.xml"
    if os.path.exists(policy_path):
        with open(policy_path, "r") as f:
            content = f.read()
        
        # Força a permissão de leitura e escrita
        new_content = content.replace('rights="none" pattern="@*"', 'rights="read|write" pattern="@*"')
        
        # Salva a nova política na pasta temporária
        with open("/tmp/policy.xml", "w") as f:
            f.write(new_content)
        
        # Avisa ao sistema para usar essa nova política
        os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp"

fix_imagemagick()
# =======================================================

st.set_page_config(page_title="Matrix Editor IA", layout="wide")
st.title("🎬 Matrix Editor IA")

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

video_file = st.file_uploader("Suba seu vídeo", type=["mp4", "mov", "avi"])

if video_file:
    temp_path = "temp_video.mp4"
    output_path = "video_editado.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    st.info("Processando transcrição...")

    # Transcrição
    try:
        resultado = modelo.transcribe(temp_path, fp16=False, language="pt")
        texto_transcrito = resultado["text"]
        st.success("Texto detectado!")
    except Exception as e:
        st.error(f"Erro no Whisper: {e}")
        st.stop()

    if st.button("🚀 Gerar Vídeo"):
        with st.spinner("Renderizando..."):
            try:
                clip = VideoFileClip(temp_path)
                
                # LIMITA O TEXTO E MUDA A FONTE (Usando 'DejaVu-Sans-Bold' que é padrão no Linux)
                txt = texto_transcrito[:80] + "..." if len(texto_transcrito) > 80 else texto_transcrito
                
                txt_clip = TextClip(
                    txt, 
                    fontsize=40, 
                    color='yellow', 
                    font='DejaVu-Sans-Bold', # FONTE SEGURA PARA LINUX
                    method='caption',
                    size=(clip.w * 0.8, None)
                ).set_pos('center').set_duration(clip.duration)

                video_final = CompositeVideoClip([clip, txt_clip])
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button("📥 Baixar Vídeo", file, "matrix_video.mp4")
                    
            except Exception as e:
                st.error(f"Erro na edição: {e}")
