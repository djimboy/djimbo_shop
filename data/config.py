# - *- coding: utf- 8 - *-
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
BOT_TOKEN = config["settings"]["token"]
admins = config["settings"]["admin_id"]
if "," in admins:
    admins = admins.split(",")
else:
    if len(admins) >= 1:
        admins = [admins]
    else:
        admins = []
        print("***** Вы не указали админ ID *****")

bot_version = "2.9"
bot_description = f"<b>♻ Bot created by @djimbox</b>\n" \
                  f"<b>⚜ Bot Version:</b> <code>{bot_version}</code>\n" \
                  f"<b>🔗 Topic Link:</b> <a href='https://lolz.guru/threads/1888814/'><b>Click me</b></a>\n" \
                  f"<b>🍩 Donate to the author:</b> <a href='https://yoomoney.ru/to/410012580032553'><b>Click me</b></a>"
