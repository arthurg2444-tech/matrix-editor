import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- CONFIGURAÇÃO VISUAL DE ELITE ---
st.set_page_config(page_title="MATRIX AI | Editor de Elite", page_icon="🎬", layout="wide")

# CSS para deixar a interface "Dark & Premium"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #00ff41; color: black; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #00cc33; color: white; }
    .stProgress > div > div > div > div { background-color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 MATRIX AI: Video Editor Pro")
st.subheader("Transforme vídeos brutos em conteúdo de alta retenção em segundos.")

# --- BARRA LATERAL DE CONFIGURAÇÕES ---
with st.sidebar:
    st.header("⚙️ Ajustes de Edição")
    st.info("Personalize o estilo do seu vídeo abaixo.")
    
    # Opções de Legenda
    st.write("---")
    st.subheader("✍️ Estilo da Legenda")
    cor_fonte = st.color_picker("Cor do Texto", "#FFFFFF")
    tamanho_ajuste = st.slider("Tamanho da Fonte", 20, 100, 50)
    posicao_ajuste = st.slider("Posição Vertical (Y)", 0.5, 0.95, 0.80)
    
    # Opções de Corte
    st.write("---")
    st.subheader("✂️ Inteligência de Corte")
    remover_silencio = st.toggle("Remover Pausas Vazias", value=True)
    intensidade_corte = st.select_slider("Agressividade do Corte", options=["Leve", "Normal", "Ninja"])

# --- ÁREA PRINCIPAL ---
col_upload, col_preview = st.columns([1, 1])

with col_upload:
    st.write("### 📤 1. Upload do Vídeo")
    arquivo_video = st.file_uploader("Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])
    
    if arquivo_video:
        with open("temp_video.mp4", "wb") as f:
            f.write(arquivo_video.read())
        st.success("Vídeo carregado com sucesso!")

with col_preview:
    st.write("### 📺 2. Visualização Original")
    if arquivo_video:
        st.video("temp_video.mp4")
    else:
        st.info("Aguardando upload...")

# --- BOTÃO DE AÇÃO ---
if arquivo_video:
    st.write("---")
    if st.button("🚀 GERAR VÍDEO DE ALTA RETENÇÃO"):
        progresso = st.progress(0, text="Iniciando Motores Matrix...")
        
        with st.spinner("Processando..."):
            # Carregando Vídeo
            video = VideoFileClip("temp_video.mp4")
            largura_video = video.w
            altura_video = video.h
            
            # Passo 1: Transcrição IA
            progresso.progress(25, text="🧠 IA: Ouvindo e transcrevendo palavras...")
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True)
            
            # Passo 2: Gerar Clips de Texto
            progresso.progress(60, text="🎨 Design: Criando legendas dinâmicas...")
            
            # Cálculo de proporção para as legendas
            largura_max = int(largura_video * 0.8)
            pos_y = int(altura_video * posicao_ajuste)
            
            legendas = []
            for segmento in resultado['segments']:
                for palavra in segmento['words']:
                    txt_clip = (TextClip(
                        text=palavra['word'].strip().upper(), 
                        font_size=tamanho_ajuste, 
                        color=cor_fonte, 
                        stroke_color='black',
                        stroke_width=2,
                        method='caption',
                        size=(largura_max, None) 
                    ).with_start(palavra['start']).with_end(palavra['end']).with_position(('center', pos_y)))
                    legendas.append(txt_clip)
            
            # Passo 3: Renderização
            progresso.progress(85, text="🎬 Render: Finalizando exportação de elite...")
            video_final = CompositeVideoClip([video] + legendas)
            saida = "video_matrix_pro.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, logger=None)
            
            progresso.progress(100, text="✅ Edição concluída com sucesso!")
            
            # --- RESULTADO FINAL ---
            st.write("---")
            st.balloons()
            st.write("### 📥 3. Seu Vídeo de Elite está Pronto!")
            
            res_col1, res_col2 = st.columns([1, 1])
            with res_col1:
                st.video(saida)
            with res_col2:
                with open(saida, "rb") as file:
                    st.download_button(
                        label="🔥 BAIXAR AGORA",
                        data=file,
                        file_name="matrix_pro_edit.mp4",
                        mime="video/mp4"
                    )







