import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V187", layout="centered")
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V187 🦅🎵</div>', unsafe_allow_html=True)

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

# EL MOTOR MUSICAL EXACTO DE LA V169
MUSICA_V169_BASE = [
    "https://cdn.pixabay.com/download/audio/2021/05/20/audio_f31f9b3b8e.mp3?filename=dance-playful-night-51078.mp3",
    "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=inspiring-cinematic-ambient-11619.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3"
]

MUSICA_TERROR = [
    "https://freepd.com/music/Horror%20Ambience.mp3",
    "https://freepd.com/music/Deep%20Space.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/2/23/Closer_to_the_Void.mp3"
]

def descargar_musica_169(ruta, tipo):
    lista_urls = MUSICA_TERROR if tipo == "terror" else MUSICA_V169_BASE
    random.shuffle(lista_urls)
    # El User-Agent y el validador > 150000 que funcionó a la perfección en la V169
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for url in lista_urls:
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200 and len(r.content) > 150000:
                with open(ruta, "wb") as f: f.write(r.content)
                return True
        except: pass
    return False

GUIONES_TERROR = [
    "Cierra los ojos. Imagina que estás solo en tu casa. De repente, escuchas un susurro desde el pasillo. Te giras lentamente, y ahí está... la sombra que te ha estado observando todo este tiempo. Quieres gritar, pero no tienes voz.",
    "Dicen que si te despiertas a las 3 de la madrugada sin razón, es porque alguien te está mirando fijamente desde la esquina de tu habitación. No abras los ojos. Hazte el dormido. Porque si la miras, nunca te dejará ir."
]
GUIONES_GYM = [
    "El noventa y nueve por ciento de la gente se rinde justo antes de lograrlo. Pero tú no eres del montón. Levántate, ponte las zapatillas y ve a sudar. El dolor que sientes hoy, es la fuerza que tendrás mañana. No hay excusas.",
    "Nadie va a hacer el trabajo por ti. Nadie te va a regalar el cuerpo de tus sueños. Tienes que ganártelo en cada repetición, en cada gota de sudor. Mírate al espejo y prométete que hoy vas a darlo absolutamente todo."
]
GUIONES_NEGOCIO = [
    "Te dijeron que era imposible. Se rieron de tus ideas. Hoy tú construyes tu imperio mientras ellos siguen perdiendo el tiempo. La libertad financiera no se sueña, se trabaja cada maldito día. El mundo es de los que toman acción.",
    "La diferencia entre un soñador y un ganador es la ejecución. Mientras otros buscan el fin de semana para descansar, tú buscas la forma de multiplicar tus ingresos. No te detengas hasta que tu cuenta bancaria parezca un número de teléfono."
]

def purificar_guion_fluido(t, fallback_text):
    if any(x in t.lower() for x in ["<div", "doctype", "html", "class="]):
        return fallback_text
    
    texto_limpio = t
    cortes = ["support pollinations", "powered by", "free text api", "coffee to keep"]
    for corte in cortes:
        if corte.lower() in texto_limpio.lower():
            texto_limpio = texto_limpio[:texto_limpio.lower().index(corte.lower())]

    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', texto_limpio).strip()
    
    if len(texto_limpio.split()) < 15 or not texto_limpio.endswith(('.', '!', '?')):
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
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#FF3E3E", "#00FFD1"])
st.markdown("---")
tema_prompt = st.text_input("🧠 Tema para guion de IA:", placeholder="Ej: Hábitos millonarios...")
guion_personalizado = st.text_area("📝 O guion EXACTO (mín 15 palabras):", placeholder="Pega tu texto aquí y el bot lo usará literalmente.", height=120)

if st.button("🚀 CREAR VÍDEO (MOTOR DE MÚSICA V169)"):
    preparar()
    log = st.container()
    with log:
        if categoria == "Terror / Misterio":
            tipo_musica = "terror"
            voz = "es-ES-AlvaroNeural"
            kws = ["scary dark", "abandoned building", "creepy forest", "horror night"]
            fallback_lista = GUIONES_TERROR
            vol_musica = "0.08"
        elif categoria == "Gym / Motivación":
            tipo_musica = "negocio" 
            voz = "es-MX-JorgeNeural"
            kws = ["gym workout", "fitness motivation", "heavy weights training", "running athlete"]
            fallback_lista = GUIONES_GYM
            vol_musica = "0.10"
        else: 
            tipo_musica = "negocio"
            voz = "es-MX-JorgeNeural"
            kws = ["luxury lifestyle", "dubai skyline", "private jet", "expensive supercar"]
            fallback_lista = GUIONES_NEGOCIO
            vol_musica = "0.10"

        fallback_texto = random.choice(fallback_lista)
        
        if guion_personalizado.strip():
            if len(guion_personalizado.strip().split()) < 15:
                st.error("⚠️ Tu guion personalizado es muy corto (mínimo 15 palabras).")
                st.stop()
            st.markdown('<div class="msg">📝 Usando tu guion personalizado exacto...</div>', unsafe_allow_html=True)
            guion_final = guion_personalizado.strip()
        elif tema_prompt.strip():
            st.markdown('<div class="msg">🧠 Pidiendo a la IA que redacte un guion...</div>', unsafe_allow_html=True)
            prompt = f"Escribe un guion fluido, intenso y completo para TikTok sobre: {tema_prompt}. Debe tener entre 45 y 70 palabras. Asegúrate de que termine con una frase conclusiva, con punto final. Solo español."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=25).text
                guion_final = purificar_guion_fluido(g_raw, fallback_texto)
            except: 
                guion_final = fallback_texto
        else:
            st.markdown('<div class="msg">🎲 Usando guion viral de la biblioteca garantizada.</div>', unsafe_allow_html=True)
            guion_final = fallback_texto

        # AQUI ESTÁ LA MAGIA DE LA V169
        st.markdown('<div class="msg">🎵 Extrayendo música con el Motor V169 (Pixabay CDN)...</div>', unsafe_allow_html=True)
        musica_file = "taller/bg.mp3"
        if not descargar_musica_169(musica_file, tipo_musica):
            st.error("❌ Fallo crítico de audio. Abortando render para evitar vídeo mudo.")
            st.stop()

        st.markdown('<div class="msg">🎙️ Grabando locución...</div>', unsafe_allow_html=True)
        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "{audio_voz}"', shell=True)

        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: dur = 20.0

        audio_mezcla = "taller/mezcla.mp3"
        fade_st = max(0, dur - 2)
        subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume={vol_musica},afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame "{audio_mezcla}" > /dev/null 2>&1', shell=True)

        palabras = guion_final.upper().split()
        n_clips = min(math.ceil(dur / 2.8), 12) 
        t_clip = dur / n_clips
        clips = []

        for i in range(n_clips):
            kw = random.choice(kws)
            st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Recortando vídeo ÚNICO para "{kw}"...</div>', unsafe_allow_html=True)
            
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
                res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=20", headers=h, timeout=10).json()
                
                videos_validos = [v for v in res.get('videos', []) if v.get('duration', 0) > 3 and v.get('id') not in st.session_state['videos_usados']]
                
                if videos_validos:
                    v_elegido = random.choice(videos_validos)
                    st.session_state['videos_usados'].append(v_elegido['id'])
                    v_url = v_elegido['video_files'][0]['link']
                    
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{v_url}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)
                    if os.path.exists(vid): exito_vid = True
            except: pass

            if not exito_vid:
                st.warning(f"⚠️ Pexels falló para '{kw}'. Usando escena neutra.")
                vf_neutro = f"format=yuv420p,{','.join(draws)}"
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -vf "{vf_neutro}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)

            clips.append(os.path.abspath(vid))

        with open("taller/lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        if dur < 8.0:
            st.error(f"❌ Fallo: El vídeo final duraría solo {dur:.1f}s. Demasiado corto. Revisa tu prompt o guion.")
            st.stop()

        final = "taller/master.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 28 -t {dur} "{final}" > /dev/null 2>&1', shell=True)
        
        if os.path.exists(final):
            st.markdown('<div class="info-card">🏆 VÍDEO CON MOTOR V169 COMPLETADO</div>', unsafe_allow_html=True)
            with open(final, "rb") as f: st.video(f.read())
            st.balloons()
