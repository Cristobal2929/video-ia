import streamlit as st
import os, time, random, subprocess, requests, math, re

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# 1. CEREBRO EXPANSOR (Tú das la idea, el bot construye el mega-prompt)
def obtener_guion_pro(orden_usuario):
    # Limpiamos tu orden para sacar de qué va el tema y buscar imágenes
    palabras = [p for p in orden_usuario.lower().split() if len(p) > 3 and p not in ["hazme", "video", "quiero", "sobre", "historia"]]
    tema_limpio = " ".join(palabras) if palabras else orden_usuario
    keys = [f"{p} cinematic" for p in palabras] + ["epic mystery", "documentary dark", "cinematic footage"]
    
    # EL MEGA-PROMPT: El bot le explica a la IA cómo expandir tu idea
    prompt_maestro = f"Eres el mejor guionista de TikTok. El jefe te ha dado esta idea muy basica: '{orden_usuario}'. TU TAREA: Coge esta idea simple y CONVIERTELA en una historia completa, fascinante y detallada. (Ejemplo: si te pide 'piramides', tu inventa un misterio epico sobre las piramides de Egipto con datos reales). ESTRUCTURA: 1. Gancho brutal. 2. Desarrollo profundo con contexto historico o cientifico. 3. Final impactante. REGLAS: MINIMO 120 PALABRAS. ESCRIBE TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. SOLO PALABRAS."

    guion_fallback = f"EL SISTEMA HA DETECTADO UN MISTERIO INCREIBLE SOBRE {tema_limpio.upper()} LA VERDAD ESTA OCULTA A PLENA VISTA DURANTE DECADAS NOS HAN MENTIDO Y HOY VAMOS A DESENTRAÑAR LA LOGICA DETRAS DE ESTE SUCESO PRESTA ATENCION PORQUE CUANDO DESCUBRAS EL SECRETO FINAL TU FORMA DE VER EL MUNDO CAMBIARA PARA SIEMPRE SIGUENOS"

    try:
        url = "https://sentence.fineshopdesign.com/api/ai"
        res = requests.get(url, params={"prompt": prompt_maestro, "seed": random.randint(1, 100000)}, timeout=15).json()
        guion = res.get("reply", "").upper()
        
        # Limpieza absoluta de signos de puntuación
        guion = re.sub(r'[^\w\s]', '', guion)
        guion = guion.replace('\n', ' ').strip()
        
        if len(guion) < 50: raise Exception("IA generó texto muy corto")
        return guion, keys, tema_limpio
    except:
        return guion_fallback, keys, tema_limpio

def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.')
    partes = t_str.split(':')
    if len(partes) == 3: 
        h, m, s = partes
        return float(h)*3600 + float(m)*60 + float(s)
    elif len(partes) == 2: 
        m, s = partes
        return float(m)*60 + float(s)
    else: 
        return float(partes[0])

st.title("🦅 Fénix Studio: Expansor de Ideas")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

# Ahora solo tienes que darle una idea suelta
if orden := st.chat_input("Dame una idea básica (Ej: 'vídeo de las pirámides' o 'fantasmas'):"):
    with st.status("🎬 Expandiendo tu idea y creando historia...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_limpio = obtener_guion_pro(orden)
        status.write(f"✍️ El bot transformó tu idea en una historia completa sobre: {tema_limpio}.")
        
        # 1. AUDIO (-10% velocidad)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        
        tono = 70
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. SUBTÍTULOS INTELIGENTES
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
                        texto = lines[i+1].strip()
                        if texto:
                            palabras = texto.split()
                            chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
                            
                            total_letras = sum(len(c) for c in chunks)
                            current_time = start
                            
                            for chunk in chunks:
                                duracion_chunk = (len(chunk) / total_letras) * (end - start) if total_letras > 0 else (end - start)
                                c_end = current_time + duracion_chunk
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{current_time},{c_end})'")
                                current_time = c_end
                                
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except:
            st.stop()

        # 3. VÍDEOS EN BLOQUE (Filtrando palabras basura)
        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"🎞️ Buscando vídeos cinematográficos de {tema_limpio}...")
        v_urls = []
        for k in palabras_claves[:3]:
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=10&orientation=portrait"
            try:
                res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                for v in res.get('videos', []):
                    v_urls.append(v['video_files'][0]['link'])
            except:
                pass
        
        random.shuffle(v_urls)
        
        last_valid_clip = None
        for i in range(num_clips): 
            try:
                v_url = v_urls[i % len(v_urls)] if v_urls else None
                if v_url:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                    last_valid_clip = f"p_{i}.mp4"
                else:
                    raise Exception("Fallo Pexels")
            except:
                if last_valid_clip: subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=480x854:d={clip_duration}:r=25 -c:v libx264 -preset superfast p_{i}.mp4', shell=True)
            processed_clips.append(f"p_{i}.mp4")

        # 4. CIERRE
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)

        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 5. RENDER FINAL
        status.write("✨ Quemando master...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡VÍDEO CREADO A PARTIR DE TU IDEA!")
            st.balloons()
