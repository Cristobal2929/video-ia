import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V152", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V152 🛠️🚀</div>', unsafe_allow_html=True)

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def limpiar_texto(t):
    t = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction', '', t, flags=re.I)
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def extraer_kw(texto, i):
    t = texto.lower()
    if any(x in t for x in ["dinero", "banco", "millonario"]): return "luxury money"
    if any(x in t for x in ["gym", "fuerte", "entrenar"]): return "fitness motivation"
    if any(x in t for x in ["coche", "velocidad", "ferrari"]): return "supercar cinematic"
    fallbacks = ["success luxury", "modern mansion", "private jet", "rolex watch", "office skyscraper"]
    return fallbacks[i % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

def s_to_srt(s):
    h, m = int(s // 3600), int((s % 3600) // 60)
    sc, ms = int(s % 60), int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sc:02d},{ms:03d}"

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de titan")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

# Mapeo de colores para SRT (Formato BGR)
colores_bgr = {"yellow": "&H0000FFFF", "white": "&H00FFFFFF", "#00FFD1": "&H00D1FF00"}
bgr_elegido = colores_bgr[color_sub]

if st.button("🚀 CREAR VÍDEO (MÉTODO SRT ANTI-RAM)"):
    if not tema: st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            # 1. GUION Y AUDIO MAESTRO
            st.markdown('<div class="msg">📝 IA redactando y grabando...</div>', unsafe_allow_html=True)
            p = f"Escribe UNICAMENTE el texto para TikTok sobre {tema}. Sin notas. Solo español fluido. Maximo 90 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=20).text
                guion = limpiar_texto(g_raw)
            except: guion = "La disciplina es la base de toda victoria. Sin esfuerzo no hay recompensa."

            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            musica_file = "taller/bg.mp3"
            r_m = requests.get("https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3")
            with open(musica_file, "wb") as f: f.write(r_m.content)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 20.0

            st.markdown('<div class="msg">🎧 Mezclando audio principal...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla_final.mp3"
            fade_st = max(0, dur - 2)
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.15,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio_mezcla}"', shell=True)

            # 2. GENERADOR DE SUBTÍTULOS SRT (El truco maestro que ahorra 99% de RAM)
            st.markdown('<div class="msg">📄 Creando archivo de subtítulos profesional...</div>', unsafe_allow_html=True)
            pal_sub = guion.upper().split()
            chunks = [pal_sub[j:j+2] for j in range(0, len(pal_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            
            srt_content = ""
            for j, p_txt in enumerate(chunks):
                ts = j * t_ch
                te = (j + 1) * t_ch
                txt_limpio = ' '.join(p_txt).replace("'", "").replace(":", "")
                srt_content += f"{j+1}\n{s_to_srt(ts)} --> {s_to_srt(te)}\n{txt_limpio}\n\n"
                
            with open("taller/subs.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)

            # 3. CAPTURA Y LIMPIEZA DE VÍDEOS (SIN DIBUJAR TEXTO AÚN)
            n_clips = min(math.ceil(dur / 3.4), 14)
            t_clip = dur / n_clips
            clips = []
            palabras = guion.split()
            chunk = max(len(palabras) // n_clips, 1)

            for i in range(n_clips):
                txt_part = " ".join(palabras[i*chunk:(i+1)*chunk])
                kw = extraer_kw(txt_part, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Procesando "{kw.upper()}"...</div>', unsafe_allow_html=True)
                
                raw, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                
                try:
                    h = {"Authorization": PEXELS_API}
                    url_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1"
                    v_link = requests.get(url_p, headers=h, timeout=12).json()['videos'][0]['video_files'][0]['link']
                    with open(raw, 'wb') as f: f.write(requests.get(v_link).content)
                    # Solo recorta, estabiliza color y quita audio (SUPER LIGERO)
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw}" -t {t_clip} -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p" -c:v libx264 -preset ultrafast -r 24 -an -threads 1 "{vid}"', shell=True)
                except:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -an -threads 1 "{vid}"', shell=True)
                
                clips.append(os.path.abspath(vid))
                if os.path.exists(raw): os.remove(raw)
                gc.collect()

            # 4. UNIÓN DE CLIPS (RÁPIDO)
            st.markdown('<div class="msg">🎬 Ensamblando las piezas mudas...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # 5. QUEMADO FINAL DEL SRT (No consume memoria, solo lee el archivo secuencialmente)
            st.markdown('<div class="msg">✨ Tatuando subtítulos con bajo consumo...</div>', unsafe_allow_html=True)
            final = "taller/master.mp4"
            
            # Estilo de subtitulos incrustados (El truco final)
            estilo = f"Fontname=Arial,FontSize=26,PrimaryColour={bgr_elegido},OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0,Alignment=5"
            cmd_final = f'ffmpeg -y -i "{mudo}" -i "{audio_mezcla}" -vf "subtitles=taller/subs.srt:force_style=' + f"'{estilo}'" + f'" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 28 -threads 1 -t {dur} "{final}"'
            
            subprocess.run(cmd_final, shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO (CERO ESTRÉS DE RAM)</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Misión fallida.")
