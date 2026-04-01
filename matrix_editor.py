import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- DESIGN DE ELITE ---
st.set_page_config(page_title="MATRIX AI PRO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ff41; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 MATRIX AI: Video Editor Pro")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Personalização")
    cor_fonte = st.color_picker("Cor do Texto", "#FFFFFF")
    tamanho_fonte = st.slider("Tamanho da Legenda", 20, 80, 40)
    posicao_y_slider = st.slider("Altura da Legenda", 0.5, 0.9, 0.8)

# --- CONTEÚDO ---
arquivo_video = st.file_uploader("📥 Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])

if arquivo_video:
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    col1, col2 = st.columns(2)
    with col1: st.info("Vídeo Original"); st.video("temp_video.mp4")
    
    if st.button("🚀 GERAR VÍDEO DE ALTA RETENÇÃO"):
        with st.spinner("🧠 IA MATRIX processando..."):
            video = VideoFileClip("temp_video.mp4")
            
            # IA Transcrição
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True)
            
            # Configuração de Layout para não cortar
            largura_maxima = int(video.w * 0.8) # Margem de 10% em cada lado
            pos_y = int(video.h * posicao_y_slider)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    texto = palavra['word'].strip().upper()
                    
                    # Criação da legenda com largura fixa para evitar corte
                    txt_clip = (TextClip(
                        text=texto, 
                        font_size=tamanho_fonte, 
                        color=cor_fonte, 
                        stroke_color='black',
                        stroke_width=1.5,
                        method='caption', # Isso força o texto a caber na largura
                        size=(largura_maxima, None),
                        text_align='center'
                    ).with_start(palavra['start'])
                     .with_end(palavra['end'])
                     .with_position(('center', pos_y)))
                    
                    legendas.append(txt_clip)

            # Renderização Final
            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_matrix_pro.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            st.success("✅ Edição Concluída!")
            st.video(saida)
            with open(saida, "rb") as file:
                st.download_button("🔥 BAIXAR AGORA", file, "matrix_pro.mp4", "video/mp4")








