import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Ultra", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- MATRIZ DE HISTORIAS Y BÚSQUEDA ---
def crear_guion_y_keywords(tema):
    t = tema.lower()
    if "terror" in t or "miedo" in t:
        guion = "Todo empezó con un susurro en aquella casa abandonada. Una sombra alta apareció al final del pasillo. El bosque oculta secretos que nunca debieron ser descubiertos."
        keys = ["abandoned house creepy", "creepy shadow spooky", "dark hallway horror", "spooky forest night"]
        return guion, keys
    elif "coche" in t or "auto" in t:
        guion = "El motor rugió despertando la ciudad. Aceleré a fondo sintiendo la velocidad en la autopista. Este deportivo es la definición de potencia y libertad."
        keys = ["sports car speed", "highway driving car", "car engine roaring", "supercar wheels close"]
        return guion, keys
    else:
        guion = f"Descubre los secretos de {tema}. Un viaje por los detalles más increíbles que definen este mundo. Una experiencia visual que no te dejará indiferente."
        keys = [f"{t} cinematic", f"{t} details", f"{t} atmosphere"]
        return guion, keys

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
        url = f"https://api.pexels.com/videos/search?query={word}&per_page=3&orientation=portrait"
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get('videos'):
                v_url = random.choice(res['videos'])['video_files'][0]['link']
                nombre = f"clip_{i}.mp4"
                with open(nombre, 'wb') as f: f.write(requests.get(v_url).content)
                desc.append(nombre)
        except: continue
    return desc

# --- NUEVA FUNCIÓN: CREAR OUTRO (Sello CapCut) ---
def crear_outro_profesional(output_filename):
    # Crea un vídeo negro de 3 segundos con el texto FÉNIX STUDIO que aparece con fade
    cmd_outro = (
        'ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=30 '
        '-vf "drawtext=fontfile=/system/fonts/Roboto-Bold.ttf:text=\'FÉNIX STUDIO\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2:alpha=\'if(lt(t,0.5),t/0.5,if(lt(t,2.5),1,1-(t-2.5)/0.5))\',drawtext=fontfile=/system/fonts/Roboto-Bold.ttf:text=\'🦅\':fontcolor=white:fontsize=60:x=(w-tw)/2:y=(h-th)/2+80:alpha=\'if(lt(t,0.5),t/0.5,if(lt(t,2.5),1,1-(t-2.5)/0.5))\',fade=t=out:st=2.5:d=0.5" '
        '-c:v libx264 -preset ultrafast -pix_fmt yuv420p -an '
        + output_filename
    )
    subprocess.run(cmd_outro, shell=True)

with st.sidebar:
    st.title("⚙️ Ajustes Pro")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-MX-JorgeNeural", "es-ES-AlvaroNeural"])

st.title("🎬 Fénix Studio: Outro Final")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]): st.video(msg["video"])

# --- LÓGICA PRINCIPAL ---
if user_input := st.chat_input("Dime el tema (ej: Terror)..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("🧠 Analizando y montando con Sello Final...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            guion, keys = crear_guion_y_keywords(user_input)
            
            # 1. Generar Voz
            subprocess.run(f'edge-tts --voice {voz} --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            cmd_dur = f"ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'"
            dur_audio = float(subprocess.check_output(cmd_dur, shell=True))
            
            # 2. Descargar clips coherentes
            clips = buscar_vids_coherentes(keys, pexels_key)
            
            if clips:
                transformar_srt("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    # Forzamos fps=30 para coincidir con el outro
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                
                # CREAMOS EL OUTRO FINAL DE 3 SEGUNDOS
                crear_outro_profesional("outro_raw.mp4")
                clips.append("outro_raw.mp4")
                
                with open("lista.txt", "w") as f:
                    for i in range(len(clips) - 1): f.write(f"file 'p_{i}.mp4'\n")
                    f.write("file 'outro_raw.mp4'\n")
                
                # Unimos todos los clips de Pexels MÁS el Outro
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # MEZCLA FINAL CON MÚSICA DE FONDO (Mezcla de bensound)
                # He añadido música de fondo genérica para darle ambiente y que el outro no sea soso.
                musica_url = "https://www.bensound.com/bensound-music/bensound-betterdays.mp3"
                with open("bg.mp3", "wb") as f: f.write(requests.get(musica_url).content)
                
                est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
                # Mezclamos Voz (t.mp3) + Música (bg.mp3) y lo pegamos al vídeo (base.mp4 que ya incluye el outro)
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -i bg.mp3 -filter_complex "[1:a]volume=2.5[v];[2:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first,afade=t=out:st={dur_audio+1}:d=1" -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -pix_fmt yuv420p -c:a aac -b:a 128k "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ ¡Vídeo con Sello Fénix terminado!", "video": v_final})
                    st.rerun()
                else: st.error("Fallo al crear el vídeo final.")
            else: st.error("No se descargaron clips.")
