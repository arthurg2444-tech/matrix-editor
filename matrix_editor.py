import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- CONFIGURAÇÃO PARA NUVEM ---
st.set_page_config(page_title="Matrix Editor Elite", layout="centered")

st.title("🎬 Matrix Editor: Legendas de Elite")
st.write("Suba seu vídeo e deixe a IA gerar as legendas dinâmicas.")

# --- COMPONENTE DE UPLOAD ---
arquivo_video = st.file_uploader("Escolha um vídeo (MP4)", type=["mp4", "mov", "avi"])

if arquivo_video:
    # Salva o vídeo temporariamente
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    st.video("temp_video.mp4")
    
    if st.button("🚀 Gerar Legendas Profissionais"):
        with st.spinner("🧠 IA Matrix analisando e renderizando..."):
            
            # Lógica do Editor
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True, fp16=False)
            video = VideoFileClip("temp_video.mp4")
            
            # Layout Adaptativo
            if video.w < video.h:
                largura, tam, pos_y = int(video.w * 0.8), int(video.w * 0.09), int(video.h * 0.75)
            else:
                largura, tam, pos_y = int(video.w * 0.6), int(video.h * 0.10), int(video.h * 0.85)

            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    # Removemos o caminho C: para usar a fonte padrão do servidor
                    txt_clip = (TextClip(
                        text=palavra['word'].strip().upper(), 
                        font_size=tam, 
                        color='white', 
                        stroke_color='black',
                        stroke_width=1.5,
                        method='caption',
                        size=(largura, None) 
                    ).with_start(palavra['start']).with_end(palavra['end']).with_position(('center', pos_y)))
                    legendas.append(txt_clip)

            video_final = CompositeVideoClip([video] + legendas)
            video_final.write_videofile("saida_matrix.mp4", codec="libx264", audio_codec="aac", fps=24)
            
            st.success("✅ Vídeo pronto!")
            with open("saida_matrix.mp4", "rb") as file:
                st.download_button("📥 Baixar Vídeo Editado", file, "video_matrix.mp4")









