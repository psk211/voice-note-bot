import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import whisper
import subprocess

OWNER_ID = int(os.getenv("OWNER_ID"))  # ID владельца
TOKEN = os.getenv("BOT_TOKEN")  # токен бота

model = whisper.load_model("base")

logging.basicConfig(level=logging.INFO)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive("voice.ogg")

    subprocess.run(["ffmpeg", "-i", "voice.ogg", "voice.wav", "-y"])

    result = model.transcribe("voice.wav")
    text = result["text"].strip()

    if len(text) <= 2500:
        await update.message.reply_text(f"Заметка:\n\n{text}")
    else:
        with open("note.txt", "w", encoding="utf-8") as f:
            f.write(text)
        await update.message.reply_document(document=open("note.txt", "rb"), filename="long_note.txt")

    os.remove("voice.ogg")
    os.remove("voice.wav")
    if os.path.exists("note.txt"):
        os.remove("note.txt")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

if __name__ == "__main__":
    app.run_polling()
