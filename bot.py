from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import asyncio
import subprocess

bot_token = ''  # Замени <BOT_TOKEN> на токен своего бота
bot = Bot(bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

work_dir = "/projects/work/#5"

def start_st_bot():
    subprocess.run(f"cd {work_dir};screen -d -m -S BotStatic python3 parse.py", shell=True)

def stop_st_bot():
    subprocess.run(f"screen -S BotStatic -X quit", shell=True)

stop_st_bot()

def restart():
    stop_st_bot()
    start_st_bot()

start_st_bot()

@dp.message_handler(commands=['help'])
async def help_command(message):
    response = "Доступные команды:\n" \
               "/add_category <название категории> - добавить категорию\n" \
               "/add_channel <название категории> <ссылка на канал> - добавить канал в категорию\n" \
               "/add_chat <название категории> <ID чата> - добавить чат для категории\n" \
               "/remove_category <название категории> - удалить категорию\n" \
               "/remove_channel <ссылка на канал> - удалить канал\n" \
               "/remove_chat <ID чата> - удалить чат\n" \
               "/view_categories - просмотреть категории\n" \
               "/view_channels - просмотреть каналы\n" \
               "/view_chats - просмотреть чаты"

    await message.reply(response)

@dp.message_handler(commands=['add_category'])
async def add_category(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    category_name = message.text.split('/add_category ')[1]
    cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
    conn.commit()

    await message.reply(f"Категория '{category_name}' добавлена")
    restart()

    conn.close()

@dp.message_handler(commands=['add_channel'])
async def add_channel(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    try:
        category_name, channel_link = message.text.split('/add_channel ')[1].split(' ')
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_id = cursor.fetchone()[0]

        cursor.execute('INSERT INTO channels (category_id, link) VALUES (?, ?)', (category_id, channel_link))
        conn.commit()

        await message.reply(f"Канал '{channel_link}' добавлен в категорию '{category_name}'\n\nБот перезапускается, в течении минуты все будет запущено.")
        restart()
    except:
        await message.reply("Неправильный формат команды. Используйте /add_channel <название категории> <ссылка на канал>")

    conn.close()

@dp.message_handler(commands=['add_chat'])
async def add_chat(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    try:
        category_name, chat_id = message.text.split('/add_chat ')[1].split(' ')
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_id = cursor.fetchone()[0]

        cursor.execute('SELECT chat_id FROM chats WHERE category_id = ?', (category_id,))
        existing_chat = cursor.fetchone()
        if existing_chat:
            cursor.execute('UPDATE chats SET chat_id = ? WHERE category_id = ?', (chat_id, category_id))
        else:
            cursor.execute('INSERT INTO chats (category_id, chat_id) VALUES (?, ?)', (category_id, chat_id))
        conn.commit()

        await message.reply(f"Чат '{chat_id}' добавлен для категории '{category_name}'\n\nБот перезапускается, в течении минуты все будет запущено.")
        restart()
    except:
        await message.reply("Неправильный формат команды. Используйте /add_chat <название категории> <ID чата>")

    conn.close()


@dp.message_handler(commands=['remove_category'])
async def remove_category(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    category_name = message.text.split('/remove_category ')[1]

    cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
    cursor.execute('DELETE FROM channels WHERE category_id IN (SELECT id FROM categories WHERE name = ?)', (category_name,))
    cursor.execute('DELETE FROM chats WHERE category_id IN (SELECT id FROM categories WHERE name = ?)', (category_name,))
    conn.commit()

    await message.reply(f"Категория '{category_name}' удалена\n\nБот перезапускается, в течении минуты все будет запущено.")
    restart()

    conn.close()

@dp.message_handler(commands=['remove_channel'])
async def remove_channel(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    channel_link = message.text.split('/remove_channel ')[1]

    cursor.execute('DELETE FROM channels WHERE link = ?', (channel_link,))
    conn.commit()

    await message.reply(f"Канал '{channel_link}' удален\n\nБот перезапускается, в течении минуты все будет запущено.")
    restart()

    conn.close()

@dp.message_handler(commands=['remove_chat'])
async def remove_chat(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    chat_id = message.text.split('/remove_chat ')[1]

    cursor.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
    conn.commit()

    await message.reply(f"Чат '{chat_id}' удален\n\nБот перезапускается, в течении минуты все будет запущено.")
    restart()

    conn.close()

@dp.message_handler(commands=['view_categories'])
async def view_categories(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM categories')
    categories = cursor.fetchall()

    response = "Доступные категории:\n"
    for category in categories:
        response += f"- {category[0]}\n"

    await message.reply(response)

    conn.close()

@dp.message_handler(commands=['view_channels'])
async def view_channels(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    cursor.execute('SELECT c.link, ct.name FROM channels c INNER JOIN categories ct ON c.category_id = ct.id')
    channels = cursor.fetchall()

    response = "Доступные каналы:\n"
    for channel in channels:
        response += f"- {channel[0]} (категория: {channel[1]})\n"

    await message.reply(response)

    conn.close()

@dp.message_handler(commands=['view_chats'])
async def view_chats(message: types.Message):
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()

    cursor.execute('SELECT ch.chat_id, ct.name FROM chats ch INNER JOIN categories ct ON ch.category_id = ct.id')
    chats = cursor.fetchall()

    response = "Доступные чаты:\n"
    for chat in chats:
        response += f"- {chat[0]} (категория: {chat[1]})\n"

    await message.reply(response)

    conn.close()

asyncio.run(dp.start_polling())
