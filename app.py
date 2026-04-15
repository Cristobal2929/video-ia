import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Ultra", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- GENERADOR DE GUIONES CREATIVOS ---
def crear_guion_pro(tema, es_largo):
    t = tema.lower()
    if "terror" in t or "miedo" in t:
        cuerpo = "Dicen que el miedo es solo una reacción química, pero quienes han sentido una mirada en la nuca cuando están solos saben que hay algo más. Sombras que se mueven más rápido que la luz y susurros que no deberían existir. No cierres los ojos, porque en la oscuridad, tú eres el invitado de algo que no quiere que te vayas jamás."
    elif "humor" in t or "risa" in t:
        cuerpo = "La vida es corta, pero parece eterna cuando estás en una fila que no avanza. ¿Por qué compramos cosas que no necesitamos con dinero que no tenemos para impresionar a gente que no nos cae bien? Somos expertos en tropezar con la misma piedra y luego pedirle perdón a la piedra. ¡Relájate, que si el mundo se acaba mañana, al menos que nos pille riendo!"
    elif "coche" in t or "auto" in t:
        cuerpo = "No es solo metal y gasolina; es el rugido que hace vibrar tu pecho y la sensación de que el horizonte es tuyo. La ingeniería llevada al límite para convertir el asfalto en tu propio escenario. Velocidad, diseño y esa libertad que solo sientes cuando el motor y tú sois uno solo."
    else:
        cuerpo = f"Bienvenidos al fascinante universo de {tema}. Un lugar donde cada detalle revela una verdad oculta y cada imagen nos transporta a una realidad que pocos llegan a comprender de verdad. Quédate con nosotros y descubre por qué esto está cambiando el mundo tal como lo conocemos."
    
    return cuerpo if es_largo else cuerpo[:150] + "..."

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
                ms_p = (e - s) / max(len(palabras), 1)
                for j in range(0, len(palabras), 2):
                    g = palabras[j:j+2]
                    srt_f.append(f"{cnt}\n{format_t(s+int(j*ms_p))} --> {format_t(s+int((j+len(g))*ms_p))}\n{' '.join(g)}\n")
                    cnt += 1
        with open(srt, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def buscar_vids(query, api_key, segs):
    t = query.lower()
    busq = "horror creepy" if "terror" in t else "funny fails" if "humor" in t else "supercars" if "coche" in t else t
    url = f"https://api.pexels.com/videos/search?query={busq}&per_page=20&orientation=portrait"
    desc, acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        vids = res.json().get('videos', [])
        random.shuffle(vids)
        for i, v in enumerate(vids):
            if acum >= segs + 10: break
            r = requests.get(v['video_files'][0]['link'])
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(r.content)
            desc.append(f"clip_{i}.mp4")
            acum += v.get('duration', 8)
        return desc
    except: return []

with st.sidebar:
    st.title("⚙️ Ajustes Pro")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-MX-JorgeNeural", "es-ES-AlvaroNeural"])

st.title("🎬 Fénix Studio Ultra")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! He mejorado los guiones y el audio. Prueba con 'vídeo largo de terror' o 'vídeo de humor'."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]):
            with open(msg["video"], "rb") as f: st.video(f.read())

if guion_in := st.chat_input("Dime el tema o escribe tu propio guion largo..."):
    st.session_state.mensajes.append({"role": "user", "content": guion_in})
    with st.chat_message("user"): st.markdown(guion_in)

    with st.chat_message("assistant"):
        with st.status("🚀 Produciendo obra maestra...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            es_largo = any(p in guion_in.lower() for p in ["bastante", "largo", "minuto"])
            
            # Guion inteligente si es corto, si no, usamos el del usuario
            texto_final = crear_guion_pro(guion_in, es_largo) if len(guion_in) < 60 else guion_in
            
            # 1. Audio y Música
            subprocess.run(f'edge-tts --voice {voz} --text "{texto_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
            
            # Descargamos una pista de música genérica segura
            musica_url = "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3"
            with open("bg.mp3", "wb") as f: f.write(requests.get(musica_url).content)
            
            # 2. Clips
            clips = buscar_vids(guion_in, pexels_key, dur)
            if clips:
                transformar_srt("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. MEZCLA FINAL CON MÚSICA Y VOZ POTENTE
                est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -i bg.mp3 -filter_complex "[1:a]volume=2.5[v];[2:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest -pix_fmt yuv420p -c:a aac -b:a 128k "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": f"✅ ¡Vídeo terminado! Tema: {guion_in}", "video": v_final})
                    st.rerun()
