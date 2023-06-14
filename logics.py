import vk_api
from datetime import datetime
from vk_api.exceptions import ApiError


class VkTools:

    def __init__(self, user_token):
        self.api = vk_api.VkApi(token=user_token)

    def _bdate_toyear(self, bdate):
        if bdate is not None:
            user_year = bdate.split('.')[2]
            now = datetime.now().year
            return now - int(user_year)
        else:
            print(f'Возраст не определен')

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get',
                                    {'user_id': user_id,
                                     'fields': 'city,sex,relation,bdate'
                                     }
                                    )
        except ApiError as e:
            info = {}
            print(f'Ошибка Аpi = {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info
                                                                               and 'last_name' in info else None,
                     'id': info.get('id'),
                     'sex': info.get('sex') if 'sex' in info else None,
                     'city': info.get('city')['title'] if info.get('city') is not None else None,
                     'bdate': info.get('bdate') if 'bdate' in info else None,
                     'year': self._bdate_toyear(info.get('bdate'))
                     }

        return user_info

    def search_users(self, params, offset):
        try:
            users = self.api.method('users.search',
                                    {'count': 50,
                                     'offset': offset,
                                     'hometown': params['city'],
                                     'sex': 1 if params['sex'] == 2 else 2,
                                     'has_photo': True,
                                     'age_from': params['year'] - 3,
                                     'age_to': params['year'] + 3,
                                     'status': params.get('relation', 6),
                                     'is_closed': False
                                     }
                                    )
        except ApiError as e:
            users = {}
            print(f'Ошибка Аpi = {e}')

        result = [{'id': item['id'],
                   'name': item['first_name'] + item['last_name']
                   } for item in users['items'] if item['is_closed'] is False
                  ]
        return result

    def get_photos(self, user_id):
        try:
            photos = self.api.method('photos.get',
                                     {'owner_id': user_id,
                                      'album_id': 'profile',
                                      'extended': 1
                                      }
                                     )
        except ApiError as e:
            photos = {}
            print(f'Ошибка Аpi = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]
        result.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)
        return result[:3]
