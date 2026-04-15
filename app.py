import streamlit as st
import os, time, random, subprocess, requests, math, re
import urllib.parse

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .pro-subtitle { text-align: center; color: #94A3B8; font-size: 15px; margin-bottom: 30px; font-weight: 400; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
    .stSelectbox>div>div>div { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
    hr { border-color: #334155; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v4.5</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Cerebro Multipolar • Adaptación de Nichos Automática</div>', unsafe_allow_html=True)

def es_texto_valido(texto):
    t_lower = texto.lower()
    basura_html = ["doctype", "<html", "502 bad gateway", "cloudflare", "html class", "error code", "div class"]
    for b in basura_html:
        if b in t_lower: return False
    return True

def limpiar_texto_ia(texto):
    basura_ia = ["USER REQUEST", "START UP", "WRITE A", "ALL CAPS", "NO PERIODS", "SAYS ZERO", "REASONING CONTENT"]
    texto_limpio = texto.upper()
    for b in basura_ia: texto_limpio = texto_limpio.replace(b, "")
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio).replace('\n', ' ').strip()
    return re.sub(' +', ' ', texto_limpio)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden, limpias

# --- DETECTOR DE NICHOS ---
def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "oscuridad", "demonio", "maldito", "asesino", "leyenda", "creepy"]):
        return "terror"
    elif any(w in t for w in ["negocio", "dinero", "invertir", "empresa", "millonario", "finanzas", "cripto", "emprendedor", "ventas", "marketing", "riqueza", "dolares"]):
        return "negocios"
    else:
        return "conspiracion"

# --- MOTOR COMBINATORIO ADAPTATIVO (Cambia la salsa según el nicho) ---
def generar_guion_procedural(tema, nicho):
    tema = tema.upper()
    
    if nicho == "terror":
        ganchos = ["ESTA ES LA HISTORIA MAS ATERRADORA QUE ESCUCHARAS HOY SOBRE", "NUNCA DEBISTE BUSCAR INFORMACION SOBRE", "HAY UNA LEYENDA MALDITA QUE MUY POCOS CONOCEN SOBRE"]
        creencias = ["MUCHOS CREEN QUE ES SOLO UN CUENTO PARA ASUSTAR A LOS NIÑOS", "LA GENTE NORMAL PIENSA QUE SON SIMPLES RUMORES DE INTERNET", "DURANTE AÑOS SE PUSO LA EXCUSA DE QUE ERA UN FENOMENO NATURAL"]
        descubrimientos = ["HASTA QUE UNA CAMARA DE SEGURIDAD GRABO ALGO INEXPLICABLE", "PERO UN GRUPO DE EXPLORADORES ENCONTRO LA VERDADERA PRUEBA EN LA OSCURIDAD", "SIN EMBARGO LOS REGISTROS POLICIALES MUESTRAN SUCESOS ESCALOFRIANTES"]
        giros = ["LO PEOR ES QUE LA ENTIDAD NUNCA SE FUE SINO QUE SIGUE ACECHANDO", "Y SE DIERON CUENTA DE QUE LAS VICTIMAS TENIAN ALGO MACABRO EN COMUN", "DEMOSTRANDO QUE EL MAL REALMENTE EXISTE Y ESTA BUSCANDO SU PROXIMA PRESA"]
        finales = ["AHORA QUE LO SABES NO VUELVAS A APAGAR LA LUZ SIGUENOS PARA MAS TERROR", "EL VERDADERO HORROR ES QUE ESTO PODRIA PASARTE A TI SIGUENOS PARA MAS MISTERIOS", "LA MALDICION ESTA SUELTA Y NADIE ESTA A SALVO SIGUENOS SI TE ATREVES"]
    
    elif nicho == "negocios":
        ganchos = ["ESTE ES EL SECRETO QUE LOS MULTIMILLONARIOS TE ESTAN OCULTANDO SOBRE", "LA MAYOR TRANSFERENCIA DE RIQUEZA ESTA A PUNTO DE OCURRIR CON", "SI QUIERES HACER DINERO REAL TIENES QUE ENTENDER ESTO SOBRE"]
        creencias = ["EL SISTEMA EDUCATIVO NOS ENSEÑO A IGNORAR ESTAS OPORTUNIDADES", "LA MAYORIA PIERDE EL TIEMPO EN METODOS TRADICIONALES QUE YA NO FUNCIONAN", "NOS VENDIERON LA IDEA DE QUE SE NECESITA MUCHO CAPITAL PARA EMPEZAR"]
        descubrimientos = ["PERO LOS NUEVOS EMPRENDEDORES ESTAN USANDO UNA ESTRATEGIA TOTALMENTE DIFERENTE", "HASTA QUE UN ANALISTA REVELO EL PATRON EXACTO QUE GENERA GANANCIAS MASIVAS", "SIN EMBARGO LOS DATOS DEMUESTRAN QUE EL MERCADO HA CAMBIADO PARA SIEMPRE"]
        giros = ["EL TRUCO ESTA EN APROVECHAR LAS TENDENCIAS ANTES DE QUE SE HAGAN PUBLICAS", "Y LA CLAVE ES SISTEMATIZAR EL PROCESO PARA QUE FUNCIONE EN PILOTO AUTOMATICO", "DEMOSTRANDO QUE LA VERDADERA RIQUEZA SE CREA ROMPIENDO LAS REGLAS ESTABLECIDAS"]
        finales = ["APLICA ESTA ESTRATEGIA Y TU CUENTA BANCARIA EXPLOTARA SIGUENOS PARA MAS TIPS", "TOMA ACCION HOY MISMO ANTES DE QUE EL MERCADO SE SATURE SIGUENOS PARA MAS NEGOCIOS", "ESTA ES TU OPORTUNIDAD PARA ESCAPAR DEL SISTEMA TRADICIONAL SIGUENOS PARA CRECER"]
    
    else: # Conspiración / Documental Clásico
        ganchos = ["PRESTA MUCHA ATENCION PORQUE NADIE TE ESTA CONTANDO LA VERDAD SOBRE", "HAY UN MISTERIO MUY OSCURO QUE LA ELITE INTENTA OCULTAR SOBRE", "EL GOBIERNO HA GASTADO MILLONES EN OCULTAR ESTE SECRETO SOBRE"]
        creencias = ["SIEMPRE NOS HAN HECHO CREER QUE ES ALGO COMPLETAMENTE INOFENSIVO Y NORMAL", "LA MAYORIA DE LA GENTE PIENSA QUE FUNCIONA DE FORMA TRANSPARENTE Y SEGURA", "LA HISTORIA OFICIAL SIEMPRE HA DICHO QUE NO HABIA NADA EXTRAÑO AQUI"]
        descubrimientos = ["PERO HACE POCO UNOS INVESTIGADORES INDEPENDIENTES FILTRARON PRUEBAS REALES", "SIN EMBARGO UN HACKER LOGRO ENTRAR A LOS SERVIDORES PRIVADOS Y VIO LOS DATOS", "HASTA QUE UN DOCUMENTO CLASIFICADO SALIO A LA LUZ POR COMPLETO ACCIDENTE"]
        giros = ["Y SE DIERON CUENTA DE QUE EL VERDADERO PROPOSITO ERA MANIPULAR NUESTRAS DECISIONES", "REVELANDO QUE TODO ES UN NEGOCIO MULTIMILLONARIO PARA MANTENERNOS ESTANCADOS", "DEMOSTRANDO QUE TODO HABIA SIDO CALCULADO AL MILIMETRO PARA TENERNOS BAJO CONTROL"]
        finales = ["AHORA QUE SABES ESTO TIENES LA VENTAJA DEFINITIVA SOBRE EL SISTEMA SIGUENOS PARA MAS SECRETOS", "EL ENGAÑO HA TERMINADO Y LA HISTORIA OFICIAL QUEDA DESTRUIDA SIGUENOS PARA MAS MISTERIOS", "ESTE DESCUBRIMIENTO LO CAMBIA TODO Y NO HAY VUELTA ATRAS SIGUENOS PARA MAS VERDADES"]
        
    return f"{random.choice(ganchos)} {tema} {random.choice(creencias)} {random.choice(descubrimientos)} {random.choice(giros)} {random.choice(finales)}"

def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    nicho = detectar_nicho(orden_usuario)
    
    # Adaptar palabras clave visuales según el nicho para Pexels
    if nicho == "terror": sufijo = "creepy dark"
    elif nicho == "negocios": sufijo = "money success"
    else: sufijo = "cinematic epic"
        
    keys = [p for p in limpias[:3]] + [f"{p} {sufijo}" for p in limpias[:2]]
    if not keys: keys = [sufijo]

    guion_fallback = generar_guion_procedural(tema_mostrar, nicho)
    semilla = random.randint(100000, 9999999)
    
    # La IA también recibe instrucciones específicas según el nicho
    if nicho == "terror":
        prompt_maestro = f"Crea un guion viral TERRORIFICO Y PARANORMAL. TEMA: '{orden_usuario}'. ESTRUCTURA: 1. Gancho que de mucho miedo. 2. Historia escalofriante o leyenda oscura. 3. FINAL: Cierra con miedo y añade EXACTAMENTE la frase 'SIGUENOS PARA MAS TERROR'. REGLAS: TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."
    elif nicho == "negocios":
        prompt_maestro = f"Crea un guion viral DE NEGOCIOS Y EMPRENDIMIENTO. TEMA: '{orden_usuario}'. ESTRUCTURA: 1. Gancho sobre dinero o exito. 2. Estrategia de negocio o caso de exito real. 3. FINAL: Cierra con una leccion de riqueza y añade EXACTAMENTE la frase 'SIGUENOS PARA MAS NEGOCIOS'. REGLAS: TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."
    else:
        prompt_maestro = f"Crea un guion viral UNICO DE MISTERIO O CONSPIRACION. TEMA: '{orden_usuario}'. ESTRUCTURA: 1. Gancho explosivo. 2. Desarrollo misterioso con datos reales. 3. FINAL: Concluye la historia y añade EXACTAMENTE la frase 'SIGUENOS PARA MAS SECRETOS'. REGLAS: TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."

    try:
        res_1 = requests.get("https://sentence.fineshopdesign.com/api/ai", params={"prompt": prompt_maestro, "seed": semilla}, timeout=12)
        if res_1.status_code == 200 and es_texto_valido(res_1.json().get("reply", "")):
            gl = limpiar_texto_ia(res_1.json().get("reply", ""))
            if len(gl) > 60: return gl, keys, tema_mostrar
    except: pass

    try:
        res_2 = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}", timeout=12)
        if res_2.status_code == 200 and es_texto_valido(res_2.text):
            gl = limpiar_texto_ia(res_2.text)
            if len(gl) > 60: return gl, keys, tema_mostrar
    except: pass
            
    return guion_fallback, keys, tema_mostrar

def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.')
    partes = t_str.split(':')
    if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
    elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
    else: return float(partes[0])

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111432.png", width=50)
    st.header("⚙️ Panel de Agencia")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Estilo Subtítulos", ["yellow", "white", "cyan", "#00FF00"])
    st.markdown("---")
    st.caption("Fénix System | Inteligencia Multi-Nicho Activa ✅")

if orden := st.chat_input("Introduzca el tema del vídeo a generar..."):
    with st.status(f"🚀 Iniciando Motor... Analizando nicho de '{orden}'", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        nicho_detectado = detectar_nicho(orden)
        status.write(f"✓ Nicho detectado: **{nicho_detectado.upper()}**. Guion y visuales adaptados.")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        if not dur_audio_str: dur_audio_str = "40.0"
        dur_audio = float(dur_audio_str)

        # Música de fondo adaptada al nicho
        tono = 50 if nicho_detectado == "terror" else 75
        ruido = 0.05 if nicho_detectado == "terror" else 0.02
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a={ruido}" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
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
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{current_time},{current_time+duracion_chunk})'")
                                current_time += duracion_chunk
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except: pass

        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"🎞️ Sincronizando imágenes ({nicho_detectado})...")
        palabras_guion = guion.split()
        chunk_size = max(1, len(palabras_guion) // max(1, num_clips))
        stop_words = {"PRESTA", "MUCHA", "ATENCION", "PORQUE", "QUE", "TE", "VOY", "A", "CONTAR", "SOBRE", "EL", "LA", "LOS", "LAS", "UN", "UNA", "UNOS", "UNAS", "CON", "SIN", "PARA", "POR", "DE", "DEL", "Y", "O", "ES", "SON", "HA", "HAN", "SE", "LO", "LE", "NO", "MAS", "ESTO", "ESTA", "ESTAS", "ESTOS", "TODO", "PERO", "SI", "COMO", "CUANDO", "DONDE", "AQUI", "ALLI", "MUY", "TAN", "SU", "SUS", "AL", "NOS", "MI", "MIS", "ENTRE", "HAY", "ESTE", "AUNQUE", "HASTA", "DESDE", "ENTONCES", "TIENES", "SIGUENOS", "AHORA", "ELLOS", "MUNDO", "TIEMPO", "SOLO"}
        
        last_valid_clip = None
        for i in range(num_clips): 
            inicio = int(i * chunk_size)
            fin = int((i + 1) * chunk_size)
            trozo = palabras_guion[inicio:fin]
            
            palabras_utiles = [p for p in trozo if p not in stop_words and len(p) > 4]
            busquedas_a_intentar = []
            
            # Buscamos las palabras del guion, pero les añadimos el tono del nicho (creepy, money, cinematic)
            sufijo_nicho = "creepy" if nicho_detectado == "terror" else ("money" if nicho_detectado == "negocios" else "cinematic")
            
            if palabras_utiles:
                palabras_utiles.sort(key=len, reverse=True)
                busquedas_a_intentar.append(f"{palabras_utiles[0]} {sufijo_nicho}")
                if len(palabras_utiles) > 1:
                    busquedas_a_intentar.append(f"{palabras_utiles[1]} {sufijo_nicho}")
            
            busquedas_a_intentar.extend(palabras_claves)
            
            v_url = None
            for busqueda in busquedas_a_intentar:
                try:
                    res = requests.get(f"https://api.pexels.com/videos/search?query={busqueda}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                    videos = res.get('videos', [])
                    if videos:
                        v_url = random.choice(videos)['video_files'][0]['link']
                        status.write(f"  ► Clip {i+1}: Imagen sincronizada para '{busqueda}'")
                        break
                except: pass
            
            try:
                if v_url:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=720x1280,fps=30" -an -c:v libx264 -preset veryfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                    last_valid_clip = f"p_{i}.mp4"
                else: raise Exception("Error")
            except:
                if last_valid_clip: subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={clip_duration}:r=30 -c:v libx264 -preset veryfast p_{i}.mp4', shell=True)
            processed_clips.append(f"p_{i}.mp4")

        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=3:r=30 -vf "drawtext=text=\'FÉNIX STUDIO 🦅\':fontcolor=white:fontsize=55:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset veryfast outro.mp4', shell=True)
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Renderizando Master Final HD...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Video completado con adaptación de nicho.")
            st.video(v_final)
