import streamlit as st
import os
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# --- FIX: DESTRAVAR IMAGEMAGICK NO STREAMLIT CLOUD ---
def fix_imagemagick():
    old_policy = "/etc/ImageMagick-6/policy.xml"
    new_policy = "/tmp/policy.xml"
    if os.path.exists(old_policy):
        with open(old_policy, "r") as f:
            content = f.read()
        # Remove a trava de segurança para leitura/escrita
        content = content.replace('rights="none" pattern="@*"', 'rights="read|write" pattern="@*"')
        with open(new_policy, "w") as f:
            f.write(content)
        os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp"

fix_imagemagick()
# ---------------------------------------------------

st.title("Matrix Editor IA 🎬")

# Carregador de Vídeo
video_file = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_file:
    # 1. Salva o vídeo fisicamente para o Whisper e MoviePy acharem
    with open("temp_video.mp4", "wb") as f:
        f.write(video_file.getbuffer())
    
    st.success("Vídeo carregado! Processando...")

    # 2. Carrega o modelo do Whisper
    @st.cache_resource
    def load_model():
        return whisper.load_model("base")

    modelo = load_model()

    # 3. Transcreve (Agora com FFmpeg garantido pelo packages.txt)
    with st.spinner("Transcrevendo áudio..."):
        resultado = modelo.transcribe(
            "temp_video.mp4",
            fp16=False,
            language="pt",
            initial_prompt="Este é um vídeo em português brasileiro, focado em alta retenção."
        )
    
    st.write("Texto detectado:", resultado["text"])

    # 4. Exemplo de Edição com MoviePy (Usando o ImageMagick destravado)
    if st.button("Gerar Clipe com Legenda"):
        clip = VideoFileClip("temp_video.mp4")
        
        # Criando uma legenda simples no centro
        txt_clip = TextClip(resultado["text"][:50], fontsize=70, color='yellow', font='Arial-Bold')
        txt_clip = txt_clip.set_pos('center').set_duration(clip.duration)
        
        video_final = CompositeVideoClip([clip, txt_clip])
        video_final.write_videofile("output_matrix.mp4", fps=24, codec="libx264")
        
        st.video("output_matrix.mp4")

