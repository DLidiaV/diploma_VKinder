import vk_api
from datetime import datetime
from config import user_token


class VkTools:
    def __init__(self, user_token):
        self.api = vk_api.VkApi(token=user_token)

    def get_profile_info(self, user_id):
        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation,home_town'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'] if 'home_town' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     'city': info['city']['id'] if 'city' in info else None
                     }
        return user_info

    def search_users(self, params, offset=0):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5
        status = params.get('relation', 6),
        home_town = params['home_town']

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': status,
                                 'home_town': home_town,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if not user['is_closed']:
                photo = self.get_photos(user['id'])
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name'],
                            'photo': photo[1]
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photo_best = (sorted(photos['items'], key=lambda x: x['likes']['count'] + x['comments']['count'],
                                 reverse=True))[:3]

            for photo in photo_best:
                result_p = ','.join([f'photo{photo["owner_id"]}_{photo["id"]}'])
                link = f'Профиль: https://vk.com/id{user_id} \n'
                return link, result_p
        except KeyError:
            return None


if __name__ == '__main__':
    bot = VkTools(user_token)

