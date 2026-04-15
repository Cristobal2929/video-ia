import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def crear_guion(tema):
    t = tema.lower()
    if "terror" in t: return "La oscuridad te observa desde el rincón de tu habitación. No estás solo, aunque el silencio diga lo contrario. Siente el frío recorriendo tu espalda mientras algo se acerca lentamente. No mires atrás."
    if "humor" in t: return "La vida es ese chiste que te cuenta el destino cuando menos te lo esperas. ¿Por qué buscamos las gafas teniéndolas puestas? Somos un desastre andante, ¡pero al menos nos lo pasamos bien!"
    return f"Bienvenidos a este vídeo sobre {tema}. Prepárate para descubrir algo que te dejará sin palabras. Una experiencia visual y sonora diseñada para impactar."

def buscar_videos(query, api_key, segs):
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    desc, acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10)
        vids = res.json().get('videos', [])
        random.shuffle(vids)
        for i, v in enumerate(vids):
            if acum >= segs + 5: break
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            desc.append(f"clip_{i}.mp4")
            acum += v.get('duration', 8)
        return desc
    except: return []

with st.sidebar:
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

st.title("🎬 Fénix Studio: Audio Fix")

if "mensajes" not in st.session_state: st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg: st.video(msg["video"])

if user_input := st.chat_input("Dime el tema..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("🚀 Procesando vídeo y audio...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            texto = crear_guion(user_input)
            
            # 1. Generar Voz (Cambiamos a Alvaro que suele ser más estable en audio)
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{texto}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            # 2. Descargar y preparar vídeos
            clips = buscar_videos(user_input, pexels_key, 15)
            if clips:
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. MEZCLA FINAL: Forzamos audio AAC, 1 canal (mono) y volumen alto
                # El comando -af "volume=3.0" triplica el sonido para que se oiga sí o sí.
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.vtt:force_style=\'Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140\'" -c:v libx264 -preset ultrafast -shortest -c:a aac -ac 1 -ar 44100 -af "volume=3.0" "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ Vídeo listo con audio mejorado.", "video": v_final})
                    st.rerun()
