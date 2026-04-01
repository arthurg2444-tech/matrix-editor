import streamlit as st
import os
import whisper
import subprocess

# --- CONFIGURAÇÃO DE AMBIENTE ANTES DE IMPORTAR MOVIEPY ---
# Isso resolve o erro de "security policy" criando um arquivo de configuração local
os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp"

policy_xml = """<policymap>
  <policy domain="resource" name="memory" value="2GiB"/>
  <policy domain="resource" name="map" value="4GiB"/>
  <policy domain="resource" name="width" value="10KP"/>
  <policy domain="resource" name="height" value="10KP"/>
  <policy domain="path" rights="read|write" pattern="@*"/>
  <policy domain="coder" rights="read|write" pattern="{GIF,JPEG,PNG,WEBP,MP4}"/>
</policymap>"""

with open("/tmp/policy.xml", "w") as f:
    f.write(policy_xml)

# Agora sim importamos o MoviePy
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
# ---------------------------------------------------------

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

    try:
        resultado = modelo.transcribe(temp_path, fp16=False, language="pt")
        texto_transcrito = resultado["text"]
        st.success("Texto detectado!")
        st.text_area("Transcrição:", texto_transcrito)
    except Exception as e:
        st.error(f"Erro no Whisper: {e}")
        st.stop()

    if st.button("🚀 Gerar Vídeo"):
        with st.spinner("Renderizando..."):
            try:
                clip = VideoFileClip(temp_path)
                
                # Texto formatado para caber na tela
                txt = texto_transcrito[:100] + "..." if len(texto_transcrito) > 100 else texto_transcrito
                
                # IMPORTANTE: No Linux do Streamlit, use 'DejaVu-Sans' ou 'Liberation-Sans'
                txt_clip = TextClip(
                    txt, 
                    fontsize=35, 
                    color='yellow', 
                    font='DejaVu-Sans', 
                    method='caption',
                    size=(clip.w * 0.9, None)
                ).set_pos('center').set_duration(clip.duration)

                video_final = CompositeVideoClip([clip, txt_clip])
                video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button("📥 Baixar Vídeo", file, "matrix_video.mp4")
                    
            except Exception as e:
                st.error(f"Erro na edição: {str(e)}")

