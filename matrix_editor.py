import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- CONFIGURAÇÃO VISUAL PREMIUM (DARK MODE) ---
st.set_page_config(page_title="MATRIX AI | Dashboard Pro", page_icon="🎬", layout="wide")

# CSS para interface Profissional
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background-color: #00ff41; color: black; font-weight: bold; border: none;
        box-shadow: 0px 4px 15px rgba(0, 255, 65, 0.3);
    }
    .stButton>button:hover { background-color: #00cc33; color: white; }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    div[data-testid="stExpander"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("🎬 MATRIX AI: Video Editor Pro")
st.write("### O Editor de Elite para Criadores de Conteúdo")

# --- BARRA LATERAL (CONFIGURAÇÕES AVANÇADAS) ---
with st.sidebar:
    st.image("https://flaticon.com", width=100)
    st.header("⚙️ Painel de Controle")
    
    with st.expander("🎨 Estilo Visual", expanded=True):
        cor_fonte = st.color_picker("Cor do Texto", "#FFFFFF")
        tamanho_fonte = st.slider("Tamanho da Fonte", 20, 100, 45)
        posicao_y_slider = st.slider("Posição na Tela (Y)", 0.5, 0.95, 0.75)
    
    with st.expander("✂️ Inteligência de Corte"):
        remover_silencio = st.toggle("Remover Pausas (Beta)", value=True)
        agressividade = st.select_slider("Nível", options=["Leve", "Pro"])

# --- ÁREA DE TRABALHO ---
col_up, col_prev = st.columns([1, 1])

with col_up:
    st.write("### 📤 1. Importar Mídia")
    arquivo_video = st.file_uploader("Arraste seu vídeo bruto aqui", type=["mp4", "mov", "avi"])
    if arquivo_video:
        with open("temp_video.mp4", "wb") as f:
            f.write(arquivo_video.read())
        st.success("✅ Mídia pronta para processamento.")

with col_prev:
    st.write("### 📺 2. Preview do Original")
    if arquivo_video:
        st.video("temp_video.mp4")
    else:
        st.info("Aguardando upload de mídia...")

# --- PROCESSAMENTO ---
if arquivo_video:
    st.divider()
    if st.button("🚀 INICIAR RENDERIZAÇÃO DE ELITE"):
        progresso = st.progress(0, text="Iniciando Motores Matrix...")
        
        with st.spinner("🧠 IA em ação..."):
            video = VideoFileClip("temp_video.mp4")
            
            # 1. Transcrição
            progresso.progress(30, text="🧠 IA: Analisando fala e sincronia...")
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True)
            
            # 2. Legendas Dinâmicas (Correção de Corte)
            progresso.progress(60, text="🎨 Design: Aplicando camadas visuais...")
            largura_maxima = int(video.w * 0.8) # Trava em 80% da largura
            pos_y = int(video.h * posicao_y_slider)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    texto = palavra['word'].strip().upper()
                    
                    txt_clip = (TextClip(
                        text=texto, 
                        font_size=tamanho_fonte, 
                        color=cor_fonte, 
                        stroke_color='black',
                        stroke_width=1.5,
                        method='caption', # Garante que o texto caiba na caixa
                        size=(largura_maxima, None),
                        text_align='center'
                    ).with_start(palavra['start'])
                     .with_end(palavra['end'])
                     .with_position(('center', pos_y)))
                    
                    legendas.append(txt_clip)

            # 3. Finalização
            progresso.progress(90, text="🎬 Render: Exportando vídeo em alta definição...")
            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_matrix_final.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            progresso.progress(100, text="✅ Tudo pronto!")
            st.balloons()
            
            # --- ÁREA DE DOWNLOAD ---
            st.divider()
            st_col1, st_col2 = st.columns([2, 1])
            with st_col1:
                st.video(saida)
            with st_col2:
                st.write("### 🔥 Resultado Final")
                st.info("Seu vídeo foi otimizado para Reels, TikTok e Shorts.")
                with open(saida, "rb") as file:
                    st.download_button(
                        label="📥 BAIXAR AGORA",
                        data=file,
                        file_name="matrix_edit_pro.mp4",
                        mime="video/mp4"
                    )







