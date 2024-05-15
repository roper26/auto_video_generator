from app.services import picture_video
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
        "font_name": "STHeitiMedium.ttc",
        "text_color": "#FFFFFF",
        "font_size": 120,
        "stroke_color": "#000000",
        "subtitle_position": "bottom",
        "stroke_width": 1.5
    }

params = VideoParams(**params_dict)
srt_file_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/subtitle.srt'
sound_file_path = '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/audio.mp3' 


picture_video.create_picture_video(
    sound_file_path, 
    srt_file_path, 
    '/Users/roper/work/auto_video_generator/storage/tasks/task_id_test_123/output.mp4', 
    params,
    )