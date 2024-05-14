import pysrt
from pysrt import SubRipFile
from moviepy.editor import *
from app.services.video import wrap_text
from app.utils import utils
from app.models.schema import VideoParams, VideoAspect

video_width = 1080
video_height = 1920
font_name = "STHeitiMedium.ttc"
font_path = os.path.join(utils.font_dir(), font_name)
font_size = 60
params_dict = {
        "video_subject": "怎么快速赚到100万",
        "video_aspect": "9:16",
        "voice_name": "zh-CN-XiaoxiaoNeural",
        "enable_bgm": False,
        "font_name": "STHeitiMedium 黑体-中",
        "text_color": "#FFFFFF",
        "font_size": 120,
        "stroke_color": "#000000",
        "subtitle_position": "bottom",
        "stroke_width": 1.5
    }

params = VideoParams(**params_dict)

aspect = VideoAspect(params.video_aspect)
video_width, video_height = aspect.to_resolution()

def create_text_clip(sub):
        phrase = sub.text
        max_width = video_width * 0.9
        wrapped_txt, txt_height = wrap_text(phrase,
                                            max_width=max_width,
                                            font=font_path,
                                            fontsize=params.font_size
                                            )
        _clip = TextClip(
            wrapped_txt,
            font=font_path,
            fontsize=params.font_size,
            color=params.text_fore_color,
            bg_color=params.text_background_color,
            stroke_color=params.stroke_color,
            stroke_width=params.stroke_width,
            print_cmd=False,
        )
        # duration = sub.duration.seconds + sub.duration.milliseconds / 1000
        # _clip = _clip.set_start(sub.start.seconds + sub.start.milliseconds / 1000)
        # _clip = _clip.set_end(sub.end.seconds + sub.end.milliseconds / 1000)
        # _clip = _clip.set_duration(duration)
        if params.subtitle_position == "bottom":
            _clip = _clip.set_position(('center', video_height * 0.95 - _clip.h))
        elif params.subtitle_position == "top":
            _clip = _clip.set_position(('center', video_height * 0.1))
        else:
            _clip = _clip.set_position(('center', 'center'))
        return _clip

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
cur_pic = None
cur_total_duration = 0
for i in range(len(subs)):
# for i in range(3):

    sub = subs[i]
    dur = sub.duration.seconds + sub.duration.milliseconds / 1000
    if i < len(subs) - 1:
        tmp_dur = subs[i+1].start - sub.start
        dur = tmp_dur.seconds + tmp_dur.milliseconds / 1000
    
    cur_total_duration += dur
    if cur_total_duration > 2:
        # 每超过2秒就更新图片
        print(f'use new Image, cur_total_duration:{cur_total_duration}')
        cur_pic = temp_files[i]
        cur_total_duration = 0

    if cur_pic == None:
        cur_pic = temp_files[i]

    print(f'start handle sub:{sub}, duration:{dur} durmili:{sub.duration.milliseconds}, picture:{cur_pic}')

    if dur <= 0:
        print(f'duration <= 0, skip')
        continue
    
    total_dur += dur
   
    if False == os.path.exists(cur_pic):
        print(f'cur_pic not exists:{cur_pic}')
        continue
    
    # 创建一个图片剪辑
    img_clip = ImageClip(cur_pic).set_duration(dur).resize((video_width, video_height))

    # text_clip = TextClip(sub.text, fontsize=70, color='white', size=img_clip.size).set_position(('center', 'bottom')).set_duration(dur)
    text_clip = create_text_clip(sub).set_duration(dur)
    video_clip = CompositeVideoClip([img_clip, text_clip])

    # 将剪辑添加到列表中
    clips.append(video_clip)


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