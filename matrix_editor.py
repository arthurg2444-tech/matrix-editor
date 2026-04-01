import streamlit as st
import whisper
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# 1. Configuração Inicial
st.set_page_config(page_title="Matrix Editor", layout="wide")
st.title("🎬 Matrix Editor - Legendas Corrigidas")

# Carrega o modelo do Whisper (Cache para não travar o app)
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo = load_whisper()

# 2. Upload do Vídeo
video_postado = st.file_uploader("Suba seu vídeo aqui", type=["mp4", "mov", "avi"])

if video_postado:
    # Salva o arquivo temporário para o Whisper e MoviePy lerem
    with open("temp_video.mp4", "wb") as f:
        f.write(video_postado.getbuffer())

    if st.button("Gerar Legendas"):
        with st.spinner("Processando... Isso pode levar um minuto."):
            try:
                # 3. Transcrição com Whisper
                resultado = modelo.transcribe("temp_video.mp4")
                texto_final = resultado['text'].strip()

                # 4. Edição com MoviePy
                video = VideoFileClip("temp_video.mp4")
                
                # CONFIGURAÇÃO DA LEGENDA (CORRIGINDO O CORTE)
                txt_clip = TextClip(
                    texto_final,
                    fontsize=40,
                    color='yellow',
                    font='DejaVu-Sans-Bold', # Fonte padrão do servidor Streamlit
                    method='caption',        # Quebra de linha automática
                    size=(video.w * 0.8, None), # Largura de 80% (evita cortes laterais)
                    align='center'
                ).set_duration(video.duration).set_position(('center', video.h * 0.70)) # Sobe a legenda para 70% da altura

                # Junta o vídeo original com a legenda
                video_com_legenda = CompositeVideoClip([video, txt_clip])
                
                # Salva o resultado final
                output_path = "video_final.mp4"
                video_com_legenda.write_videofile(output_path, codec="libx264", audio_codec="aac")

                # 5. Exibição e Download
                st.success("Vídeo editado com sucesso!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button("Baixar Vídeo Legendado", file, "video_matrix.mp4")

            except Exception as e:
                st.error(f"Ocorreu um erro no processamento: {e}")
