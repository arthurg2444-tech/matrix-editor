import streamlit as st
import os
import whisper
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# =======================================================
# FIX: DESTRAVAR IMAGEMAGICK NO STREAMLIT CLOUD
# =======================================================
def fix_imagemagick():
    old_policy = "/etc/ImageMagick-6/policy.xml"
    new_policy = "/tmp/policy.xml"
    if os.path.exists(old_policy):
        with open(old_policy, "r") as f:
            content = f.read()
        # Altera a permissão de 'none' para 'read|write'
        content = content.replace('rights="none" pattern="@*"', 'rights="read|write" pattern="@*"')
        with open(new_policy, "w") as f:
            f.write(content)
        # Informa ao sistema para usar a nova política configurada
        os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp"

fix_imagemagick()
# =======================================================

st.set_page_config(page_title="Matrix Editor IA", layout="wide")
st.title("🎬 Matrix Editor IA - Edição Automática")

# 1. Carregamento do Modelo Whisper (Cache para não baixar toda vez)
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

# 2. Upload do Vídeo
video_file = st.file_uploader("Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_file:
    # Caminho temporário absoluto
    temp_path = os.path.join(os.getcwd(), "temp_video.mp4")
    output_path = os.path.join(os.getcwd(), "video_editado.mp4")

    # Salva o arquivo no disco
    with open(temp_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    st.info("Vídeo carregado com sucesso! Iniciando processamento...")

    # 3. Transcrição com Whisper
    with st.spinner("🤖 IA Transcrevendo áudio..."):
        try:
            resultado = modelo.transcribe(
                temp_path, 
                fp16=False, 
                language="pt",
                initial_prompt="Vídeo em português brasileiro, alta retenção."
            )
            texto_transcrito = resultado["text"]
            st.success("Transcrição concluída!")
            st.text_area("Texto Detectado:", texto_transcrito, height=100)
        except Exception as e:
            st.error(f"Erro na transcrição: {e}")
            st.stop()

    # 4. Edição com MoviePy
    if st.button("🚀 Gerar Vídeo com Legenda Matrix"):
        with st.spinner("🎬 Renderizando edição..."):
            try:
                clip = VideoFileClip(temp_path)
                
                # Criando a legenda centralizada (Exemplo de 50 caracteres)
                txt = texto_transcrito[:60] + "..." if len(texto_transcrito) > 60 else texto_transcrito
                
                # Configuração do Texto (Usa ImageMagick via policy.xml corrigida)
                txt_clip = TextClip(
                    txt, 
                    fontsize=50, 
                    color='yellow', 
                    font='Arial-Bold',
                    method='caption',
                    size=(clip.w*0.8, None)
                ).set_pos('center').set_duration(clip.duration)

                # Overlay do texto no vídeo original
                video_final = CompositeVideoClip([clip, txt_clip])
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                # Exibe o vídeo final
                st.video(output_path)
                
                # Botão de Download
                with open(output_path, "rb") as file:
                    st.download_button("📥 Baixar Vídeo Editado", file, "matrix_final.mp4")
                    
            except Exception as e:
                st.error(f"Erro na edição de vídeo: {e}")

