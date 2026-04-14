import streamlit as st
import os, time, random, subprocess, glob, re

st.set_page_config(page_title="Fénix Studio AI", layout="centered", page_icon="🎬")

st.markdown("""
    <style>
    .main {background-color: #0d1117; color: white;}
    .stHeader {text-align: center; background: #1c2128; padding: 30px; border-radius: 20px; border: 1px solid #30363d; margin-bottom: 20px;}
    .stButton>button {background: linear-gradient(90deg, #6366f1, #a855f7); color: white; border: none; font-weight: bold; border-radius: 12px; height: 3.5em; width: 100%; transition: 0.3s;}
    .stButton>button:hover {transform: scale(1.02); box-shadow: 0 5px 15px rgba(168, 85, 247, 0.4);}
    h1 {background: -webkit-linear-gradient(#fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    </style>
""", unsafe_allow_html=True)

def transformar_srt(vtt_path, srt_path):
    try:
        def parse_t(t):
            p = t.split(':')
            return int(p[-3])*3600000 + int(p[-2])*60000 + int(float(p[-1].replace(',','.'))*1000)
        def format_t(ms):
            return f"{ms//3600000:02d}:{(ms%3600000)//60000:02d}:{(ms%60000)//1000:02d},{ms%1000:03d}"
        with open(vtt_path, 'r', encoding='utf-8') as f: lines = f.readlines()
        clean = [l for l in lines if "-->" in l or (l.strip() and not l.strip().isdigit() and not l.startswith("WEBVTT"))]
        srt_f, cnt = [], 1
        for i in range(0, len(clean), 2):
            if i+1 < len(clean) and "-->" in clean[i]:
                t = clean[i].split(" --> ")
                s, e = parse_t(t[0]), parse_t(t[1])
                w = re.sub(r'[.,;!¡¿?]', '', clean[i+1].strip()).upper().split()
                if not w: continue
                step = (e - s) / max(len(w), 1)
                for j in range(0, len(w), 2):
                    g = w[j:j+2]
                    srt_f.append(f"{cnt}\n{format_t(s+int(j*step))} --> {format_t(s+int((j+len(g))*step))}\n{' '.join(g)}\n")
                    cnt += 1
        with open(srt_path, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def generar_guion(prompt, nicho):
    textos = {"Negocio": "El éxito se construye con disciplina.", "Dieta": "Tu cuerpo es tu templo.", "Historia": "Conocer el pasado es dominar el futuro."}
    return f"{prompt.upper()}. {textos.get(nicho, '')} Toma acción hoy mismo y cambia tu vida. Las oportunidades no esperan a nadie."

st.markdown('<div class="stHeader"><h1>🎬 FÉNIX AI STUDIO</h1><p>Producción Viral de Alta Gama</p></div>', unsafe_allow_html=True)
if "guion_ia" not in st.session_state: st.session_state.guion_ia = ""

with st.sidebar:
    st.header("⚙️ Configuración")
    nicho = st.selectbox("Nicho", ["Negocio", "Dieta", "Historia"])
    color_sub = st.color_picker("Color Subtítulos", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

col1, col2 = st.columns(2)
with col1:
    prompt = st.text_input("🤖 Idea Principal:", "Las claves del éxito")
    if st.button("🪄 REDACTAR GUION"): st.session_state.guion_ia = generar_guion(prompt, nicho)
    guion_final = st.text_area("✍️ Guion:", value=st.session_state.guion_ia, height=150)
with col2:
    st.info(f"📁 Nicho: {nicho}")
    st.info(f"🎨 Subs: {color_sub}")

if st.button("🚀 INICIAR PRODUCCIÓN HD"):
    if not guion_final:
        st.warning("Primero genera un guion.")
    else:
        uid = int(time.time())
        os.makedirs("output", exist_ok=True)
        final_p = f"output/video_{uid}.mp4"
        with st.status("💎 Fabricando Vídeo...", expanded=True) as status:
            status.write("🔊 Generando voz...")
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            if transformar_srt("t.vtt", "t.srt"):
                clips = glob.glob(f"{nicho}/*.mp4")
                if clips:
                    status.write("🎬 Editando vídeo para web...")
                    clip = random.choice(clips)
                    est = f"Fontname=Impact,FontSize=30,PrimaryColour={ass_color},Outline=3,Alignment=2,MarginV=150"
                    
                    # Comando ultra-compatible para Google Chrome
                    cmd = f'ffmpeg -y -stream_loop -1 -i "{clip}" -i t.mp3 -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -profile:v baseline -level 3.0 -c:a aac -b:a 192k -shortest "{final_p}"'
                    
                    subprocess.run(cmd, shell=True)
                    
                    # Mostrar el video leyendo directamente el archivo (evita bloqueos del navegador)
                    st.video(final_p)
                    
                    with open(final_p, 'rb') as f:
                        st.download_button("📥 DESCARGAR VIDEO", f.read(), file_name=f"Fenix_{uid}.mp4")
                    status.update(label="✅ Vídeo Listo y Compatible!", state="complete")
                else:
                    st.error("No hay clips en la carpeta.")
