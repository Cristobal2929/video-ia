import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V194", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #00FFD1; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
    .stTextArea>div>div>textarea, .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #00FFD1; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V194 🦅🎬</div>', unsafe_allow_html=True)

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

GUIONES_TERROR = ["En la oscuridad del hospital abandonado, los susurros no vienen de los vivos. Cada puerta cerrada guarda un secreto que nunca debió ser despertado. Si escuchas pasos detrás de ti, no te gires. Ya es tarde."]
GUIONES_GYM = ["El éxito no se regala, se construye con cada gota de sudor. Cuando tus músculos ardan y quieras rendirte, recuerda por qué empezaste. La disciplina es lo que te separa de los demás."]
GUIONES_NEGOCIO = ["Mientras otros duermen, tú construyes. Mientras otros gastan, tú inviertes. La libertad financiera no es un sueño, es el resultado de decisiones valientes tomadas cada día."]

def purificar_guion_fluido(t, fallback_text):
    t_low = t.lower()
    # FILTRO BÚNKER: Bloquea fallos de la IA (HTML/Cloudflare)
    if any(x in t_low for x in ["<div", "doctype", "html", "class=", "error", "cloudflare"]):
        return fallback_text
    
    texto_limpio = t
    cortes = ["pollinations", "support", "powered", "http", "www", ".ai", "free text", "api"]
    for corte in cortes:
        if corte.lower() in texto_limpio.lower():
            texto_limpio = texto_limpio[:texto_limpio.lower().index(corte.lower())]

    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', texto_limpio).strip()
    if len(texto_limpio.split()) < 15:
        return fallback_text
    return texto_limpio

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)
    if 'videos_usados' not in st.session_state:
        st.session_state['videos_usados'] = []

f_abs = get_font()

categoria = st.selectbox("🎬 Temática General:", ["Negocios / Éxito", "Gym / Motivación", "Terror / Misterio"])
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])
st.markdown("---")
tema_prompt = st.text_input("🧠 Tema para que la IA escriba:", placeholder="Ej: Terror en el bosque...")
guion_personalizado = st.text_area("📝 O pega tu texto EXACTO:", placeholder="Pega aquí tu guion viral...", height=120)

if st.button("🚀 CREAR VÍDEO RÁPIDO (SIN MÚSICA)"):
    preparar()
    log = st.container()
    with log:
        # Selección de recursos según categoría
        if categoria == "Terror / Misterio":
            voz, kws, fallback = "es-ES-AlvaroNeural", ["scary abandoned hospital", "creepy dark forest", "ghostly shadows"], random.choice(GUIONES_TERROR)
        elif categoria == "Gym / Motivación":
            voz, kws, fallback = "es-MX-JorgeNeural", ["bodybuilding gym", "heavy weight lifting", "running athlete"], random.choice(GUIONES_GYM)
        else:
            voz, kws, fallback = "es-MX-JorgeNeural", ["luxury lifestyle dubai", "private jet interior", "supercars city"], random.choice(GUIONES_NEGOCIO)

        # Determinar Guion
        if guion_personalizado.strip():
            guion_final = guion_personalizado.strip()
        elif tema_prompt.strip():
            st.markdown('<div class="msg">🧠 IA redactando guion...</div>', unsafe_allow_html=True)
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote('Escribe un guion épico para TikTok sobre: ' + tema_prompt + '. Solo español. Mínimo 50 palabras.')}", timeout=20).text
                guion_final = purificar_guion_fluido(g_raw, fallback)
            except: guion_final = fallback
        else: guion_final = fallback

        # 1. GRABAR VOZ
        st.markdown('<div class="msg">🎙️ Grabando locución perfecta...</div>', unsafe_allow_html=True)
        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "{audio_voz}"', shell=True)

        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: dur = 15.0

        # Procesar clips
        palabras = guion_final.upper().split()
        n_clips = min(math.ceil(dur / 2.8), 12) 
        t_clip = dur / n_clips
        clips = []

        for i in range(n_clips):
            kw = random.choice(kws)
            st.markdown(f'<div class="msg">🎥 Escena {i+1}: Procesando visuales de "{kw}"...</div>', unsafe_allow_html=True)
            raw_vid, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
            
            # Subtítulos dinámicos
            sub_split = [palabras[j:j+2] for j in range(i*len(palabras)//n_clips, (i+1)*len(palabras)//n_clips, 2)]
            t_p = t_clip / max(len(sub_split), 1)
            draws = []
            for k, p in enumerate(sub_split):
                t_t = " ".join(p)
                if len(t_t) > 10:
                    draws.append(f"drawtext=text='{p[0]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                    draws.append(f"drawtext=text='{p[1]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                else:
                    draws.append(f"drawtext=text='{t_t}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=75:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{k*t_p},{(k+1)*t_p})'")
            
            vf_script = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,{','.join(draws)}"
            with open(f"taller/f_{i}.txt", "w", encoding="utf-8") as f: f.write(vf_script)

            try:
                h = {"Authorization": PEXELS_API}
                res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=15", headers=h).json()
                videos_validos = [v for v in res.get('videos', []) if v.get('duration', 0) > 3 and v.get('id') not in st.session_state['videos_usados']]
                if videos_validos:
                    v_elegido = random.choice(videos_validos)
                    st.session_state['videos_usados'].append(v_elegido['id'])
                    with open(raw_vid, 'wb') as f: f.write(requests.get(v_elegido['video_files'][0]['link']).content)
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -filter_script:v taller/f_{i}.txt -c:v libx264 -preset ultrafast -r 24 -an "{vid}" > /dev/null 2>&1', shell=True)
                    if os.path.exists(vid): clips.append(os.path.abspath(vid))
            except: pass
            if os.path.exists(raw_vid): os.remove(raw_vid)

        # Montaje final
        with open("taller/lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        final = "taller/master.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_voz}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -r 24 -t {dur} "{final}" > /dev/null 2>&1', shell=True)
        
        if os.path.exists(final):
            st.markdown('<div class="info-card">🏆 VÍDEO SIN MÚSICA LISTO (MÁXIMA VELOCIDAD)</div>', unsafe_allow_html=True)
            with open(final, "rb") as f: st.video(f.read())
