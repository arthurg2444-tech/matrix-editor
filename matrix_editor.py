# Mude apenas a parte do TextClip no seu código:
txt_clip = TextClip(
    texto_transcrito,
    fontsize=40,
    color='yellow',
    font='DejaVu-Sans-Bold', # Esta fonte SEMPRE funciona no Streamlit
    method='caption',
    size=(video.w * 0.8, None),
    align='center'
).set_duration(video.duration).set_position(('center', video.h * 0.75))


