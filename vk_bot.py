import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import comm_token, user_token
from logics import VkTools
from work_db import Rightpeople


class VkBot:

    def __init__(self, comm_token, user_token):
        self.interface = vk_api.VkApi(token=comm_token)
        self.api = VkTools(user_token)
        self.params = None
        self.works_people = []

    def do_keyboard(self, one_time=False):
        keyboard = VkKeyboard(one_time=one_time)
        keyboard.add_button('Привет', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Пока', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Следующий', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()

    def message_send(self, user_id: int, message: str, attachment=None, keyboard=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'keyboard': keyboard,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def params_input(self, user_id):
        longpoll = VkLongPoll(self.interface)
        desired = ['sex', 'bdate', 'home_town']
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params = self.api.get_profile_info(user_id)
                params = self.params
                for param in params:
                    if param in desired:
                        if param == 'sex':
                            self.message_send(user_id, "Укажите свой пол: женский или мужской")
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    sex = event.text.lower()
                                    if sex == 'мужской':
                                        self.params[param] = 1
                                    elif sex == 'женский':
                                        self.params[param] = 2
                        elif param == 'bdate':
                            self.message_send(user_id, "Уточните вашу дату рождения(ДД.ММ.ГГГГ)")
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    bdate = event.text.lower()
                                    self.params[param] = bdate
                        elif param == 'home_town':
                            self.message_send(user_id, "Уточните город для поиска")
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    home_town = event.text.lower()
                                    self.params[param] = home_town
                    return params

    def new_message(self, partner_id=None):
        longpoll = VkLongPoll(self.interface)
        offset = 0
        users = []
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                user_id = event.user_id
                self.params = self.api.get_profile_info(user_id)
                if command == 'привет':
                    keyboard = self.do_keyboard()
                    self.message_send(user_id=user_id, message=f"Привет, {self.params['name']}, жми на кнопки",
                                      keyboard=keyboard)
                elif command == "пока":
                    keyboard = self.do_keyboard()
                    self.message_send(user_id=user_id, message=f"Пока, {self.params['name']}",
                                      keyboard=keyboard)
                elif command == "поиск":
                    keyboard = self.do_keyboard()
                    # temp_params = self.params_input(user_id=user_id)
                    users = self.api.search_users(self.params)
                    offset += 1
                    for user in users:
                        one = Rightpeople(user_id=self.params['id'], partner_id=user['id'])
                        self.works_people.append(user)
                        if not one.people_in_db():
                            one.add_in_db(user_id=user_id, partner_id=user['id'])
                            self.works_people.append(user)
                        photos_user = self.api.get_photos(user['id'])
                        self.message_send(user_id, f'Есть {len(self.works_people)} найденных пользователей',
                                      keyboard=keyboard)
                        self.message_send(user_id, f'https://vk.com/id{user["id"]}, {user["name"]}',
                                      photos_user, keyboard=keyboard)
                elif command == 'следующий':
                    keyboard = self.do_keyboard()
                    if self.works_people == [] or users is None:
                        offset += 10
                        # temp_params = self.params_input(user_id=user_id)
                        users = self.api.search_users(self.params, offset)
                        user = users.pop()
                        photos_user = self.api.get_photos(user['id'])
                        self.message_send(user_id, f'Подходящий пользователь: https://vk.com/id{user["id"]}, '
                                                   f'{user["name"]}', photos_user, keyboard=keyboard)
                        one = Rightpeople(user_id=self.params['id'], partner_id=user['id'])
                        one.add_in_db(user_id, partner_id)
                    else:
                        user = self.works_people.pop()
                        one = Rightpeople(user_id=user_id, partner_id=user['id'])
                        photos_user = self.api.get_photos(user['id'])
                        keyboard = self.do_keyboard(one_time=True)
                        self.message_send(user_id,
                                          f'Подходящий пользователь: https://vk.com/id{user["id"]}, {user["name"]}',
                                          photos_user, keyboard=keyboard)
                        if not one.people_in_db:
                            one.add_in_db(user_id=user_id, partner_id=user['id'])


if __name__ == '__main__':
    bot = VkBot(comm_token, user_token)
    bot.new_message()

