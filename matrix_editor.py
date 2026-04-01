import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- INTERFACE PREMIUM ---
st.set_page_config(page_title="MATRIX AI | Pro Editor", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #00ff41; color: black; font-weight: bold; }
    .stSidebar { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 MATRIX AI: Video Editor Pro")

# --- CONFIGURAÇÕES LATERAIS ---
with st.sidebar:
    st.header("⚙️ Ajustes de Elite")
    cor_fonte = st.color_picker("Cor do Texto", "#FFFFFF")
    tamanho_fonte = st.slider("Tamanho da Fonte", 30, 90, 55)
    posicao_y = st.slider("Posição (Y)", 0.5, 0.95, 0.80)

# --- ÁREA DE UPLOAD ---
arquivo_video = st.file_uploader("📥 Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])

if arquivo_video:
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    col1, col2 = st.columns(2)
    with col1: st.info("Preview Original"); st.video("temp_video.mp4")

    if st.button("🚀 GERAR VÍDEO EM PORTUGUÊS"):
        with st.spinner("🧠 IA MATRIX processando em Português..."):
            video = VideoFileClip("temp_video.mp4")
            
            # IA Transcrição FORÇANDO PORTUGUÊS
            modelo = whisper.load_model("base")
            # O segredo está aqui: language='pt'
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True, language='pt')
            
            largura_maxima = int(video.w * 0.85) # 85% da tela
            pos_y_pixel = int(video.h * posicao_y)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    texto_limpo = palavra['word'].strip().upper()
                    
                    # NOVO MÉTODO: Label + Margem de Segurança
                    txt_clip = (TextClip(
                        text=texto_limpo, 
                        font_size=tamanho_fonte, 
                        color=cor_fonte, 
                        stroke_color='black',
                        stroke_width=2,
                        method='label' # Label ajusta o tamanho ao texto
                    ).with_start(palavra['start'])
                     .with_end(palavra['end']))
                    
                    # Garante que se a palavra for gigante, ela reduza para caber nos 85%
                    if txt_clip.w > largura_maxima:
                        txt_clip = txt_clip.with_display_aspect_ratio(largura_maxima / txt_clip.w)
                        
                    txt_clip = txt_clip.with_position(('center', pos_y_pixel))
                    legendas.append(txt_clip)

            # Renderização
            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_final_pt.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            st.success("✅ Edição Concluída!")
            st.video(saida)
            with open(saida, "rb") as file:
                st.download_button("🔥 BAIXAR VÍDEO EDITADO", file, "matrix_editado.mp4")







