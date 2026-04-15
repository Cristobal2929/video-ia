import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

COMPONENTES = {
    "humor": [["La vida es un chiste.", "Reír es gratis.", "El mundo está loco."], ["¿Te has fijado que siempre pasa lo mismo?", "Lo peor es cuando intentas ser serio."], ["Es como cuando buscas las llaves y las tienes en la mano."], ["¡Relájate y disfruta!"]],
    "terror": [["La oscuridad te observa.", "Hay ruidos en el pasillo."], ["Nunca deberías haber abierto esa puerta.", "Las sombras se mueven."], ["Sientes una mano en tu hombro."], ["No cierres los ojos."]]
}

def generar_guion_unico(tema):
    t = tema.lower()
    tipo = "humor" if "humor" in t or "risa" in t else "terror" if "terror" in t or "miedo" in t else "general"
    if tipo in COMPONENTES:
        return " ".join([random.choice(grupo) for grupo in COMPONENTES[tipo]])
    return f"Descubre el fascinante mundo de {tema}. Una experiencia llena de sorpresas."

def transformar_srt(vtt, srt):
    try:
        def parse_t(t):
            p = t.split(':')
            return int(p[-3])*3600000 + int(p[-2])*60000 + int(float(p[-1].replace(',','.'))*1000)
        def format_t(ms):
            return f"{ms//3600000:02d}:{(ms%3600000)//60000:02d}:{(ms%60000)//1000:02d},{ms%1000:03d}"
        with open(vtt, 'r', encoding='utf-8') as f: lines = f.readlines()
        clean = [l for l in lines if "-->" in l or (l.strip() and not l.strip().isdigit() and not l.startswith("WEBVTT"))]
        srt_f, cnt = [], 1
        for i in range(0, len(clean), 2):
            if i+1 < len(clean) and "-->" in clean[i]:
                t = clean[i].split(" --> ")
                s, e = parse_t(t[0]), parse_t(t[1])
                palabras = re.sub(r'[.,;!¡¿?]', '', clean[i+1].strip()).upper().split()
                if not palabras: continue
                ms_p = (e - s) / len(palabras)
                for j in range(0, len(palabras), 2):
                    g = palabras[j:j+2]
                    srt_f.append(f"{cnt}\n{format_t(s+int(j*ms_p))} --> {format_t(s+int((j+len(g))*ms_p))}\n{' '.join(g)}\n")
                    cnt += 1
        with open(srt, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def buscar_vids(query, api_key, segs):
    busqueda = re.sub(r'quiero|un|video|de|sobre|hazme|haz|crea|largo|bastante', '', query.lower()).strip() or "abstract"
    url = f"https://api.pexels.com/videos/search?query={busqueda}&per_page=20&orientation=portrait"
    desc, acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
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

st.title("🎬 Fénix Studio Pro")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Probemos el nuevo motor de audio sin errores."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]):
            with open(msg["video"], "rb") as f: st.video(f.read())

if guion_in := st.chat_input("Dime el tema..."):
    st.session_state.mensajes.append({"role": "user", "content": guion_in})
    with st.chat_message("user"): st.markdown(guion_in)

    with st.chat_message("assistant"):
        with st.status("🎬 Produciendo...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            guion_txt = generar_guion_unico(guion_in)
            
            # 1. Voz
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion_txt}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
            
            # 2. Vídeos
            clips = buscar_vids(guion_in, pexels_key, dur)
            if clips:
                transformar_srt("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. Mezcla Final Robusta (Voz con audio normalizado)
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3\'" -c:v libx264 -preset superfast -shortest -pix_fmt yuv420p -c:a aac -b:a 128k "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ ¡Vídeo listo!", "video": v_final})
                    st.rerun()
                else: st.error("Fallo al crear el archivo final.")
            else: st.error("No se descargaron clips.")
