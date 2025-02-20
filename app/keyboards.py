from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


ready = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Подтвердить готовность')]],
    resize_keyboard=True,
    input_field_placeholder='Нажмите, когда будете готовы')


q1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Менее 18')],
    [KeyboardButton(text='18-34'),
    KeyboardButton(text='35-44')],
    [KeyboardButton(text='45-54'), 
    KeyboardButton(text='55 и более')]],
    resize_keyboard=True,
    input_field_placeholder='Укажите возраст')

q2 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Мужской'), KeyboardButton(text='Женский')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите пол')

q3 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Куйбышевский'), KeyboardButton(text='Самарский')],
                                    [KeyboardButton(text='Ленинский'), KeyboardButton(text='Железнодорожный')],
                                    [KeyboardButton(text='Октябрьский'), KeyboardButton(text='Советский')],
                                    [KeyboardButton(text='Промышленный'), KeyboardButton(text='Кировский')],
                                    [KeyboardButton(text='Красноглининский'), KeyboardButton(text='Частный сектор в пригороде')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите районы')

q4 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Проблемы со зрением')],
                                    [KeyboardButton(text='Проблемы со слухом')],
                                    [KeyboardButton(text='Проблемы опорно-двигательного аппарата')],
                                    [KeyboardButton(text='Ментальные особенности')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите ограничения здоровья')

q5 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Наличие голосового помощника')],
                                    [KeyboardButton(text='Индивидуальная настройка масштаба приложения')],
                                    [KeyboardButton(text='Управление жестами')],
                                    [KeyboardButton(text='Применение методики \"Ясный язык\"')],
                                    [KeyboardButton(text='Возможность быстро поделиться местоположением')],
                                    [KeyboardButton(text='Возможность оперативно отправить сигнал тревоги с указанием своего местоположения')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите дополнительные функциональные возможности')

q6 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Указать местоположение на карте и описать проблему')],
                                    [KeyboardButton(text='Отправить сообщение в службу поддержки')],
                                    [KeyboardButton(text='Оставить отзыв после завершения маршрута')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите удобный способ об изменении информации')

q7 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Часто'),
                                    KeyboardButton(text='Иногда')],
                                    [KeyboardButton(text='Редко'),
                                    KeyboardButton(text='Не буду')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите частоту пользования')

q8 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Готов участвовать в сборе данных дорожных объектов во время прохождения своих ежедневных маршрутов')],
                                    [KeyboardButton(text='Готов примкнуть к волонтёрам для массового сбора информации о дорожных объектах города')],
                                    [KeyboardButton(text='Готов рассказать о проекте знакомым')],
                                    [KeyboardButton(text='Не готов')]],
                        resize_keyboard=True,
                        input_field_placeholder='Расскажите о готовности помочь')

q9 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Социальные объекты'),
                                    KeyboardButton(text='Медицинский учреждения')],
                                    [KeyboardButton(text='Культурные учреждения'),
                                    KeyboardButton(text='Образовательные учреждения')],
                                    [KeyboardButton(text='Развлекательные учреждения'),
                                    KeyboardButton(text='Религиозные объекты')],
                                    [KeyboardButton(text='Общественные организации')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите объекты')

q10 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Помощь разработчикам в понимании Ваших потребностей для комфортного маршрута')],
                                    [KeyboardButton(text='Предоставление информации о сложностях передвижения на улице')],
                                    [KeyboardButton(text='Исполнение запроса на прохождение теста')]],
                        resize_keyboard=True,
                        input_field_placeholder='Укажите цель')