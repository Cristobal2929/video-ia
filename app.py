import streamlit as st
import os, time, random, subprocess, requests, math, re

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# 1. GENERADOR DE GUIONES CON ENFOQUES ALEATORIOS
def obtener_guion_pro(tema):
    t = tema.lower()
    
    # Lista de enfoques para que la IA no se repita
    enfoques = [
        "desde una perspectiva conspiranoica y secreta",
        "enfocado en un misterio olvidado por la historia",
        "con un tono de leyenda urbana aterradora",
        "basado en un descubrimiento cientifico impactante",
        "como si fuera un archivo clasificado que acaba de filtrarse"
    ]
    enfoque_hoy = random.choice(enfoques)
    
    if "terror" in t or "miedo" in t or "paranormal" in t:
        keys = ["creepy shadow", "abandoned room", "scary dark", "horror movie", "nightmare"]
        guion_fallback = "HAY UN EXPERIMENTO DE MIL NOVECIENTOS OCHENTA QUE EL GOBIERNO INTENTO BORRAR DE LA HISTORIA ENCERRARON A CINCO PERSONAS EN LA OSCURIDAD TOTAL DURANTE UN MES LO QUE ENCONTRARON AL ABRIR LA PUERTA TE DEJARA SIN DORMIR"
    elif "coche" in t or "motor" in t:
        keys = ["sports car", "engine", "fast racing", "luxury vehicle", "drifting"]
        guion_fallback = "EN LOS AÑOS OCHENTA UN INGENIERO CREO UN MOTOR QUE FUNCIONABA SOLO CON AGUA DIAS ANTES DE PATENTARLO SU TALLER ARDIO HASTA LOS CIMIENTOS Y EL DESAPARECIO SIN DEJAR RASTRO LA TECNOLOGIA NUNCA SE RECUPERO"
    else:
        keys = [f"{t} cinematic", "epic discovery", "secret documents", "shocking truth"]
        guion_fallback = f"LA HISTORIA OFICIAL DE {tema.upper()} ES UNA MENTIRA HACE DECADAS UN INVESTIGADOR DESCUBRIO DOCUMENTOS QUE PROBABAN LO CONTRARIO ANTES DE PODER PUBLICARLOS FUE SILENCIADO Y SU TRABAJO DESTRUIDO"

    # El Prompt ahora incluye el ENFOQUE ALEATORIO
    prompt_maestro = f"Eres un experto en retencion de TikTok. Escribe una historia UNICA y ORIGINAL sobre {tema} {enfoque_hoy}. REGLAS: 1. Gancho psicologico. 2. Desarrollo con datos logicos. 3. Final brutal. MAXIMO 65 PALABRAS. TODO EN MAYUSCULAS. SIN PUNTOS NI COMAS NI TILDES. SOLO PALABRAS."

    try:
        url = "https://sentence.fineshopdesign.com/api/ai"
        # Usamos una semilla aleatoria para romper el cache de la API
        res = requests.get(url, params={"prompt": prompt_maestro, "seed": random.randint(1, 99999)}, timeout=12).json()
        guion = res.get("reply", "").upper()
        
        guion = re.sub(r'[^\w\s]', '', guion)
        guion = guion.replace('\n', ' ').strip()
        
        if len(guion) < 40: raise Exception("IA corta")
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

st.title("🦅 Fénix Studio: Historias Unicas")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema (Cada vez sera una historia distinta):"):
    with st.status("🎬 Generando historia original...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves = obtener_guion_pro(user_input)
        status.write(f"✍️ Enfoque aplicado. Guion: {guion[:50]}...")
        
        # 1. AUDIO (-10% velocidad para mejor lectura)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        
        tono = 60 if "terror" in user_input.lower() else 80
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. SUBTÍTULOS DINÁMICOS (Tamaño 38 para evitar cortes)
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

        # 3. IMÁGENES
        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        random.shuffle(palabras_claves)
        last_valid_clip = None
        
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
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
