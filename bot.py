#dev: @yummy1gay

from telethon import TelegramClient, events, Button
from telethon.tl.functions.messages import EditInlineBotMessageRequest
from telethon.tl.types import UpdateBotInlineSend, MessageEntityBold, MessageEntityTextUrl, InputMediaDocumentExternal
import emoji
import requests
import os
from config import *

client = TelegramClient('TikTok', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('👋 <i>Привет! Я бот, который скачивает видео с TikTok. Просто отправь мне ссылку на видео</i>', parse_mode='HTML')

@client.on(events.NewMessage)
async def ttdl(event):
    if event.message.text.startswith('http'):
        wait = await event.respond('⚡️ <b>Скачиваю...</b>', parse_mode='HTML')
        url = event.message.text
        video_data = download_video(url)
        if video_data:
            music_path = f'music_{event.id}_{event.chat_id}.mp3'

            media = InputMediaDocumentExternal(
                url=video_data['video']
            )

            await client.send_file(
                event.chat_id, media,
                caption=f"<b>Описание:</b>\n{video_data['title']}\n\n<a href='{url}'><b>Ссылка на видео</b></a>",
                buttons=[Button.inline("🎵 Получить музыку этого видео", data=music_path.encode())],
                parse_mode='HTML'
            )
            await wait.delete()

            with open(music_path, 'wb') as music_file:
                music_file.write(video_data['music'])
        else:
            await event.respond('😕 <b>Ошибка при сохранении видео :(</b>', parse_mode='HTML')

@client.on(events.CallbackQuery())
async def music(event):
    music_path = event.data.decode()
    if os.path.exists(music_path) and os.path.getsize(music_path) > 0:
        await client.send_file(event.chat_id, music_path, caption="🎶 <i>Музыка данного видео</i>", parse_mode='HTML')
    else:
        await event.respond('😕 <b>Ошибка при отправке музыки :(</b>', parse_mode='HTML')

@client.on(events.InlineQuery)
async def inline_temp(event):
    if event.text.startswith('http'):
        temp_result = event.builder.document(
            'https://i.imgur.com/ooNyb2c.mp4',
            title="Отправить видео",
            description="Сначала отправится пустышка, но потом она заменится на ваше видео честно-честно!!",
            text="<b>Загружаю ваше видео...</b>",
            mime_type='video/mp4',
            parse_mode="HTML",
            buttons=[Button.inline('...')]
        )
        await event.answer([temp_result], cache_time=1)

@client.on(events.Raw(UpdateBotInlineSend))
async def ttdl_inline(event):
    try:
        url = event.query
        video_data = download_video(url)
        
        if video_data:
            message = f"Описание:\n{video_data['title']}\n\nСсылка на видео"
            emoji_count = emoji.emoji_count(video_data['title'])

            link_offset = len(f"Описание:\n{video_data['title']}\n\n") + emoji_count

            entities = [
                MessageEntityBold(offset=0, length=9),
                MessageEntityBold(offset=link_offset, length=15),
                MessageEntityTextUrl(offset=link_offset, length=15, url=url)
            ]

            media = InputMediaDocumentExternal(
                url=video_data['video']
            )

            await client(EditInlineBotMessageRequest(
                id=event.msg_id,
                message=message,
                media=media,
                entities=entities
            ))
            return
        else:
            await inline_error(event)
    except Exception as e:
        print(f"Ошибка: {e}")   

async def inline_error(event):
    message = "Произошла ошибка :("
    entities = [
        MessageEntityBold(offset=0, length=len(message)),
    ]
    url = "https://i.imgur.com/kGPoMEk.mp4"
    
    media = InputMediaDocumentExternal(
        url=url
    )
    await client(EditInlineBotMessageRequest(
            id=event.msg_id,
            message=message,
            media=media,
            entities=entities
        ))
    return

def download_video(url):
    api_url = "https://tiktok-download5.p.rapidapi.com/getVideo"
    querystring = {"url": url, "hd": "0"}
    headers = {
        "X-RapidAPI-Key": "", #get this in rapidapi.com/llbbmm/api/tiktok-download5/ (200 free requests per month)
        "X-RapidAPI-Host": "" #get this in rapidapi.com/llbbmm/api/tiktok-download5/ (200 free requests per month)
    }
    response = requests.get(api_url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json().get('data')
        if data:
            video_url = data.get('play')
            music_url = data.get('music')
            title = data.get('title')
            if video_url and music_url and title:
                music = requests.get(music_url).content
                return {'video': video_url, 'music': music, 'title': title}
    return None

client.run_until_disconnected()