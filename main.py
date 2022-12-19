from pytube import YouTube
import telebot
import os
import datetime
import moviepy.editor
from config import settings

bot=telebot.TeleBot(settings["token"])

def extract_audio(file):
    (moviepy.editor.VideoFileClip(file)).audio.write_audiofile(file.split(".")[0] + ".mp3")
    os.remove(file)
    return file.split(".")[0] + ".mp3"




@bot.message_handler(commands=["start"])
def start(ctx):
    bot.send_message(chat_id=ctx.chat.id, text = "Hey, send me a Youtube link or a video and I will extract the audio for you!")

@bot.message_handler(content_types=['text'])
def all_messages(message):
    if "https://" in message.text or "www." in message.text:
        yt = YouTube(message.text)
        bot.send_message(chat_id = message.chat.id , text = f"""Title: {yt.title}\nNumber of views: {yt.views}\nLength of video: {datetime.timedelta(seconds=yt.length)}""")
        bot.send_message(chat_id = message.chat.id , text = "Downloading...")
        yt.streams.get_highest_resolution().download("videos/")
        bot.send_message(chat_id = message.chat.id , text = "Download completed!!!")
        bot.send_message(chat_id = message.chat.id , text = "Converting...")
        title = yt.title
        for i in  "\/?:*><|.,":
            title = title.replace(i, "")
        file = extract_audio(f"videos/{title}.mp4")
        bot.send_audio(chat_id = message.chat.id, audio = open(file, 'rb'))
        os.remove(file)

@bot.message_handler(content_types=['video'])
def handle_docs(message):
    bot.send_message(chat_id = message.chat.id , text = "Downloading...")
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_info.file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    os.rename(file_info.file_path, f"videos/{message.video.file_name}")
    bot.send_message(chat_id = message.chat.id , text = "Download completed!!!")
    title = message.video.file_name[:-4]
    for i in  "\/?:*><|.,":
        title = title.replace(i, "")
    bot.send_message(chat_id = message.chat.id , text = "Converting...")
    file = extract_audio(f"videos/{title}.mp4")
    bot.send_audio(chat_id = message.chat.id, audio = open(file, 'rb'))
    os.remove(file)


if __name__ == "__main__":
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    print("BOT_CONNECTED")
    bot.polling(none_stop=True, interval=0, skip_pending=True)