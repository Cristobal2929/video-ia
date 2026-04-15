import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Ultra", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def crear_guion_pro(tema, es_largo):
    t = tema.lower()
    if "terror" in t:
        return "La oscuridad te observa. Hay ruidos en el pasillo que no puedes explicar. Algo se mueve bajo tu cama esperando el momento exacto para atrapar tu tobillo. No cierres los ojos."
    elif "humor" in t:
        return "La vida es un chiste constante. ¿Por qué buscamos el móvil con la linterna del móvil encendida? Somos expertos en complicarnos la vida de la forma más tonta posible. ¡Ríete un poco!"
    return f"Bienvenidos al mundo de {tema}. Un lugar lleno de secretos y momentos increíbles que estamos a punto de descubrir juntos."

def buscar_vids(query, api_key, segs):
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

st.title("🎬 Fénix Studio Ultra")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]): st.video(msg["video"])

if guion_in := st.chat_input("¿Qué vídeo hacemos?"):
    st.session_state.mensajes.append({"role": "user", "content": guion_in})
    with st.chat_message("user"): st.markdown(guion_in)

    with st.chat_message("assistant"):
        with st.status("🚀 Editando vídeo...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            
            # 1. Voz rápida
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{crear_guion_pro(guion_in, True)}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
            
            # 2. Clips rápidos
            clips = buscar_vids(guion_in, pexels_key, dur)
            if clips:
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. Mezcla final (Voz potente + Subtítulos Impact)
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.vtt:force_style=\'Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140\'" -c:v libx264 -preset ultrafast -shortest -c:a aac "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ ¡Hecho!", "video": v_final})
                    st.rerun()
