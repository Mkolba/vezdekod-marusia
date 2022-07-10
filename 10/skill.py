# -*- coding: utf-8 -*-
from aiohttp import web
from utils import json_serial, BetterDict, prepare_text, prepare_tts, incline_score, is_stop_word
from random import shuffle
import json


weights = {
    'Шестёрка': 6, 'Семёрка': 7, 'Восьмёрка': 8, 'Девятка': 9, 'Десятка': 10,
    'Валет': 2, 'Дама': 3, 'Король': 4, 'Туз': 11
}


class Handler(web.View):
    async def post(self):

        data = BetterDict.loads(await self.request.text())
        self.session = data.session
        state = data.state.session
        print(data.request.command)

        if self.session.new:
            text = 'Привет! Сыграем в двадцать одно? Скажи «^Начать^», чтобы продолжить'
            return self.response(text, text, buttons=[{"title": "Начать"}], state={"stage": "start"})

        elif is_stop_word(data.request.command) or 'on_interrupt' in data.request.command:
            text = 'Поняла. До скорых встреч!'
            return self.response(text, text, end=True)

        elif state.stage == 'start':
            if 'нет' in data.request.command or 'не хочу' in data.request.command:
                text = 'Поняла. До скорых встреч!'
                return self.response(text, text, end=True)

            cards = ['Шестёрка', 'Семёрка', 'Восьмёрка', 'Девятка', 'Десятка', 'Валет', 'Дама', 'Король', 'Туз']
            suits = ['червы', 'пики', 'бубны', 'трефы']

            deck = []
            for card in cards:
                for suit in suits:
                    deck.append(f'{card} {suit}')

            shuffle(deck)

            card = deck.pop()
            score = weights[card.split()[0]]
            text = f'Отлично, начинаем! Ваша первая карта: {card}. Ваш счёт: {score}. Будете брать ещё?'
            return self.response(text, text, state={"stage": "playing", "score": score, 'deck': deck}, buttons=[{'title': 'Ещё'}, {'title': 'Нет'}])

        elif state.stage == 'playing':

            if 'ещё' in data.request.command or 'да' in data.request.command or 'еще' in data.request.command:
                deck = state.deck
                card = deck.pop()
                score = weights[card.split()[0]] + state.score
                if score < 21:
                    text = f'Ваша карта: {card}. Ваш счёт: {score}. Будете брать ещё?'
                    return self.response(text, text, state={"stage": "playing", "score": score, 'deck': deck},
                                         buttons=[{'title': 'Ещё'}, {'title': ''}])

                elif score == 21:
                    text = f'Ваша карта: {card}. Ваш счёт: {score}. Поздравляю с победой! Сыграем еще раз?'
                    tts = f'<speaker audio=\"marusia-sounds/game-win-2\"> ' + text

                    return self.response(text, tts, state={"stage": "start"}, buttons=[{'title': 'Да'}, {'title': 'Нет'}])

                else:
                    text = f'Ваша карта: {card}. Ваш счёт: {score}. Увы, но вы проиграли. Сыграем еще раз?'
                    return self.response(text, text, state={"stage": "start"}, buttons=[{'title': 'Да'}, {'title': 'Нет'}])

            elif 'нет' in data.request.command:
                deck = state.deck
                card = deck.pop()
                score = weights[card.split()[0]]
                while score <= 17:
                    card = deck.pop()
                    score += weights[card.split()[0]]

                text = 'Хорошо. Теперь моя очередь брать карты. Так-с, что тут у нас? '
                if score > 21:
                    text += 'Упс. Перебор. Поздравляю с победой!'
                elif score < state.score:
                    text += f'У меня {score}. Поздравляю с победой!'
                elif score > state.score:
                    text += f'Вот и на моей улице праздник. {score} {incline_score(score)} однозначно больше чем {state.score}!'
                elif score == state.score:
                    text += f'Я набрала {score}. Вышли на ничью.'
                elif score == 21:
                    text += f'Двадцать одно! В этот раз победа за мной.'

                text += ' Сыграем еще раз?'
                return self.response(text, text, state={"stage": "start"}, buttons=[{'title': 'Да'}, {'title': 'Нет'}])

            else:
                text = 'Не поняла вас. Скажите «Ещё» или «Нет»'
                return self.response(text, text, state=state, buttons=[{'title': 'Ещё'}, {'title': 'Нет'}])

        else:
            text = 'Привет! Сыграем в двадцать одно? Скажи «^Начать^», чтобы продолжить'
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
