import os
import datetime
from gtts import gTTS
import soundfile as sf

def text_to_speech(prompt):
    folder_path = "audio_file"
    os.makedirs(folder_path, exist_ok=True)

    time_now = datetime.datetime.now()
    file_name = time_now.strftime('%Y-%m-%d-%H%M%S')

    print(prompt)
    
    #保存パスの設定
    save_file_path = f"{os.getcwd()}/audio_file/{file_name}.wav"

    tts = gTTS(text=prompt, lang="ja") # 日本語
    tts.save(save_file_path)

    return save_file_path