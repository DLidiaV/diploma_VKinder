 Дипломная работа "VKinder"

Задание

Используя данные из VK, нужно сделать сервис намного лучше, чем Tinder, а именно: чат-бота “VKinder”. Бот должен искать людей, подходящих под условия, на основании информации о пользователе из VK:

Возраст,
пол,
город,
семейное положение.
У тех людей, которые подошли по требованиям пользователю, получать топ-3 популярных фотографии профиля и отправлять их пользователю в чат вместе со ссылкой на найденного человека.
Популярность определяется по количеству лайков и комментариев.

За основу можно взять код из файла basic_code.py:

from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = input('Token: ')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

Входные данные

Имя пользователя или его id в ВК, для которого мы ищем пару.
если информации недостаточно нужно дополнительно спросить её у пользователя.

Требования к сервису:

Код программы удовлетворяет PEP8.
Получать токен от пользователя с нужными правами.
Программа декомпозирована на функции/классы/модули/пакеты.
Результат программы записывать в БД.
Люди не должны повторяться при повторном поиске.
Не запрещается использовать внешние библиотеки для vk.