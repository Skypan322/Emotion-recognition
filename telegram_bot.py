import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from Parser_v2 import get_filters
from Parser_v2 import get_film
import json
from fer import FER
import matplotlib.pyplot as plt

from auth import bot_token

genres = get_filters()
genres = [genre for genre in genres.keys() if genre != '']

curl = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
user = types.User()

emo_keys = {
    'sad': 'драма',
    "disgust": 'фильм-нуар',
    "angry": 'боевик',
    "happy": "комедия",
    "surpise": 'детектив',
    "fear": 'ужасы',
}
translate = {
    'sad': 'грусть',
    "disgust": 'отвращение',
    "angry": 'злость',
    "happy": "счастье",
    "surpise": 'удивление',
    "fear": 'страх',
}


def dominant_emo(captured_emo):
    phrase = []

    phrases = {
        'angry': ['Ты немного зол(зла), возможно', 'Выглядишь раздражённо'],
        'disgust': ['Неприятное утро?', 'Явно что-то же неприятное ты увидел(а)?'],
        'fear': ['Немного паникуешь, да?', 'Да ты паникёр! Не переживай, нормально всё будет.'],
        'happy': ["Рад, что ты на позитиве сегодня :).", 'BROOOO, WHO GOT YOU SMILE LIKE THAT?)'],
        'sad': ['Грустишь?', 'Бывают в жизни огорчения, ведь так? Всё будет нормально!'],
        'surprise': ['Ничего себе! А чему удивляемся?', 'Ух ты, что ж такое произошло, что ты так удивлён?'],
    }
    flag = False
    for i in captured_emo:
        emo = i['emotions']

        if emo['neutral'] <= 0.4:
            phrase.append('Ничоси на тебе эмоций!')
            flag = True
        emo.pop('neutral', None)

        emo = list(sorted(emo.items(), key=lambda item: item[1]))[::-1]
        for j in emo:
            if j[1] != 0:
                if j[1] >= 0.4:
                    phrase.append(phrases[j[0]][1])
                else:
                    phrase.append(phrases[j[0]][0])
        final_emo = emo
        print(emo)
        if emo[0][1] - emo[1][1] >= 0.4:
            final_emo = emo[:1]
        print(final_emo)
        return "\n".join(phrase[:2]), final_emo, flag


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Приветик! \n Напиши жанр, который хочешь посмотреть, или отправь мне своё фото, чтобы я подобрал что-то для тебя!) \n Используй /help, \
                        чтобы узнать список жанров!")


@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await message.reply(f"Я понимаю жанры: {genres}")
    await message.reply("Также ты можешь отправить мне своё фото, а по глядя на тебя я подберу что-то хорошее)")


@dp.message_handler(content_types=['photo'])
async def collect_photo(message: types.Message):
    user_id = message.from_user.id
    file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    src = f'images\\user_photo_{user_id}.jpg'
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file.read())

    user_image = plt.imread(f"images\\user_photo_{user_id}.jpg")
    emo_detector = FER(mtcnn=True)

    try:
        captured_emotions = emo_detector.detect_emotions(user_image)
        with open('emotions.json', 'a+', encoding='utf-8') as file:
            table = {user_id: captured_emotions}
            json.dump(table, file, indent=4, ensure_ascii=False)
        if len(captured_emotions) > 1:
            await bot.send_message(user_id, f"Ля какие красавцы! \n Вы прекрасны, но сфоткайся, пожалуйста, один :3")
        elif len(captured_emotions) < 1:
            await bot.send_message(user_id, f"А где? :с \n Не вижу людей(((")
        else:
            # await bot.send_message(user_id, captured_emotions[0]['emotions'])
            # await bot.send_message(user_id, f"Фото успешно скачано! Твой Id {user_id}")
            phrase, main_emo, strength = dominant_emo(captured_emotions)

            emo_vector = set(main_emo + [strength])
            genre = False

            if emo_vector == {'fear', 'angry', False}:
                genre = 'триллер'
            elif emo_vector == {'angry', 'sad', False}:
                genre = 'история'
            elif emo_vector == {'angry', 'sad', True}:
                genre = 'военный'
            elif emo_vector == {'disgust', 'sad', False}:
                genre = "фэнтези"
            elif emo_vector == {'happy', 'sad', False}:
                genre = 'фантастика'
            elif (emo_vector == {'happy', 'sad', False}) or (emo_vector == {'happy', 'sad', True}):
                genre = 'мелодрама'

            if not genre:
                genre = emo_keys[main_emo[0][0]]

            if genre in genres:
                await bot.send_message(message.from_user.id, "Сейча-а-ас что-то найду :3")
                url, name, image_url = get_film(curl, genre)
                await bot.send_message(message.from_user.id,
                                       f'Попробуй посмотреть "{name}", \nСсылка на него - {url} \n Если хочешь, могу посоветовать что-то ещё')

            await bot.send_message(user_id, phrase)
            if len(main_emo) > 1:
                await bot.send_message(user_id,
                                       f'Твои доминирующие эмоции - {translate[main_emo[0][0]]} и {translate[main_emo[1][0]]}')
            else:
                await bot.send_message(user_id, f'Твои доминирующия эмоция - {translate[main_emo[0][0]]}')


    except Exception as ex:
        print(ex)
        await bot.send_message(user_id,
                               "Бро, ты меня просто сломал :с.\nОднако, если ты перезапустишь, это решит все проблемы ")


@dp.message_handler()
async def get_genre(msg: types.Message):
    requested_genre = msg.text.lower()
    if requested_genre in genres:
        await bot.send_message(msg.from_user.id, "Сейча-а-ас что-то найду :3")
        url, name, image_url = get_film(curl, requested_genre)
        await bot.send_message(msg.from_user.id,
                               f'Попробуй посмотреть "{name}", \nСсылка на него - {url}'
                               f' \n Если хочешь, могу посоветовать что-то ещё')
    else:
        await msg.reply("Увы, но такого жанра я не знаю :С "
                        "\n Попробуй посмотерть доступные жанры командой /help")


'''
@dp.message_handler(commands=['repeat'])
async def repeat(msg:types.Message):
    global last_func
    global last_msg
    last_func(last_msg)
'''

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
