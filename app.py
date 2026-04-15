import streamlit as st
import os, time, random, subprocess, requests, math, re

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

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v8.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Cerebro Simulado • Plantillas Variables Infinitas</div>', unsafe_allow_html=True)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden, limpias

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "oscuridad", "demonio", "maldito", "asesino", "leyenda", "creepy"]): return "terror"
    elif any(w in t for w in ["negocio", "dinero", "invertir", "inversion", "empresa", "millonario", "finanzas", "cripto", "emprendedor", "ventas", "marketing", "riqueza", "dolares"]): return "negocios"
    else: return "misterio"

# --- LA ILUSIÓN DE LA IA: ARCOS NARRATIVOS CON VARIABLES ---
def generar_falsa_ia(tema, nicho):
    tema = tema.upper()
    
    # 1. Creamos el diccionario de variables (El bot "inventa" datos)
    variables = {
        "tema": tema,
        "año": random.choice(["DOS MIL OCHO", "MIL NOVECIENTOS NOVENTA Y NUEVE", "DOS MIL QUINCE", "EL AÑO DOS MIL VEINTE", "MIL NOVECIENTOS OCHENTA"]),
        "enemigo_negocio": random.choice(["LOS BANCOS CENTRALES", "LA ELITE DE WALL STREET", "LAS GRANDES CORPORACIONES", "LOS MULTIMILLONARIOS DEL FORO ECONOMICO"]),
        "enemigo_misterio": random.choice(["EL GOBIERNO", "UNA AGENCIA DE INTELIGENCIA SECRETA", "EL VATICANO", "UN GRUPO MILITAR CLASIFICADO"]),
        "porcentaje": random.choice(["NOVENTA Y NUEVE", "NOVENTA Y CINCO", "OCHENTA Y OCHO", "NOVENTA"]),
        "dinero": random.choice(["MILLONES DE DOLARES", "FORTUNAS INMENSA", "TODO SU CAPITAL EN SEGUNDOS"]),
        "lugar_creepy": random.choice(["UN HOSPITAL ABANDONADO", "LOS BOSQUES DEL NORTE", "UNA CUEVA SELLADA", "LOS SOTANOS DE UNA IGLESIA ANTIGUA"]),
        "tiempo_misterio": random.choice(["SETENTA Y DOS HORAS", "UNA SEMANA", "TRES DIAS", "UN MES ENTERO"]),
    }

    # 2. Plantillas MAESTRAS. Tienen principio, nudo y final perfectos. Nunca pierden el sentido.
    if nicho == "negocios":
        plantillas = [
            "EL {porcentaje} POR CIENTO DE LAS PERSONAS PIERDE {dinero} CUANDO INTENTA ENTRAR EN EL MUNDO DE {tema} Y NO ES POR CASUALIDAD EN {año} {enemigo_negocio} DISEÑARON UN SISTEMA PERFECTO PARA QUE EL CIUDADANO COMUN FRACASARA LA ESTRATEGIA ERA MANTENER ESTA INFORMACION OCULTA MIENTRAS ELLOS MULTIPLICABAN SUS INGRESOS PERO UN ANALISTA FINANCIERO FILTRO LA FORMULA EXACTA RESULTA QUE LA CLAVE ESTA EN HACER EXACTAMENTE LO CONTRARIO A LO QUE ENSEÑAN EN LAS NOTICIAS CUANDO TODOS COMPRAN TU VENDES Y CUANDO HAY PANICO TU ATACAS AHORA QUE CONOCES ESTE TRUCO EL SISTEMA YA NO PUEDE ROBARTE APLICALO HOY MISMO Y TU VIDA CAMBIARA SIGUENOS PARA MAS NEGOCIOS",
            
            "TE ESTAN ROBANDO EN TU PROPIA CARA CON {tema} Y LA ESCUELA TE ENSEÑO A ACEPTARLO TODO COMENZO EN {año} CUANDO {enemigo_negocio} SE DIERON CUENTA DE QUE PODIAN CONTROLAR EL MERCADO SI MANTENIAN A LA POBLACION IGNORANTE EL SECRETO MEJOR GUARDADO ES QUE NO NECESITAS {dinero} PARA EMPEZAR SOLO NECESITAS ENTENDER COMO FLUYE EL CAPITAL UN JOVEN EMPRENDEDOR DESCUBRIO ESTA FALLA EN EL SISTEMA Y ROMPIO LAS REGLAS GENERANDO GANANCIAS MASIVAS EN TIEMPO RECORD LA LOGICA ES SIMPLE DEJA DE CAMBIAR TU TIEMPO POR DINERO Y HAZ QUE EL ALGORITMO TRABAJE PARA TI EL JUEGO ESTA ROTO APROVECHALO SIGUENOS PARA MAS NEGOCIOS"
        ]
    elif nicho == "terror":
        plantillas = [
            "NO MIRES ESTE VIDEO DE NOCHE SI LE TEMES A {tema} TODO EL MUNDO PIENSA QUE ES UNA SIMPLE LEYENDA URBANA PERO EN {año} LA POLICIA ENCONTRO ALGO MACABRO EN {lugar_creepy} HABIA GRABACIONES DE SEGURIDAD QUE MOSTRABAN LO INEXPLICABLE LOS ARCHIVOS FUERON CLASIFICADOS DE INMEDIATO PERO UN INVESTIGADOR LOGRO EXTRAER LOS VIDEOS ANTES DE QUE LO SILENCIARAN LA AUTOPSIA REVELO QUE LAS VICTIMAS COMPARTIAN EL MISMO PATRON EXTRAÑO LO MAS ATERRADOR ES QUE ESTA ENTIDAD NO ESTA ENCERRADA SIGUE BUSCANDO A QUIEN ROMPA LAS REGLAS SI ESCUCHAS UN RUIDO EXTRAÑO HOY NO ABRAS LA PUERTA SIGUENOS PARA MAS TERROR",
            
            "ESTA ES LA HISTORIA MAS ATERRADORA Y REAL SOBRE {tema} DURANTE AÑOS LOS HABITANTES DE LA ZONA HABLABAN EN SUSURROS SOBRE LO QUE PASO EN {año} DENTRO DE {lugar_creepy} EL GOBIERNO MANDO A UN GRUPO DE EXPERTOS A INVESTIGAR PERO DESAPARECIERON DURANTE {tiempo_misterio} CUANDO LOS ENCONTRARON HABIAN PERDIDO LA CORDURA Y SOLO REPETIAN UNA FRASE EN BUCLE DESCUBRIERON QUE HABIAN DESPERTADO ALGO QUE LLEVABA SIGLOS DORMIDO LA VERDAD ES TAN PERTURBADORA QUE DECIDIERON BORRARLA DE LOS REGISTROS OFICIALES PERO EL MAL NUNCA SE FUE DEL TODO MIRA DETRAS DE TI AHORA MISMO SIGUENOS PARA MAS TERROR"
        ]
    else:
        plantillas = [
            "TE HAN MENTIDO TODA TU VIDA SOBRE {tema} LOS LIBROS DE HISTORIA TE CUENTAN UNA VERSION REDUCIDA PORQUE EN {año} {enemigo_misterio} DECIDIO QUE LA HUMANIDAD NO ESTABA LISTA PARA SABER LA VERDAD UN EX EMPLEADO ROMPIO SU CONTRATO DE SILENCIO Y FILTRO DOCUMENTOS DE LA DEEP WEB QUE LO CAMBIAN TODO RESULTA QUE ESTA TECNOLOGIA YA SE USABA HACE MILENIOS PERO FUE OCULTADA PARA MANTENER EL CONTROL SOBRE LA POBLACION EL {porcentaje} POR CIENTO DE LA GENTE SIGUE CREYENDO LA MENTIRA OFICIAL PERO LAS PRUEBAS MATEMATICAS NO MIENTEN TODO ESTA CONECTADO DESDE EL PRINCIPIO DESPIERTA DE UNA VEZ Y NO CREAS NADA DE LO QUE TE DICEN SIGUENOS PARA MAS SECRETOS",
            
            "BORRARAN ESTE VIDEO EN HORAS PORQUE REVELA LA VERDAD DETRAS DE {tema} DURANTE DECADAS CREIMOS QUE ERA ALGO INOFENSIVO PERO LA REALIDAD SUPERA A LA FICCION DOCUMENTOS DESCLASIFICADOS DEMUESTRAN QUE EN {año} {enemigo_misterio} LLEVO A CABO EXPERIMENTOS SECRETOS RELACIONADOS CON ESTO EL OBJETIVO FINAL ERA MANIPULAR NUESTRA MENTE SIN QUE NOS DIERAMOS CUENTA UN CIENTIFICO LOGRO ESCAPAR CON LOS DISCOS DUROS Y EXPUSO EL PLAN MAESTRO AUNQUE INTENTARON SILENCIARLO LA INFORMACION YA ESTA EN LA RED EL ENGAÑO HA TERMINADO Y AHORA TIENES EL PODER DE VER LA REALIDAD SIGUENOS PARA MAS MISTERIOS"
        ]
    
    # Elegimos una plantilla y rellenamos los huecos mágicamente
    guion_final = random.choice(plantillas).format(**variables)
    return guion_final

def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    nicho = detectar_nicho(orden_usuario)
    
    if nicho == "terror": sufijo = "creepy dark"
    elif nicho == "negocios": sufijo = "money success"
    else: sufijo = "cinematic epic"
        
    keys = [p for p in limpias[:3]] + [f"{p} {sufijo}" for p in limpias[:2]]
    if not keys: keys = [sufijo]

    # AQUÍ ESTÁ EL TRUCO: Ya no llamamos a ninguna IA externa. El Cerebro Simulado es instantáneo y perfecto.
    guion = generar_falsa_ia(tema_mostrar, nicho)
    return guion, keys, tema_mostrar

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
    st.caption("Fénix System | Cerebro Simulado Activo ✅")

if orden := st.chat_input("Introduzca el tema (Lógica 100% Humana):"):
    with st.status(f"🚀 Generando guion inteligente para '{orden}'", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        # Generación instantánea
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        nicho_detectado = detectar_nicho(orden)
        status.write(f"✓ Nicho: **{nicho_detectado.upper()}**. Guion perfecto inyectado.")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        if not dur_audio_str: dur_audio_str = "40.0"
        dur_audio = float(dur_audio_str)

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
        
        status.write(f"🎞️ Sincronizando imágenes HD...")
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

        status.write("✨ Renderizando Master Definitivo...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Video completado con Lógica Perfecta.")
            st.video(v_final)
