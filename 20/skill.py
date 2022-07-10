# -*- coding: utf-8 -*-
from aiohttp import web
from utils import json_serial, BetterDict, prepare_text, prepare_tts, incline_score, is_stop_word
from random import choice
import json


edible = [
    'Суп', 'Макароны', 'Котлета', 'Мандарин', 'Яблоко', 'Груша', 'Колбаса', 'Фрикаделька',
    'Стейк', 'Роллы', 'Творог', 'Чизкейк', 'Булка', 'Хлеб', 'Масло', 'Сахар'
]

inedible = [
    'Кирпич', 'Гравий', 'Лампочка', 'Провод', 'Ножницы', 'Штаны', 'Стол', 'Стул', 'Бордюр',
    'Асфальт', 'Бетон', 'Стекло', 'Игрушка', 'Циркуль', 'Флешка', 'Карандаш'
]


class Handler(web.View):
    async def post(self):

        data = BetterDict.loads(await self.request.text())
        self.session = data.session
        state = data.state.session
        print(data.request.command)

        if self.session.new:
            text = 'Привет! Поиграем в съедобное-несъедобное? Скажи «^Начать^», чтобы продолжить'
            return self.response(text, text, buttons=[{"title": "Начать"}], state={"stage": "start"})

        elif is_stop_word(data.request.command) or 'on_interrupt' in data.request.command:
            text = 'Поняла. До скорых встреч!'
            return self.response(text, text, end=True)

        elif state.stage == 'start':
            if 'нет' in data.request.command or 'не хочу' in data.request.command:
                text = 'Поняла. До скорых встреч!'
                return self.response(text, text, end=True)

            food_type = choice(['edible', 'inedible'])
            item = choice(edible) if food_type == 'edible' else choice(inedible)

            text = f'Отлично, начинаем! Что делать с такой вкусняшкой как {item.lower()}?'
            return self.response(text, text, state={"stage": "playing", "score": 0, 'food_type': food_type}, buttons=[{'title': 'Съем'}, {'title': 'Выброшу'}])

        elif state.stage == 'playing':

            if 'съем' in data.request.command:
                if state.food_type == 'edible':
                    score = state.score + 1
                    text = f'Точно! Вполне вкусно и, наверное, даже полезно.'
                else:
                    text = f'А вот и неправильно. Такое кушать точно нельзя.'
                    score = 0

                food_type = choice(['edible', 'inedible'])
                item = choice(edible) if food_type == 'edible' else choice(inedible)

                text += f' А если бы тебе предложили угоститься такой штукой как {item.lower()}?'
                add = f'\n\nВаш счёт: {score}'
                return self.response(text + add, text, state={"stage": "playing", "score": score, 'food_type': food_type},
                                     buttons=[{'title': 'Съем'}, {'title': 'Выброшу'}])

            elif 'выброшу' in data.request.command:
                if state.food_type == 'inedible':
                    score = state.score + 1
                    text = f'Точно! Такое и правда употреблять не стоит.'
                else:
                    text = f'А вот и неправильно. Кушать такое можно, а иногда даже нужно!.'
                    score = 0

                food_type = choice(['edible', 'inedible'])
                item = choice(edible) if food_type == 'edible' else choice(inedible)

                text += f' А если бы тебе предложили угоститься такой штукой как {item.lower()}?'
                add = f'\n\nВаш счёт: {score}'
                return self.response(text + add, text, state={"stage": "playing", "score": score, 'food_type': food_type},
                                     buttons=[{'title': 'Съем'}, {'title': 'Выброшу'}])

            else:
                text = 'Не поняла вас. Скажите «Съем» или «Выброшу»'
                return self.response(text, text, state=state, buttons=[{'title': 'Ещё'}, {'title': 'Нет'}])

        else:
            text = 'Привет! Поиграем в съедобное-несъедобное? Скажи «^Начать^», чтобы продолжить'
            return self.response(text, text, buttons=[{"title": "Начать"}], state={"stage": "start"})

    def response(self, text, tts="", end=False, state=None, buttons=None, jsonify=True, perm_state=None, image=None):
        data = {
            "response": {
                "end_session": end,
                "text": prepare_text(text),
                "tts": prepare_tts(tts)
            },
            "session": {
                "session_id": self.session.session_id,
                "user_id": self.session.application.application_id,
                "message_id": self.session.message_id
            },
            "version": "1.0"
        }

        if state:
            data.update({"session_state": state})

        if perm_state:
            data.update({"user_state_update": perm_state})

        if buttons:
            data["response"].update({'buttons': buttons})

        if image:
            data["response"].update({'card': {"type": "BigImage", "image_id": image}})
        resp = web.Response(body=(json.dumps(data, default=json_serial)) if jsonify else data)
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'application/json'
        return resp

    async def options(self):
        resp = web.Response()
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'application/json'
        return resp
