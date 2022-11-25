import os
import datetime
import pyttsx3
import librosa
import soundfile as sf

def text_to_speech(prompt):
    folder_path = "audio_file"
    os.makedirs(folder_path, exist_ok=True)

    time_now = datetime.datetime.now()
    file_name = time_now.strftime('%Y-%m-%d-%H%M%S')

    engine = pyttsx3.init()
    print(prompt)
    
    #保存パスの設定
    save_file_path = f"{os.getcwd()}/audio_file/{file_name}.wav"

    engine.save_to_file(prompt, save_file_path)
    engine.runAndWait()

    #pyttsx3で生成した音声がそのままmaxで読み込めないので、librosaで整形し直す。
    y, sr = librosa.load(save_file_path, sr=44100, mono=False)
    os.remove(save_file_path)
    sf.write(save_file_path, y, sr, subtype="PCM_16")

    return save_file_path