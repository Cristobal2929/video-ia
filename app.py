import streamlit as st
import os, time, random, subprocess, requests, math

st.set_page_config(page_title="Fénix Master", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def obtener_guion_pro(tema):
    try:
        prompt = f"Escribe una historia viral increible de 70 palabras sobre {tema}. Estructura: Gancho fuerte -> Datos reales -> Final sorprendente. TODO EN ESPAÑOL Y MAYUSCULAS. SIN SIGNOS DE PUNTUACION."
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=15).json()
        guion = res.get("reply", "").upper()
        if len(guion) < 50: raise Exception("IA falló")
        return guion
    except:
        return f"PRESTA MUCHA ATENCION PORQUE LO QUE TE VOY A CONTAR SOBRE {tema.upper()} ES UN SECRETO QUE HA SIDO GUARDADO DURANTE AÑOS. ESTO NO ES UNA COINCIDENCIA ES UN PLAN PERFECTO PARA OCULTAR LA VERDAD. SI TE QUEDAS HASTA EL FINAL DESCUBRIRAS ALGO QUE CAMBIARA TU FORMA DE VER EL MUNDO PARA SIEMPRE. SIGUENOS PARA MAS VERDADES."

# EL FIX DEFINITIVO: Cambiamos la coma por un punto para que Python no crashee
def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.') # <--- LA MAGIA ESTÁ AQUÍ
    partes = t_str.split(':')
    if len(partes) == 3: 
        h, m, s = partes
        return float(h)*3600 + float(m)*60 + float(s)
    elif len(partes) == 2: 
        m, s = partes
        return float(m)*60 + float(s)
    else: 
        return float(partes[0])

st.title("🦅 Fénix Studio: Sistema Profesional")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema y yo haré el resto..."):
    with st.status("🎬 Producción Profesional en curso...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion = obtener_guion_pro(user_input)
        status.write("✍️ Guion Maestro generado.")
        
        # 1. AUDIO Y TIEMPOS
        status.write("🎙️ Grabando voz y calculando tiempos al milisegundo...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        dur_audio = float(dur_audio_str)
        
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency=65:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.3[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. FILTRO DE SUBTÍTULOS BLINDADO
        drawtext_filters = []
        try:
            with open('t.vtt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    tiempos = lines[i].strip().split(" --> ")
                    start = time_to_sec(tiempos[0])
                    end = time_to_sec(tiempos[1])
                    if i + 1 < len(lines):
                        texto = lines[i+1].strip().replace("'", "").replace('"', '')
                        if texto:
                            drawtext_filters.append(f"drawtext=text='{texto}':fontcolor={color_sub}:fontsize=50:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})'")
            
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except Exception as e:
            st.error(f"Error detallado en subtítulos: {e}")
            st.stop()

        # 3. ESCENAS MATEMÁTICAS (Ritmo rápido y cero cortes)
        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        palabras_claves = [p for p in guion.split() if len(p) > 5]
        random.shuffle(palabras_claves)
        last_valid_clip = None
        
        status.write(f"🎞️ Reuniendo {num_clips} escenas para cubrir el audio...")
        for i in range(num_clips): 
            k = palabras_claves[i % len(palabras_claves)] if palabras_claves else user_input
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=1&orientation=portrait"
            try:
                res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=8).json()
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                last_valid_clip = f"p_{i}.mp4"
            except:
                if last_valid_clip:
                    subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=480x854:d={clip_duration}:r=25 -c:v libx264 -preset superfast p_{i}.mp4', shell=True)
            
            processed_clips.append(f"p_{i}.mp4")

        # 4. EL CIERRE (El truco para que NO se corte el vídeo)
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)

        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 5. RENDERIZADO FINAL
        status.write("✨ Exportando Master...")
        v_final = f"output/v_{int(time.time())}.mp4"
        
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success(f"🔥 VÍDEO PERFECTO DE {int(dur_audio)}s. CERO CORTES.")
            st.balloons()
        else:
            st.error("Error crítico en el renderizado final.")
