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

st.title("🎬 MATRIX AI: Editor de Elite V8")

with st.sidebar:
    st.header("⚙️ Ajustes Finais")
    cor_fonte = st.color_picker("Cor da Letra", "#FFFFFF")
    tamanho_fonte = st.slider("Tamanho da Letra", 20, 70, 35) # Reduzi o padrão para não cortar
    posicao_y_slider = st.slider("Altura (Y)", 0.6, 0.95, 0.8)

arquivo_video = st.file_uploader("📥 Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])

if arquivo_video:
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    col1, col2 = st.columns(2)
    with col1: st.info("Original"); st.video("temp_video.mp4")

    if st.button("🚀 RENDERIZAR VÍDEO PROFISSIONAL"):
        with st.spinner("🧠 IA MATRIX: Usando modelo de alta precisão..."):
            video = VideoFileClip("temp_video.mp4")
            
            # PASSO 1: MODELO 'SMALL' PARA PORTUGUÊS PRECISO
            modelo = whisper.load_model("small") # Troquei o 'base' pelo 'small'
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True, language='pt')
            
            # PASSO 2: CÁLCULO DE ÁREA SEGURA
            largura_segura = int(video.w * 0.8) 
            pos_y_pixel = int(video.h * posicao_y_slider)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    texto = palavra['word'].strip().upper()
                    
                    # PASSO 3: TEXTO SEM STROKE (BORDA) PARA NÃO CORTAR
                    # O Linux corta letras quando a borda é muito grossa
                    txt_clip = (TextClip(
                        text=texto, 
                        font_size=tamanho_fonte, 
                        color=cor_fonte,
                        method='label' # Ajuste automático ao texto
                    ).with_start(palavra['start'])
                     .with_end(palavra['end']))

                    # Se a palavra ainda for grande demais, reduzimos a escala
                    if txt_clip.w > largura_segura:
                        fator = largura_segura / txt_clip.w
                        txt_clip = txt_clip.with_display_aspect_ratio(fator)

                    txt_clip = txt_clip.with_position(('center', pos_y_pixel))
                    legendas.append(txt_clip)

            # RENDERIZAÇÃO
            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_matrix_v8.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            st.success("✅ Edição Concluída com Alta Precisão!")
            st.video(saida)
            with open(saida, "rb") as file:
                st.download_button("🔥 BAIXAR VÍDEO AGORA", file, "video_matrix_final.mp4")






