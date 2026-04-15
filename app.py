import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- HISTORIAS CON PALABRAS CLAVE PARA BÚSQUEDA ---
def crear_guion_y_keywords(tema):
    t = tema.lower()
    if "terror" in t or "miedo" in t:
        guion = "Todo empezó con un susurro que nadie más parecía escuchar en aquella casa abandonada. Pronto, una sombra alta empezó a aparecer al final del oscuro pasillo cada noche. Ahora entiendo que el bosque que rodea la mansión oculta secretos que nunca debieron ser descubiertos."
        # Lista de búsquedas ordenadas según el guion
        keywords = ["abandoned house", "creepy shadow", "dark hallway", "spooky forest", "scary mansion"]
        return guion, keywords
    elif "coche" in t:
        guion = "El motor rugió despertando la ciudad. Aceleré a fondo sintiendo la velocidad en la autopista mientras el sol se ponía. Este deportivo es la definición de potencia y libertad sobre el asfalto."
        keywords = ["engine car", "sports car speed", "highway driving", "sunset car", "supercar wheels"]
        return guion, keywords
    else:
        guion = f"Descubre los secretos de {tema}. Un viaje por los detalles más increíbles que definen este mundo. Una experiencia visual que no te dejará indiferente."
        keywords = [t, f"{t} details", f"{t} cinematic"]
        return guion, keywords

def transformar_srt(vtt_path, srt_path):
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

def buscar_vids_coherentes(keywords, api_key):
    desc = []
    headers = {"Authorization": api_key.strip()}
    for i, word in enumerate(keywords):
        url = f"https://api.pexels.com/videos/search?query={word}&per_page=1&orientation=portrait"
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                nombre = f"clip_{i}.mp4"
                with open(nombre, 'wb') as f: f.write(requests.get(v_url).content)
                desc.append(nombre)
        except: continue
    return desc

with st.sidebar:
    st.title("⚙️ Ajustes Pro")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

st.title("🎬 Fénix: Coherencia Visual")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]): st.video(msg["video"])

if user_input := st.chat_input("Dime el tema (ej: Terror)..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("🧠 Analizando guion y buscando imágenes que coincidan...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            
            # 1. Crear historia y lista de búsqueda
            guion, keys = crear_guion_y_keywords(user_input)
            
            # 2. Generar Voz
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            # 3. Descargar clips en orden (coherencia)
            clips = buscar_vids_coherentes(keys, pexels_key)
            
            if clips:
                transformar_srt("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # Mezcla final con tus subtítulos clásicos y voz potente
                est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest -c:a aac -af "volume=2.5" "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ ¡Vídeo coherente terminado!", "video": v_final})
                    st.rerun()
