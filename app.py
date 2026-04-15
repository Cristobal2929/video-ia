import streamlit as st
import os, time, random, subprocess, requests, math, re

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# 1. CEREBRO DINÁMICO (Se adapta a CUALQUIER tema)
def obtener_guion_pro(tema):
    t = tema.lower().strip()
    
    # 1. Palabras clave auto-generadas (Busca la palabra exacta + contexto cinematográfico)
    # Así, si pides "Pirámides", buscará "Pirámides cinematic", "Pirámides mystery", etc.
    palabras_base = t.split()
    keys = [f"{p} cinematic" for p in palabras_base] + [f"{t} mystery", f"{t} epic", "secret discovery", "dark history"]
    
    # 2. Asignación de Rol Dinámico
    roles = [
        f"el mayor investigador y documentalista experto en {tema}",
        f"un periodista de investigacion que acaba de descubrir un secreto sobre {tema}",
        f"un historiador revelando la verdad oculta de {tema}",
        f"un experto en teorias conspirativas hablando sobre {tema}"
    ]
    rol_elegido = random.choice(roles)

    # 3. Prompt Maestro Adaptativo
    prompt_maestro = f"Actua como {rol_elegido}. Escribe una historia viral, INCREIBLE y poco conocida sobre {tema}. ESTRUCTURA EXACTA: 1. Gancho perturbador o dato chocante. 2. Desarrollo con un suceso real o misterioso sobre {tema}. 3. Final que explote la cabeza del espectador. REGLAS: MAXIMO 65 PALABRAS. ESCRIBE SOLO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. SOLO TEXTO LIMPIO."

    guion_fallback = f"LO QUE ESTAS A PUNTO DE ESCUCHAR SOBRE {tema.upper()} HA SIDO CENSURADO DURANTE DECADAS LOS LIBROS DE HISTORIA MIENTEN Y LA VERDAD ESTA OCULTA A PLENA VISTA PRESTA ATENCION PORQUE CUANDO DESCUBRAS EL SECRETO TU FORMA DE VER EL MUNDO CAMBIARA PARA SIEMPRE SIGUENOS"

    try:
        url = "https://sentence.fineshopdesign.com/api/ai"
        res = requests.get(url, params={"prompt": prompt_maestro, "seed": random.randint(1, 10000)}, timeout=12).json()
        guion = res.get("reply", "").upper()
        
        # Limpiamos todo rastro de puntuación
        guion = re.sub(r'[^\w\s]', '', guion)
        guion = guion.replace('\n', ' ').strip()
        
        if len(guion) < 40: raise Exception("IA generó texto muy corto")
        return guion, keys
    except:
        return guion_fallback, keys

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

st.title("🦅 Fénix Studio: Cerebro Dinámico")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime CUALQUIER tema y el bot se adaptará:"):
    with st.status("🎬 Analizando tema y creando guion...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves = obtener_guion_pro(user_input)
        status.write(f"✍️ Rol adaptado a: {user_input}.")
        
        # 1. AUDIO (-10% velocidad)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        
        tono = 60 if "terror" in user_input.lower() else 80
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. SUBTÍTULOS (Tamaño 38, sincronización perfecta)
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
                            time_per_chunk = (end - start) / len(chunks)
                            for j, chunk in enumerate(chunks):
                                c_start = start + (j * time_per_chunk)
                                c_end = c_start + time_per_chunk
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=38:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{c_start},{c_end})'")
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except:
            st.stop()

        # 3. IMÁGENES DINÁMICAS (Busca exactamente tu tema)
        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        random.shuffle(palabras_claves)
        last_valid_clip = None
        
        status.write(f"🎞️ Buscando vídeos de '{user_input}'...")
        for i in range(num_clips): 
            k = palabras_claves[i % len(palabras_claves)]
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=1&orientation=portrait"
            try:
                res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=8).json()
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                last_valid_clip = f"p_{i}.mp4"
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
        status.write("✨ Montando master...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
