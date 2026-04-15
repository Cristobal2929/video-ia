import streamlit as st
import os, time, random, subprocess, requests, math, re
import urllib.parse

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 2]
    return " ".join(limpias) if limpias else orden

def obtener_guion_pro(orden_usuario):
    tema_limpio = limpiar_orden(orden_usuario)
    keys = [f"{tema_limpio} cinematic", f"{tema_limpio} epic", "ancient mystery", "dark secret"]
    
    prompt_maestro = f"Eres el mejor guionista de TikTok. TAREA: Escribe una historia fascinante sobre: {tema_limpio}. ESTRUCTURA: 1. Gancho brutal. 2. Desarrollo profundo con datos historicos o increibles reales. 3. Climax y la EXPLICACION LOGICA del misterio al final. REGLAS: MINIMO 100 PALABRAS. ESCRIBE TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. SOLO TEXTO."

    guion_fallback = f"TODO LO QUE TE HAN ENSEÑADO SOBRE {tema_limpio.upper()} ES UNA COMPLETA MENTIRA DURANTE AÑOS LOS INVESTIGADORES NOTARON ALGO EXTRAÑO PERO FUERON SILENCIADOS POR LOS DE ARRIBA LA VERDADERA LOGICA DETRAS DE ESTE MISTERIO ES QUE EL GOBIERNO LO USO COMO UN EXPERIMENTO SOCIAL MASIVO PARA VER HASTA DONDE PODIAMOS CREER UNA ILUSION ABSOLUTA AHORA QUE SABES EL SECRETO FINAL EL SISTEMA YA NO PUEDE ENGAÑARTE DESPIERTA Y SIGUENOS"

    # INTENTO 1: Motor IA Principal
    try:
        url_1 = "https://sentence.fineshopdesign.com/api/ai"
        res_1 = requests.get(url_1, params={"prompt": prompt_maestro, "seed": random.randint(1, 999999)}, timeout=15).json()
        guion = res_1.get("reply", "").upper()
        guion = re.sub(r'[^\w\s]', '', guion).replace('\n', ' ').strip()
        if len(guion) > 50:
            return guion, keys, tema_limpio
    except Exception as e:
        print(f"IA Principal falló: {e}. Activando IA de respaldo...")
        pass

    # INTENTO 2: Motor IA de Respaldo (Pollinations) - Entra si la primera falla
    try:
        prompt_codificado = urllib.parse.quote(prompt_maestro)
        url_2 = f"https://text.pollinations.ai/{prompt_codificado}?system=Eres%20un%20guionista%20experto"
        res_2 = requests.get(url_2, timeout=20)
        guion = res_2.text.upper()
        guion = re.sub(r'[^\w\s]', '', guion).replace('\n', ' ').strip()
        if len(guion) > 50:
            return guion, keys, tema_limpio
    except Exception as e:
        print(f"IA Secundaria falló: {e}. Usando guion de emergencia...")
        pass
            
    # Solo llega aquí si se cae Internet o las dos IAs están muertas
    return guion_fallback, keys, tema_limpio

def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.')
    partes = t_str.split(':')
    if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
    elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
    else: return float(partes[0])

st.title("🦅 Fénix Studio: Doble Motor IA")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Pide tu tema (Las IAs se encargarán):"):
    with st.status("🎬 Analizando y creando guion...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_limpio = obtener_guion_pro(orden)
        status.write(f"✍️ Guion completado sobre: '{tema_limpio}'.")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        
        tono = 70
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

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
            pass

        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"🎞️ Buscando vídeos de {tema_limpio}...")
        v_urls = []
        for k in palabras_claves[:2]:
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=15&orientation=portrait"
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

        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)

        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Exportando con doble IA...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
