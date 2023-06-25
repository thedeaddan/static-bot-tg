from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest,ImportChatInviteRequest
import asyncio
import re
import sqlite3
import time
import datetime
import random


api_id = 
api_hash = ""

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
    async with TelegramClient('Abduhail', api_id, api_hash) as client:
        for channel in channels:
            try:
                await asyncio.sleep(random.randint(1,2))
                try:
                    channel_entity = await client.get_entity(channel)
                    if channel_entity.left == False:
                        print(f"You are subscribed to {channel}")
                        pass
                    else:
                        print(f"You are not subscribed to {channel}") 
                        await client(JoinChannelRequest(channel))
                except Exception as e:
                    print(e)
                    print(channel.replace("https://t.me/+",""))
                    try:
                        await client(ImportChatInviteRequest(hash=channel.replace("https://t.me/+","")))
                    except Exception as e:
                        print(e)
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
    async with TelegramClient('Abduhail', api_id, api_hash) as client:
        print("act")
        @client.on(events.NewMessage(chats=channels))
        async def Messages(event):
            if not event.message.grouped_id:
                try:
                    await asyncio.sleep(random.randint(20,30))
                    message_id = event.message.id
                    print(f"Получил сообщение {message_id} ")  # Замените на нужный ID сообщения
                    message = await get_message_by_id(client, event.message.peer_id.channel_id, message_id)
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
                        start_time = time.time()
                        conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)
                        
                        while time.time() - start_time <= 600 or conversion_rate <= 2:
                            await asyncio.sleep(random.randint(20, 40))
                            message = await get_message_by_id(client, event.message.peer_id.channel_id, message_id)
                            conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)
                            current_time = datetime.datetime.now().strftime("%H:%M:%S")
                            print(f"Ожидаю сообщение ID:{message.id}:\n👀Просмотры: {message.views} ↩️Репосты: {message.forwards} Конверсия: {str(conversion_rate)}% Данные на {current_time} Осталось: {time.time() - start_time} сек.")
                            
                        if conversion_rate > 2:
                            await client.forward_messages(my_channel, event.message)
                            print(f"Переслал сообщение ID: {message.id}")
                            current_time = datetime.datetime.now().strftime("%H:%M:%S")
                            msg = await client.send_message(my_channel, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(conversion_rate)}%\n\nДанные на {current_time}')
                            for i in range(5):
                                print(f"Ждем обновления статистики сообщения ID:{message.id}")
                                await asyncio.sleep(random.randint(100,150))
                                message = await get_message_by_id(client, event.message.peer_id.channel_id, message_id)
                                try:
                                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                                    conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)
                                    if conversion_rate > 2:
                                        await client.edit_message(my_channel, msg.id, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(conversion_rate)}%\n\nДанные на {current_time}')
                                        print(f"Обновил сообщение ID:{message.id}:\n👀Просмотры: {message.views} ↩️Репосты: {message.forwards} Конверсия: {str(conversion_rate)}%\n\nДанные на {current_time}")
                                    else:
                                        break
                                except:
                                    pass
                                print(i)
                except Exception as e:
                    print(e)

        @client.on(events.Album(chats=channels))
        async def Album(event):
            if event.original_update.message.grouped_id:
                try:
                    await asyncio.sleep(random.randint(20, 40))
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
                        start_time = time.time()
                        conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)

                        while time.time() - start_time <= 600 or conversion_rate <= 2:
                            await asyncio.sleep(random.randint(20, 40))
                            message = await get_message_by_id(client, event.original_update.message.peer_id.channel_id, message_id)
                            conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)

                        if conversion_rate > 2:
                            await event.forward_to(my_channel)
                            print(f"Переслал сообщение ID: {message.id}")
                            current_time = datetime.datetime.now().strftime("%H:%M:%S")
                            msg = await client.send_message(my_channel, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%\n\nДанные на {current_time}')
                            for i in range(5):
                                print(f"Ждем обновления статистики сообщения ID:{message.id}")
                                await asyncio.sleep(random.randint(100, 150))
                                message = await get_message_by_id(client, event.original_update.message.peer_id.channel_id, message_id)
                                try:
                                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                                    conversion_rate = round((int(message.forwards) / int(message.views) * 100), 3)
                                    if conversion_rate > 2:
                                        await client.edit_message(my_channel, msg.id, f'Статистика:\n👀Просмотры: {message.views}\n↩️Репосты: {message.forwards}\n\nКонверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%\n\nДанные на {current_time}')
                                        print(f"Обновил сообщение ID:{message.id}:\n👀Просмотры: {message.views} ↩️Репосты: {message.forwards} Конверсия: {str(round((int(message.forwards)/int(message.views)*100),3))}%\n\nДанные на {current_time}")
                                    else:
                                        break
                                except:
                                    pass
                                print(i)
                except Exception as e:
                    print(e)


        await client.run_until_disconnected()
asyncio.run(main())
