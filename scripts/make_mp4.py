import subprocess, os
# build a concat file for ffmpeg
lines=[]
for i in range(1,7):
    dur = 2.2 if i<6 else 3.6
    lines.append(f"file 'gif_{i}.png'")
    lines.append(f"duration {dur}")
lines.append("file 'gif_6.png'")
open('build/concat.txt','w',encoding='utf-8').write("\n".join(lines))
cmd=['ffmpeg','-y','-f','concat','-safe','0','-i','build/concat.txt',
     '-vf','scale=1440:-2,format=yuv420p','-r','25','-c:v','libx264','-crf','18','-preset','medium',
     'output/interactions_komi.mp4']
r=subprocess.run(cmd, capture_output=True, text=True)
print(r.returncode)
print(r.stderr[-500:])
print(round(os.path.getsize('output/interactions_komi.mp4')/1e6,2),'MB')
