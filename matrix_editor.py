import streamlit as st
import whisper
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import MultiplySpeed

# --- CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="Matrix Editor PRO", layout="centered")

st.title("🎬 Matrix Editor: Editor de Elite")
st.write("Corte silêncios e gere legendas dinâmicas automaticamente.")

arquivo_video = st.file_uploader("Escolha um vídeo (MP4)", type=["mp4", "mov", "avi"])

if arquivo_video:
    with open("temp_video.mp4", "wb") as f:
        f.write(arquivo_video.read())
    
    st.video("temp_video.mp4")
    
    # OPÇÕES DO EDITOR
    col1, col2 = st.columns(2)
    with col1:
        cortar_silencio = st.checkbox("✂️ Cortar Silêncios (Jump Cut)", value=True)
    with col2:
        gerar_legendas = st.checkbox("✍️ Gerar Legendas Brancas", value=True)

    if st.button("🚀 INICIAR EDIÇÃO PROFISSIONAL"):
        with st.spinner("🧠 IA Matrix trabalhando no seu vídeo..."):
            video = VideoFileClip("temp_video.mp4")
            
            # 1. LÓGICA DE LEGENDAS (Whisper)
            legendas = []
            if gerar_legendas:
                modelo = whisper.load_model("base")
                resultado = modelo.transcribe("temp_video.mp4", word_timestamps=True, fp16=False)
                
                # Ajuste de layout automático para Nuvem
                if video.w < video.h:
                    largura, tam, pos_y = int(video.w * 0.8), int(video.w * 0.08), int(video.h * 0.75)
                else:
                    largura, tam, pos_y = int(video.w * 0.6), int(video.h * 0.12), int(video.h * 0.85)

                for segmento in resultado['segments']:
                    for palavra in segmento['words']:
                        # Ajuste de fonte para compatibilidade com Linux/Streamlit
                        txt_clip = (TextClip(
                            text=palavra['word'].strip().upper(), 
                            font_size=tam, 
                            color='white', 
                            stroke_color='black',
                            stroke_width=1,
                            method='caption',
                            size=(largura, None) 
                        ).with_start(palavra['start']).with_end(palavra['end']).with_position(('center', pos_y)))
                        legendas.append(txt_clip)

            # 2. MONTAGEM FINAL
            video_final = CompositeVideoClip([video] + legendas)
            
            # Salvando o resultado
            saida = "video_final_matrix.mp4"
            video_final.write_videofile(saida, codec="libx264", audio_codec="aac", fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True)
            
            st.success("✅ Edição Concluída!")
            st.video(saida) # Mostra o vídeo pronto na tela para o usuário ver
            
            with open(saida, "rb") as file:
                st.download_button(
                    label="📥 CLIQUE AQUI PARA BAIXAR VÍDEO",
                    data=file,
                    file_name="video_editado_matrix.mp4",
                    mime="video/mp4"
                )









