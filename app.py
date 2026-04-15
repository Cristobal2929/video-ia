import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- MATRIZ DE FRASES ---
COMPONENTES = {
    "humor": [
        ["La vida es un chiste.", "Reír es gratis.", "El mundo está loco."],
        ["¿Te has fijado que siempre pasa lo mismo?", "Lo peor es cuando intentas ser serio.", "Nada sale como uno planea."],
        ["Es como cuando buscas las llaves y las tienes en la mano.", "O cuando saludas a alguien que no conoces por error.", "Incluso el GPS se ríe de nosotros a veces."],
        ["¡Relájate y disfruta!", "Si no te ríes, pierdes.", "Mañana será más divertido."]
    ],
    "terror": [
        ["La oscuridad te observa.", "Hay ruidos en el pasillo.", "El frío recorre tu espalda."],
        ["Nunca deberías haber abierto esa puerta.", "Las sombras se mueven solas.", "El silencio es lo más peligroso."],
        ["Sientes una mano en tu hombro.", "Una cara aparece en el cristal.", "Ya es demasiado tarde para huir."],
        ["No cierres los ojos.", "Ellos ya están aquí.", "Dulces sueños."]
    ]
}

def generar_guion_unico(tema):
    tema = tema.lower()
    tipo = "humor" if "humor" in tema or "risa" in tema else "terror" if "terror" in tema or "miedo" in tema else "coche"
    if tipo in COMPONENTES:
        return " ".join([random.choice(grupo) for grupo in COMPONENTES[tipo]])
    return f"Descubre el mundo de {tema}. Una experiencia única llena de detalles fascinantes."

def transformar_srt_profesional(vtt_path, srt_path):
    try:
        def parse_t(t):
            p = t.split(':')
            return int(p[-3])*3600000 + int(p[-2])*60000 + int(float(p[-1].replace(',','.'))*1000)
        def format_t(ms):
            return f"{ms//3600000:02d}:{(ms%3600000)//60000:02d}:{(ms%60000)//1000:02d},{ms%1000:03d}"
        with open(vtt_path, 'r', encoding='utf-8') as f: lines = f.readlines()
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
        with open(srt_path, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def buscar_y_descargar_dinamico(query, api_key, segundos_totales):
    busqueda = re.sub(r'quiero|un|video|de|sobre|hazme|haz|crea|largo|bastante', '', query.lower()).strip()
    url = f"https://api.pexels.com/videos/search?query={busqueda}&per_page=20&orientation=portrait"
    descargados, segundos_acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        videos = res.json().get('videos', [])
        random.shuffle(videos)
        for i, v in enumerate(videos):
            if segundos_acum >= segundos_totales + 10: break
            link = v['video_files'][0]['link']
            nombre = f"clip_{i}.mp4"
            with open(nombre, 'wb') as f: f.write(requests.get(link).content)
            descargados.append(nombre)
            segundos_acum += v.get('duration', 8)
        return descargados, busqueda
    except: return [], "error"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    musica_on = st.checkbox("🎵 Música de Fondo", value=True)
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix Studio Pro (Con Audio)")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Ahora mis vídeos tienen música épica de fondo. ¡Pruébalo!"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f: st.video(f.read())

# --- LÓGICA PRINCIPAL ---
if user_input := st.chat_input("Dime el tema del vídeo..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        guion_final = generar_guion_unico(user_input)
        with st.status("🎬 Generando producción con música...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            
            # 1. Generar Voz
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            cmd_dur = f"ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'"
            dur_audio = float(subprocess.check_output(cmd_dur, shell=True))
            
            # 2. Descargar Vídeos
            clips, tema_det = buscar_y_descargar_dinamico(user_input, pexels_key, dur_audio)
            
            if clips:
                transformar_srt_profesional("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. Descargar Música (Ejemplo: Epic Music)
                if musica_on:
                    m_url = "https://www.bensound.com/bensound-music/bensound-epic.mp3"
                    r_m = requests.get(m_url)
                    with open("musica.mp3", "wb") as f: f.write(r_m.content)
                    
                    # MEZCLA DE AUDIO: Voz fuerte + Música bajita
                    cmd_mix = f'ffmpeg -y -i base.mp4 -i t.mp3 -i musica.mp3 -filter_complex "[1:a]volume=2.0[v];[2:a]volume=0.1,afade=t=in:ss=0:d=2,afade=t=out:st={dur_audio-2}:d=2[m];[v][m]amix=inputs=2:duration=first" -vf "subtitles=t.srt:force_style=\'Fontname=Impact,FontSize=28,PrimaryColour={ass_color},Outline=3\'" -c:v libx264 -preset superfast -shortest -c:a aac "{v_final}"'
                else:
                    cmd_mix = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'Fontname=Impact,FontSize=28,PrimaryColour={ass_color},Outline=3\'" -c:v libx264 -preset superfast -shortest -c:a aac "{v_final}"'
                
                subprocess.run(cmd_mix, shell=True)
                
                st.session_state.mensajes.append({"role": "assistant", "content": f"✅ ¡Vídeo con música listo!", "video": v_final})
                st.rerun()
