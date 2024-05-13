import pysrt
from pysrt import SubRipFile
from moviepy.editor import *

srt_file_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/subtitle.srt'
sound_file_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/audio.mp3' 

temp_files = ['/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpo0wr901h.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp11iyujh7.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpzg6jus_p.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpjsdzvnm2.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpt8o3xo1x.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpr_r70tv3.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp3riwsjsp.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp_vuw60mo.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpqfq4zmo4.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp8mefqjnn.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpz80d_d38.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmppzykwczt.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpad34y5t4.jpg',
 '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpv40y8fhi.jpg']


# 读取字幕文件
subs = pysrt.open(srt_file_path)


clips = []
i = 0
total_dur = 0
for i in range(len(subs)):
    sub = subs[i]
    dur = sub.duration.seconds + sub.duration.milliseconds / 1000
    if i < len(subs) - 1:
        tmp_dur = subs[i+1].start - sub.start
        dur = tmp_dur.seconds + tmp_dur.milliseconds / 1000
    
    picture = temp_files[i]
    if i < len(temp_files) - 1:
        i += 1

    print(f'start handle sub:{sub}, duration:{dur} durmili:{sub.duration.milliseconds}, picture:{picture}')

    if dur <= 0:
        print(f'duration <= 0, skip')
        continue
    
    total_dur += dur
   
    if False == os.path.exists(picture):
        print(f'picture not exists:{picture}')
        continue
    
    # 创建一个图片剪辑
    img_clip = ImageClip(picture).set_duration(dur)
    
    # 将剪辑添加到列表中
    clips.append(img_clip)

print(f'total_dur:{total_dur}')

# 合并所有视频片段
video = concatenate_videoclips(clips, method="compose")

 # Load the audio file
audio = AudioFileClip(sound_file_path)

# Set the audio of the concatenated video clip
final_video = video.set_audio(audio)

# Set the duration of the final video to match the audio duration
final_video = final_video.set_duration(audio.duration)


final_video.write_videofile("test.mp4", fps=5)