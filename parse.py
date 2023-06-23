from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
import asyncio
import re
import sqlite3
import time

api_id = 
api_hash = 

async def get_channels():
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
    channels_ = cursor.fetchall()
    cursor.execute('SELECT * FROM chats')
    chats_ = cursor.fetchall()
    conn.close()

    channels = []

    for i in channels_:
        channels.append(i[2])
    for j in chats_:
        channels.append(j[2])
    return channels

    
async def join(channels):
    async with TelegramClient('123', api_id, api_hash) as client:
        for channel in channels:
            try:
                await asyncio.sleep(3)
                channel_entity = await client.get_entity(channel)
                if channel_entity.left == False:
                    print(f"You are subscribed to {channel}")
                    pass
                else:
                    print(f"You are not subscribed to {channel}") 
                    await client(JoinChannelRequest(channel))
            except Exception as e:
                print(f"Channel {channel} not found.")

async def get_message_by_id(client, channel, message_id):
    try:
        entity = await client.get_entity(channel)
        message = await client.get_messages(entity, ids=message_id)
        return message
    except errors.FloodWaitError as e:
        print(f"Sleeping for {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
        return await get_message_by_id(client, channel, message_id)
    except errors.MessageIdInvalidError:
        print("Invalid message ID.")
        return None

async def main():
    channels = await get_channels()
    await join(channels)
    async with TelegramClient('123', api_id, api_hash) as client:
        print("act")
        @client.on(events.NewMessage(chats=channels))
        async def Messages(event):
            if not event.message.grouped_id:
                try:
                    await asyncio.sleep(20)
                    message_id = event.message.id  # Замените на нужный ID сообщения
                    message = await get_message_by_id(client, event.message.peer_id.channel_id, message_id)
                    entity = await client.get_entity(message.peer_id.channel_id)
                    username = f"https://t.me/{entity.username}"
                    conn = sqlite3.connect('channels.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT category_id FROM channels WHERE link = ?',(username,))
                    cat = cursor.fetchone()[0]
                    cursor.execute('SELECT chat_id FROM chats WHERE category_id = ?',(cat,))
                    my_channel = cursor.fetchone()[0]
                    conn.close()
                    if message:
                        await client.forward_messages(my_channel,event.message)
                        print(f"Переслал сообщение ID: {message.id}")
                        msg = await client.send_message(my_channel, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%')
                        for i in range(5):
                            print(f"Ждем обновления статистики сообщения ID:{message.id}")
                            await asyncio.sleep(120)
                            message = await get_message_by_id(client, event.message.peer_id.channel_id, message_id)
                            try:
                                await client.edit_message(my_channel,msg.id,f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%')
                                print(f"Обновил сообщение ID:{message.id}:\n👀Просмотры: {message.views} ↩️Репосты: {message.forwards} Конверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%")
                            except:
                                pass
                            print(i)
                except Exception as e:
                    print(e)

        @client.on(events.Album(chats=channels))
        async def Album(event):
            if event.original_update.message.grouped_id:
                await asyncio.sleep(20)
                message_id = event.original_update.message.id  # Замените на нужный ID сообщения
                message = await get_message_by_id(client, event.original_update.message.peer_id.channel_id, message_id)
                entity = await client.get_entity(message.peer_id.channel_id)
                username = f"https://t.me/{entity.username}"
                conn = sqlite3.connect('channels.db')
                cursor = conn.cursor()
                cursor.execute('SELECT category_id FROM channels WHERE link = ?', (username,))
                cat = cursor.fetchone()[0]
                cursor.execute('SELECT chat_id FROM chats WHERE category_id = ?', (cat,))
                my_channel = cursor.fetchone()[0]
                conn.close()
                if message:
                    await event.forward_to(my_channel)
                    print(f"Переслал сообщение ID: {message.id}")
                    msg = await client.send_message(my_channel, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%')
                    for i in range(5):
                        print(f"Ждем обновления статистики сообщения ID:{message.id}")
                        await asyncio.sleep(120)
                        message = await get_message_by_id(client, event.original_update.message.peer_id.channel_id, message_id)
                        try:
                            await client.edit_message(my_channel, msg.id, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%')
                            print(f"Обновил сообщение ID:{message.id}:\n👀Просмотры: {message.views} ↩️Репосты: {message.forwards} Конверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%")
                        except:
                            pass
                        print(i)


        await client.run_until_disconnected()
asyncio.run(main())
