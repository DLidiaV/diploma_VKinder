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
        self.longpoll = VkLongPoll(self.interface)
        self.api = VkTools(user_token)
        self.params = {}
        self.works_people = []
        self.offset = 0

    def do_keyboard(self, one_time=False):
        keyboard = VkKeyboard(one_time=one_time)
        keyboard.add_button('Привет', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Пока', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    def message_send(self, user_id: int, message: str, attachment: str = None, keyboard: str = None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'keyboard': keyboard,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def new_message(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    keyboard = self.do_keyboard()
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(user_id=event.user_id, message=f"Привет, {self.params['name']}, жми на Поиск",
                                      keyboard=keyboard)
                    if not self.params.get('city'):
                        self.message_send(user_id=event.user_id, message=f"Уточните город для поиска",
                                          keyboard=keyboard)
                        for event1 in self.longpoll.listen():
                            if event1.type == VkEventType.MESSAGE_NEW and event1.to_me:
                                city = event1.text.lower()
                                self.params['city'] = city
                                break
                        self.message_send(user_id=event.user_id, message=f"Город для поиска: {self.params['city']}",
                                          keyboard=keyboard)
                    if not self.params.get('sex'):
                        self.message_send(user_id=event.user_id, message=f"Укажите свой пол: женский или мужской")
                        for event2 in self.longpoll.listen():
                            if event2.type == VkEventType.MESSAGE_NEW and event2.to_me:
                                sex = event2.text.lower()
                                if sex == 'мужской':
                                    self.params['sex'] = 1
                                elif sex == 'женский':
                                    self.params['sex'] = 2
                    if not self.params.get('bdate'):
                        self.message_send(user_id=event.user_id, message=f"Уточните вашу дату рождения(ДД.ММ.ГГГГ)")
                        for event3 in self.longpoll.listen():
                            if event3.type == VkEventType.MESSAGE_NEW and event3.to_me:
                                bdate = event3.text.lower()
                                self.params['bdate'] = bdate

                elif event.text.lower() == "поиск":
                    keyboard = self.do_keyboard()
                    self.message_send(user_id=event.user_id, message="Начинаем поиск",
                                      keyboard=keyboard)
                    if self.works_people:
                        works_people_one = self.works_people.pop()
                        photos_user = self.api.get_photos(works_people_one['id'])
                        photo_string = ''
                        for photo in photos_user:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.works_people = self.api.search_users(self.params, self.offset)
                        works_people_one = self.works_people.pop()
                        photos_user = self.api.get_photos(works_people_one['id'])
                        photo_string = ''
                        for photo in photos_user:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10
                    self.message_send(event.user_id,
                                      f' Подходящий пользователь ВК:https://vk.com/id{works_people_one["id"]}, '
                                      f'{works_people_one["name"]}', attachment=photo_string, keyboard=keyboard)
                    one = Rightpeople(user_id=self.params['id'], partner_id=works_people_one['id'])

                    if one.extract_from_db(self.params['id'], works_people_one['id']) is False:
                        one.add_in_db(user_id=self.params['id'], partner_id=works_people_one['id'])

                elif event.text.lower() == "пока":
                    keyboard = self.do_keyboard()
                    self.message_send(user_id=event.user_id, message=f"Пока, {self.params['name']}",
                                      keyboard=keyboard)

                else:
                    keyboard = self.do_keyboard()
                    self.message_send(
                        event.user_id, 'Неизвестная команда', keyboard=keyboard)


if __name__ == '__main__':
    bot = VkBot(comm_token, user_token)
    bot.new_message()
