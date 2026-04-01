import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- INTERFACE DE LUXO ---
st.set_page_config(page_title="MATRIX AI | Final Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #00ff41; color: black; font-weight: bold; border: none; }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 MATRIX AI: Editor de Elite V9")

with st.sidebar:
    st.header("⚙️ Ajustes")
    cor_fonte = st.color_picker("Cor da Letra", "#FFFFFF")
    tamanho_fonte = st.slider("Tamanho", 20, 60, 30)
    posicao_y = st.slider("Altura", 0.6, 0.95, 0.8)

arquivo_video = st.file_uploader("📥 Arraste seu vídeo", type=["mp4", "mov", "avi"])

if arquivo_video:
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    if st.button("🚀 RENDERIZAR AGORA"):
        with st.spinner("🧠 IA MATRIX: Processando..."):
            video = VideoFileClip("temp_video.mp4")
            
            # MODELO BASE + PROMPT EM PORTUGUÊS (Rápido e Preciso)
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe(
                "temp_video.mp4", 
                word_timestamps=True, 
                language='pt',
                initial_prompt="Este é um vídeo em português brasileiro, focado em alta retenção."
            )
            
            largura_segura = int(video.w * 0.8)
            pos_y_pixel = int(video.h * posicao_y)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    # MÉTODO SEGURO: Sem bordas complexas para não bugar no Linux
                    txt_clip = (TextClip(
                        text=palavra['word'].strip().upper(), 
                        font_size=tamanho_fonte, 
                        color=cor_fonte,
                        method='label'
                    ).with_start(palavra['start']).with_end(palavra['end']))

                    if txt_clip.w > largura_segura:
                        txt_clip = txt_clip.with_display_aspect_ratio(largura_segura / txt_clip.w)

                    txt_clip = txt_clip.with_position(('center', pos_y_pixel))
                    legendas.append(txt_clip)

            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_final.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            st.success("✅ Edição Concluída!")
            st.video(saida)
            with open(saida, "rb") as file:
                st.download_button("🔥 BAIXAR AGORA", file, "video_final.mp4")




