import streamlit as st
import os, time, random, subprocess, requests, math

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# 1. GENERADOR DE GUIONES Y KEYWORDS BLINDADO
def obtener_guion_pro(tema):
    t = tema.lower()
    # Mapeo de conceptos visuales en INGLÉS para Pexels (Así no salen cosas raras)
    keys = ["cinematic", "mystery", "epic"]
    if "terror" in t or "miedo" in t:
        keys = ["creepy shadow", "abandoned house", "scary dark", "horror movie", "nightmare"]
        guion_fallback = "HAY UN EXPERIMENTO DE 1980 QUE EL GOBIERNO INTENTO BORRAR DE LA HISTORIA. ENCERRARON A CINCO PERSONAS EN LA OSCURIDAD TOTAL DURANTE UN MES. LO QUE ENCONTRARON AL ABRIR LA PUERTA TE DEJARA SIN DORMIR. SIGUENOS."
    elif "coche" in t or "motor" in t:
        keys = ["sports car", "engine", "fast racing", "luxury vehicle", "drifting"]
        guion_fallback = "ESTE ES EL SECRETO MEJOR GUARDADO DE LA INDUSTRIA AUTOMOTRIZ. HAY UN MOTOR QUE NO USA GASOLINA Y QUE FUE DESTRUIDO PARA PROTEGER LOS NEGOCIOS DE LOS MAS RICOS. PRESTA ATENCION AL FINAL."
    else:
        keys = [f"{t} cinematic", "epic discovery", "secret mystery", "shocking truth"]
        guion_fallback = f"EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE NADIE QUIERE QUE SEPAS. ESTO NO ES UNA TEORIA, ES UN PLAN PERFECTO PARA OCULTAR LA VERDAD MAS PERTURBADORA. SIGUENOS PARA DESCUBRIRLO."

    try:
        prompt = f"Escribe un guion viral increible de 60 palabras sobre {tema}. Estructura: Gancho -> Datos -> Final. SOLO MAYUSCULAS. SIN SIGNOS."
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=5).json()
        guion = res.get("reply", "").upper()
        if len(guion) < 40: raise Exception("IA lenta")
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

st.title("🦅 Fénix Studio: Viral Perfecto")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema (Terror, Coches, Espacio...):"):
    with st.status("🎬 Producción Viral en curso...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves = obtener_guion_pro(user_input)
        status.write("✍️ Guion y conceptos visuales listos.")
        
        # 1. AUDIO
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        
        tono = 60 if "terror" in user_input.lower() else 80
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. SUBTÍTULOS CORTADOS A 1-2 PALABRAS (El gran arreglo)
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
                            # Rompemos la frase larga en trozos de 2 palabras máximo
                            palabras = texto.split()
                            chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
                            time_per_chunk = (end - start) / len(chunks)
                            
                            for j, chunk in enumerate(chunks):
                                c_start = start + (j * time_per_chunk)
                                c_end = c_start + time_per_chunk
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=55:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{c_start},{c_end})'")
            
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except Exception as e:
            st.error(f"Error en VTT: {e}")
            st.stop()

        # 3. ESCENAS COHERENTES
        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        random.shuffle(palabras_claves)
        last_valid_clip = None
        
        status.write(f"🎞️ Reuniendo escenas visuales épicas...")
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
        status.write("✨ Quemando master viral...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
