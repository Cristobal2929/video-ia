import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- GENERADOR DE HISTORIAS CON LÓGICA (Inicio, Nudo, Fin) ---
def crear_historia_logica(tema):
    t = tema.lower()
    
    if "terror" in t or "miedo" in t:
        inicio = "Todo empezó con un susurro que nadie más parecía escuchar en la casa vacía."
        nudo = "Pero pronto, las puertas empezaron a cerrarse solas y una sombra alta y delgada empezó a aparecer al final del pasillo cada noche a las tres de la mañana."
        fin = "Ahora, atrapado en mi propia habitación, entiendo que el susurro no era una advertencia, sino una invitación para algo que ya está conmigo aquí dentro."
        return f"{inicio} {nudo} {fin}"
        
    elif "humor" in t or "risa" in t:
        inicio = "El otro día decidí ponerme en forma y me apunté al gimnasio más caro de la ciudad."
        nudo = "El primer día, intentando impresionar en la cinta de correr, tropecé con mis propios cordones y salí disparado hacia atrás, aterrizando encima de la tarta de cumpleaños del dueño."
        fin = "Ahora no solo no estoy en forma, sino que tengo prohibida la entrada y una deuda de quinientos euros por una tarta que ni siquiera probé."
        return f"{inicio} {nudo} {fin}"
        
    elif "coche" in t or "auto" in t:
        inicio = "El motor V8 rugió, despertando a todo el vecindario en la fría mañana de domingo."
        nudo = "Aceleré a fondo, sintiendo cómo los quinientos caballos de fuerza me pegaban al asiento mientras el asfalto se convertía en un borrón de velocidad y adrenalina pura."
        fin = "Al llegar a la cima de la montaña, con el sol naciendo en el horizonte, entendí que no era solo un coche, era la libertad absoluta en cuatro ruedas."
        return f"{inicio} {nudo} {fin}"
    
    else:
        # Historia genérica con lógica para cualquier otro tema
        return f"Bienvenidos al fascinante viaje para descubrir los secretos de {tema}. Empezaremos entendiendo sus orígenes ocultos para luego explorar cómo ha evolucionado y está cambiando nuestro mundo hoy en día. Al final de este vídeo, verás {tema} con unos ojos totalmente diferentes y entenderás por qué es tan crucial en nuestras vidas."

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
                # Dividimos el texto en palabras para que salgan de 2 en 2 (Tu estilo original)
                palabras = re.sub(r'[.,;!¡¿?]', '', clean[i+1].strip()).upper().split()
                if not palabras: continue
                
                duracion_total = e - s
                ms_por_palabra = duracion_total / len(palabras)
                
                for j in range(0, len(palabras), 2):
                    grupo = palabras[j:j+2]
                    inicio_g = s + int(j * ms_por_palabra)
                    fin_g = s + int((j + len(grupo)) * ms_por_palabra)
                    srt_f.append(f"{cnt}\n{format_t(inicio_g)} --> {format_t(fin_g)}\n{' '.join(grupo)}\n")
                    cnt += 1
        
        with open(srt_path, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def buscar_vids(query, api_key, segs):
    t = query.lower()
    busq = "horror creepy" if "terror" in t else "funny fails" if "humor" in t else "supercars" if "coche" in t else t
    url = f"https://api.pexels.com/videos/search?query={busq}&per_page=20&orientation=portrait"
    desc, acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10)
        vids = res.json().get('videos', [])
        random.shuffle(vids)
        for i, v in enumerate(vids):
            if acum >= segs + 10: break
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
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

st.title("🎬 Fénix Studio: Historias con Lógica")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! He mejorado las historias para que tengan sentido completo. Prueba con 'vídeo de terror' o 'vídeo de humor'."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg and os.path.exists(msg["video"]):
            with open(msg["video"], "rb") as f: st.video(f.read())

if guion_in := st.chat_input("Dime el tema..."):
    st.session_state.mensajes.append({"role": "user", "content": guion_in})
    with st.chat_message("user"): st.markdown(guion_in)

    with st.chat_message("assistant"):
        with st.status("🚀 Produciendo historia con lógica...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            
            # Generamos la historia estructurada (Inicio, Nudo, Fin)
            historia_final = crear_historia_logica(guion_in)
            
            # 1. Voz y Audio (Forzamos volumen alto)
            subprocess.run(f'edge-tts --voice {voz} --text "{historia_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
            
            # 2. Clips
            clips = buscar_vids(guion_in, pexels_key, dur)
            if clips:
                # Transformamos subtítulos al ESTILO ORIGINAL (2 palabras, grandes)
                transformar_srt_profesional("t.vtt", "t.srt")
                
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # 3. MEZCLA FINAL: Subtítulos Impact, Grandes, Centrales y Voz Potente
                est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_col},OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=140"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest -pix_fmt yuv420p -c:a aac -ac 1 -b:a 128k -af "volume=2.5" "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": f"✅ Vídeo de {round(dur)}s con historia lógica y subtítulos clásicos.", "video": v_final})
                    st.rerun()
