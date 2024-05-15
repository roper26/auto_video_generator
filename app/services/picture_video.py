import pysrt
from app.services.llm import generate_picture_term
from app.services.material import search_picture
from loguru import logger
from moviepy.editor import *
from app.services.video import wrap_text
from app.utils import utils
from app.models.schema import VideoParams, VideoAspect
import requests
from tempfile import NamedTemporaryFile
import os

def download_image(url):
    # Download the image and return the path to the temporary file
    response = requests.get(url)
    if response.status_code == 200:
        temp_file = NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"Failed to download image from {url}")


def get_picture_for_subtitle(video_subject, subtitle_path):
    subs = pysrt.open(subtitle_path)
    picture_urls = []
    for sub in subs:
        subtitle_str = sub.text
        search_term = generate_picture_term(video_subject, subtitle_str)
        pic = search_picture(search_term)
        picture_urls.append(pic)
        logger.info(f'len pics:{len(picture_urls)}, pic:{pic}')

    pictures = []
    for pic_url in picture_urls:
        logger.info(f'pic_url:{pic_url}')
        picture = download_image(pic_url)
        pictures.append(picture)
    
    return pictures


def create_text_clip(sub, params, font_path, video_width, video_height):
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



def create_picture_video(
                   audio_path: str,
                   subtitle_path: str,
                   output_file: str,
                   params: VideoParams):
    aspect = VideoAspect(params.video_aspect)
    video_width, video_height = aspect.to_resolution()

    logger.info(f"start, video size: {video_width} x {video_height}")
    logger.info(f"  ② audio: {audio_path}")
    logger.info(f"  ③ subtitle: {subtitle_path}")
    logger.info(f"  ④ output: {output_file}")

    output_dir = os.path.dirname(output_file)

    font_path = ""
    if params.subtitle_enabled:
        if not params.font_name:
            params.font_name = "STHeitiMedium.ttc"
        font_path = os.path.join(utils.font_dir(), params.font_name)
        if os.name == 'nt':
            font_path = font_path.replace("\\", "/")

        logger.info(f"using font: {font_path}")


    # subtitle_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/subtitle.srt'
    # audio_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/audio.mp3' 

    pictures = get_picture_for_subtitle(params.video_subject, subtitle_path)
    
    # pictures = ['/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpo0wr901h.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp11iyujh7.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpzg6jus_p.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpjsdzvnm2.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpt8o3xo1x.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpr_r70tv3.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp3riwsjsp.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp_vuw60mo.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpqfq4zmo4.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmp8mefqjnn.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpz80d_d38.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmppzykwczt.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpad34y5t4.jpg',
    #  '/var/folders/20/h5ktr5ls0zgdjw1dtlxcrlpc0000gn/T/tmpv40y8fhi.jpg']



    # 读取字幕文件
    subs = pysrt.open(subtitle_path)


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
            cur_pic = pictures[i]
            cur_total_duration = 0

        if cur_pic == None:
            cur_pic = pictures[i]

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
        text_clip = create_text_clip(sub, params, font_path, video_width, video_height).set_duration(dur)
        video_clip = CompositeVideoClip([img_clip, text_clip])

        # 将剪辑添加到列表中
        clips.append(video_clip)


    print(f'total_dur:{total_dur}')

    # 合并所有视频片段
    video = concatenate_videoclips(clips, method="compose")

     # Load the audio file
    audio = AudioFileClip(audio_path)

    # Set the audio of the concatenated video clip
    final_video = video.set_audio(audio)

    # Set the duration of the final video to match the audio duration
    final_video = final_video.set_duration(audio.duration)


    final_video.write_videofile(output_file, fps=5)

    return output_file