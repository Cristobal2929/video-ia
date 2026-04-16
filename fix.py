import re

with open('app.py', 'r') as f:
    code = f.read()

# 1. Quitamos el loop que atascaba los clips
code = code.replace('-stream_loop -1 -i', '-i')

# 2. Hacemos que el video se adapte a la voz EXACTA y forzamos que se vea en Chrome
code = re.sub(r'cmd = .*', 'cmd = f"ffmpeg -y {inputs} -i \\"t.mp3\\" -filter_complex \\"{filt}\\" -map \\"[outv]\\" -map 5:a -c:v libx264 -pix_fmt yuv420p -movflags +faststart -shortest \\"{final_p}\\""', code)

with open('app.py', 'w') as f:
    f.write(code)
