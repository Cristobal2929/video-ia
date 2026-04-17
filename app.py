import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V182", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF3E3E, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FF3E3E; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #FF3E3E; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #FF3E3E, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V182 🦍🔥</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
            with open(p, "wb") as f: f.write(r.content)
        except: pass
    return "font.ttf"

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def obtener_datos_tema(t_input):
    t = t_input.lower()
    if any(x in t for x in ["miedo", "terror", "horror", "oscuro", "hospital", "sangre", "paranormal"]):
        return {
            "tipo": "terror",
            "voz": "es-ES-AlvaroNeural",
            # Servidor Inmortal: Internet Archive
            "musica": "https://ia800104.us.archive.org/1/items/HorrorAmbience_201901/Horror%20Ambience.mp3",
            "kws": ["scary dark", "abandoned building", "creepy forest", "horror night", "dark shadows"],
            "fallback": "En el silencio de la noche, las sombras susurran verdades que nadie quiere escuchar. Lo que acecha en la oscuridad, pronto será tu peor pesadilla."
        }
    elif any(x in t for x in ["gym", "entrenar", "fuerte", "disciplina", "fitness", "dieta", "kilos"]):
        return {
            "tipo": "gym",
            "voz": "es-MX-JorgeNeural",
            "musica": "https://ia801400.us.archive.org/1/items/A_Hero_Steps_Forward/A_Hero_Steps_Forward.mp3",
            "kws": ["gym workout heavy", "fitness motivation intense", "heavy weights running", "athlete intense"],
            "fallback": "El dolor que sientes hoy es la victoria que celebrarás mañana. No te detengas, no te rindas, levántate y demuestra de qué estás hecho."
        }
    else:
        return {
            "tipo": "negocio",
            "voz": "es-MX-JorgeNeural",
            "musica": "https://ia801400.us.archive.org/1/items/A_Hero_Steps_Forward/A_Hero_Steps_Forward.mp3",
            "kws": ["luxury lifestyle success", "dubai skyline rich", "private jet wealth", "expensive supercar business"],
            "fallback": "La gente común sueña con el éxito, mientras que los grandes madrugan y trabajan duro para hacerlo realidad. Tu imperio se construye hoy."
        }

def purificar_guion(t, fallback_text):
    if any(x in t.lower() for x in ["<div", "doctype", "html", "class="]):
        return fallback_text
    
    texto_limpio = t
    cortes = ["support pollinations", "powered by", "free text api", "coffee to keep"]
    for corte in cortes:
        if corte.lower() in texto_limpio.lower():
            texto_limpio = texto_limpio[:texto_limpio.lower().index(corte.lower())]

    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', texto_limpio).strip()
    if len(texto_limpio) < 20: 
        return fallback_text
    return texto_limpio

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Terror oscuro... o Negocios de lujo...")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#FF3E3E", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (MODO BESTIA V182)"):
    if not tema: st.error("⚠️ Escribe un tema primero")
    else:
        preparar()
        datos_tema = obtener_datos_tema(tema)
        
        log = st.container()
        with log:
            st.markdown(f'<div class="msg">🤖 Modo de Guion: {datos_tema["tipo"].upper()} (Agresivo)</div>', unsafe_allow_html=True)
            st.markdown('<div class="msg">📝 Creando historia viral e impactante...</div>', unsafe_allow_html=True)
            try:
                # PROMPT EXTREMO: Forzamos historias potentes y virales
                prompt_bestia = f"Escribe un guion viral y MUY impactante para TikTok sobre: {tema}. Tono intenso, que atrape la atención desde la primera palabra. Historia o reflexión épica. No uses palabras raras, ni introducciones aburridas, ve al grano. Solo español. Maximo 60 palabras."
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_bestia)}", timeout=25).text
                guion = purificar_guion(g_raw, datos_tema["fallback"])
            except: guion = datos_tema["fallback"]

            st.markdown('<div class="msg">🎙️ Grabando voz y buscando música invencible...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice {datos_tema["voz"]} --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            musica_file = "taller/bg.mp3"
            exito_musica = False
            try:
                # Enlaces directos a Internet Archive (inmunes a bloqueos)
                r_m = requests.get(datos_tema["musica"], headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                if r_m.status_code == 200 and len(r_m.content) > 100000:
                    with open(musica_file, "wb") as f: f.write(r_m.content)
                    exito_musica = True
            except: pass

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            st.markdown('<div class="msg">🎧 Mezclando audio y voz al 10%...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            vol = "0.08" if datos_tema["tipo"] == "terror" else "0.10"
            
            if exito_musica:
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume={vol},afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame "{audio_mezcla}" > /dev/null 2>&1', shell=True)
            else:
                shutil.copy(audio_voz, audio_mezcla)

            palabras = guion.upper().split()
            n_clips = min(math.ceil(dur / 2.8), 12) # Clips más dinámicos
            t_clip = dur / n_clips
            clips = []
            videos_usados = [] # MEMORIA PARA NO REPETIR EL MISMO CLIP

            for i in range(n_clips):
                kw = random.choice(datos_tema["kws"])
                st.markdown(f'<div class="msg">🎥 Escena {i+1}: Cazando metraje de acción para "{kw}"...</div>', unsafe_allow_html=True)
                
                vid = f"taller/v_{i}.mp4"
                exito_vid = False
                
                sub_split = [palabras[j:j+2] for j in range(i*len(palabras)//n_clips, (i+1)*len(palabras)//n_clips, 2)]
                t_p = t_clip / max(len(sub_split), 1)
                draws = []
                for k, p in enumerate(sub_split):
                    t_txt = " ".join(p)
                    if len(t_txt) > 10:
                        draws.append(f"drawtext=text='{p[0]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                        if len(p) > 1:
                            draws.append(f"drawtext=text='{p[1]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                    else:
                        draws.append(f"drawtext=text='{t_txt}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                
                vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,{','.join(draws)}"

                try:
                    h = {"Authorization": PEXELS_API}
                    res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=20", headers=h).json()
                    
                    # Filtramos vídeos largos y que NO SE HAYAN USADO ANTES
                    videos_validos = [v for v in res.get('videos', []) if v.get('duration', 0) > 3 and v.get('id') not in videos_usados]
                    
                    if videos_validos:
                        v_elegido = random.choice(videos_validos)
                        videos_usados.append(v_elegido['id'])
                        v_url = v_elegido['video_files'][0]['link']
                        
                        subprocess.run(f'ffmpeg -y -ss {random.randint(0,2)} -i "{v_url}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)
                        if os.path.exists(vid): exito_vid = True
                except: pass

                # EL ANTICONGELAMIENTO: Si Pexels falla o está colapsado, generamos un clip neutro con el texto
                if not exito_vid:
                    vf_neutro = f"format=yuv420p,{','.join(draws)}"
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -vf "{vf_neutro}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)

                clips.append(os.path.abspath(vid))

            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO MODO BESTIA COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
