#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram-бот Макс — эксперт-консультант магазина «Авангард»
Напольные покрытия и обои.
Запускается как Web Service (вебхуки).
"""

import os
import random
import logging
import asyncio
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ---------- Логирование ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- ТОКЕН ----------
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не установлена!")

# ---------- Состояния диалога ----------
(
    MAIN,
    LINOLEUM_MENU,
    LAMINAT_MENU,
    KVC_MENU,
    WALLPAPER_MENU,
    CHOOSE_ROOM,
    CHOOSE_LOAD,
    CHOOSE_BUDGET,
    RECOMMENDATION,
    COMPARE_MENU,
    TIPS_MENU,
    FEEDBACK_INIT,
    FEEDBACK_TEXT,
    FEEDBACK_DATE,
    CONSULT,
) = range(15)

# ---------- Клавиатуры ----------
def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["🟫 Линолеум", "🟧 Ламинат"],
            ["⬜ Кварц-винил", "🎨 Обои"],
            ["⚖️ Что выбрать?", "🔧 Лайфхак"],
            ["💬 Обратная связь", "📞 Консультант"],
        ],
        resize_keyboard=True,
    )

# ---------- Банк лайфхаков ----------
TIPS = [
    "Перед укладкой ламината или кварц-винила оставьте материал в помещении на 48 часов. Пачки должны акклиматизироваться, иначе после монтажа появятся щели.",
    "Отошли обои в углу? Налейте клей ПВА в шприц, введите под обоину и прогладьте сухой тряпкой. Чисто и держит мёртво.",
    "Фетровые подпяточники на ножки мебели — святое для нового пола. Наклейте ДО того, как занесёте мебель. Пол скажет спасибо.",
    "При резке линолеума оставляйте запас 3–5 см у стены. Лучше потом аккуратно подрезать, чем получить дыру на всю комнату.",
    "Кварц-винил не боится ковриков, но чёрная резина может оставить несмываемые следы. Проверяйте маркировку придверного коврика.",
    "Хотите визуально приподнять потолок? Клейте вертикальные полосы. Комната узкая? Диагональная укладка пола её расширит.",
    "Никогда не выбрасывайте остатки обоев и плашек пола! Через 5 лет для ремонта одного участка вы не найдёте ту же партию.",
    "Плинтус крепите к стене, а не к полу. Любое напольное покрытие «дышит» — расширяется и сужается от температуры. Плинтус, прибитый к полу, будет скрипеть и отрываться.",
    "Перед поклейкой обоев обязательно грунтуйте стены. Это сэкономит до 30% клея и предотвратит отваливание стыков через год.",
    "Маркер или фломастер на ламинате? Не трите ацетоном! Закрасьте след обычным ластиком, затем протрите сухой микрофиброй. След исчезнет.",
    "Тёмный пол — это красиво, но на нём видна любая пылинка. Выбирайте покрытие с неоднородной текстурой (под дерево с брашированием) — оно прощает неидеальную уборку.",
    "Передвигаете мебель? Подложите под ножки старые носки или влажные тряпки — скользить будет как по маслу, без единой царапины.",
    "Сомневаетесь в цвете обоев? Возьмите образец и посмотрите при своём домашнем свете. Магазинный «холодный» свет делает оттенок на 1–2 тона светлее, чем тёплая домашняя лампа.",
    "Замок ламината не защёлкнулся до конца? Не бейте молотком по самой планке! Используйте брусок-подбойник — удар напрямую деформирует замок.",
    "Новый линолеум пахнет? Не пугайтесь — это нормально для качественного ПВХ-покрытия. Хорошо проветрите помещение 2–3 дня, и запах уйдёт полностью. Не заставляйте комнату мебелью сразу после укладки.",
    "Пятно на виниловых обоях на кухне? Вода + капля средства для мытья посуды, нанесите губкой и оставьте на 5 минут. Жир сам отойдёт, не трите щёткой.",
    "При расчёте количества плитки или плашек всегда берите +10% к площади. Подрезка, кривые углы и случайный бой неизбежны.",
    "Щель между плинтусом и стеной? Не замазывайте белым герметиком — через месяц он станет серым от пыли. Используйте акриловый герметик под покраску и закрасьте в цвет стены.",
    "Перед укладкой линолеума проверьте пол на влажность: приклейте кусочек полиэтилена скотчем к стяжке на ночь. Если утром под ним соберётся конденсат — укладывать нельзя, пойдёт плесень.",
    "Зеркало напротив окна + светлые обои = визуально +10 метров к пространству. В маленьких комнатах работает безотказно!",
]

# ---------- Команды ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! 🏠\n"
        "Я Макс, твой личный консультант из магазина «Авангард».\n\n"
        "Здесь мы можем спокойно подобрать напольное покрытие или обои под твою ситуацию. "
        "Расскажу про плюсы и минусы, помогу с выбором, отвечу на любые вопросы.\n\n"
        "С чего начнём? Выбери, что тебя интересует:"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())
    context.user_data["state"] = MAIN

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Вот что я умею:\n\n"
        "В ЛИЧНЫХ СООБЩЕНИЯХ:\n"
        "— Консультирую по всем товарам\n"
        "— Помогаю подобрать покрытие под твой бюджет и ситуацию\n"
        "— Принимаю обратную связь и жалобы\n"
        "— Могу передать вопрос живому консультанту\n\n"
        "В КАНАЛЕ:\n"
        "— Пишу полезные посты и лайфхаки\n"
        "— Отвечаю на общие вопросы\n\n"
        "КАТАЛОГ:\n"
        "/linoleum | /laminat | /quartzvinyl | /wallpaper\n"
        "/compare | /faq | /tips | /consult | /feedback\n\n"
        "А можешь просто написать мне свой вопрос — я отвечу! 😊"
    )
    await update.message.reply_text(text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Магазин «Авангард» — это напольные покрытия и обои с душой. 🏡\n"
        "Работаем для вас каждый день с 9:00 до 18:30.\n"
        "Мы не просто продаём — мы помогаем найти идеальное решение для вашего дома.\n\n"
        "Нужен совет? Просто напиши мне в личные сообщения — обсудим всё детально!"
    )
    await update.message.reply_text(text)

# ---------- Главный обработчик текстовых сообщений ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    state = context.user_data.get("state", MAIN)

    # Глобальные кнопки
    if text == "🏠 В начало":
        await start(update, context)
        return
    if text in ("💡 Помоги подобрать",):
        await start_wizard(update, context)
        return
    if text in ("📞 Консультант", "📞 Связаться с консультантом"):
        await consult_handler(update, context)
        return
    if text in ("🔧 Лайфхак", "🔧 Ещё лайфхак"):
        await tips_handler(update, context)
        return
    if text == "⚖️ Что выбрать?":
        await compare_menu(update, context)
        return
    if text == "💬 Обратная связь":
        await feedback_start(update, context)
        return
    if text == "🔄 Подобрать заново":
        await start_wizard(update, context)
        return
    if text == "⬅ Назад":
        await start(update, context)  # упрощённый возврат
        return

    # Обработка по состояниям
    if state == MAIN:
        await main_menu_actions(update, context, text)
    elif state in (LINOLEUM_MENU, LAMINAT_MENU, KVC_MENU, WALLPAPER_MENU):
        await category_info_handler(update, context, text)
    elif state == CHOOSE_ROOM:
        await choose_room_step(update, context, text)
    elif state == CHOOSE_LOAD:
        await choose_load_step(update, context, text)
    elif state == CHOOSE_BUDGET:
        await choose_budget_step(update, context, text)
    elif state == COMPARE_MENU:
        await compare_actions(update, context, text)
    elif state == TIPS_MENU:
        await tips_handler(update, context)
    elif state == FEEDBACK_INIT:
        await feedback_init_step(update, context, text)
    elif state == FEEDBACK_TEXT:
        await feedback_text_step(update, context, text)
    elif state == FEEDBACK_DATE:
        await feedback_date_step(update, context, text)
    elif state == CONSULT:
        await consult_done(update, context)
    else:
        await update.message.reply_text("Я не понял. Давай вернёмся в главное меню.")
        await start(update, context)

# ---------- Главное меню (категории) ----------
async def main_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if text == "🟫 Линолеум":
        await show_category(update, context, "linoleum")
    elif text == "🟧 Ламинат":
        await show_category(update, context, "laminat")
    elif text == "⬜ Кварц-винил":
        await show_category(update, context, "kvc")
    elif text == "🎨 Обои":
        await show_category(update, context, "wallpaper")
    else:
        await update.message.reply_text("Пожалуйста, используй клавиатуру.")

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE, cat: str) -> None:
    data = {
        "linoleum": {
            "text": (
                "🟫 ЛИНОЛЕУМ\n"
                "Рулонное покрытие. Ширина 1,5–5 м, толщина 1,8–6,5 мм.\n"
                "Главный плюс: широкий рулон (4–5 м) = комната без стыков.\n"
                "Служит 5–10 лет (полукоммерческий класс).\n\n"
                "Что хочешь узнать?"
            ),
            "kb": [
                ["📋 Виды линолеума", "⭐ Классы"],
                ["💰 Цена", "🆚 Сравнить с кварц-винилом"],
                ["💡 Помоги подобрать"],
                ["⬅ Назад", "🏠 В начало"],
            ],
            "state": LINOLEUM_MENU,
        },
        "laminat": {
            "text": (
                "🟧 ЛАМИНАТ\n"
                "Многослойная планка на HDF-плите. Замковое соединение.\n"
                "Классы: 31 (спальня), 32 (оптимум), 33 (кухня), 34 (офисы).\n"
                "Толщина: 8/10/12 мм.\n\n"
                "Что хочешь узнать?"
            ),
            "kb": [
                ["📋 Классы ламината", "🔒 Типы замков"],
                ["💰 Цена", "💧 Влагостойкий"],
                ["💡 Помоги подобрать"],
                ["⬅ Назад", "🏠 В начало"],
            ],
            "state": LAMINAT_MENU,
        },
        "kvc": {
            "text": (
                "⬜ КВАРЦ-ВИНИЛ (LVT, SPC)\n"
                "Плитка ПВХ + кварцевый песок. 100% водостойкий. Служит 20–25 лет.\n"
                "Виды: SPC (жёсткий), LVT замковый, LVT клеевой.\n"
                "Не продавливается мебелью, совместим с тёплым полом.\n\n"
                "Что хочешь узнать?"
            ),
            "kb": [
                ["📋 Виды кварц-винила", "🆚 Отличие от линолеума"],
                ["💰 Цена", "🔥 Тёплый пол"],
                ["💡 Помоги подобрать"],
                ["⬅ Назад", "🏠 В начало"],
            ],
            "state": KVC_MENU,
        },
        "wallpaper": {
            "text": (
                "🎨 ОБОИ\n"
                "Типы: бумажные, виниловые, флизелиновые, стеклообои, текстильные, жидкие.\n"
                "Главное правило: одна партия на все рулоны = одинаковый оттенок.\n\n"
                "Что хочешь узнать?"
            ),
            "kb": [
                ["📋 Типы обоев", "🧼 Моющиеся"],
                ["💰 Цена", "🖌️ Под покраску"],
                ["💡 Помоги подобрать"],
                ["⬅ Назад", "🏠 В начало"],
            ],
            "state": WALLPAPER_MENU,
        },
    }
    d = data[cat]
    await update.message.reply_text(
        d["text"],
        reply_markup=ReplyKeyboardMarkup(d["kb"], resize_keyboard=True),
    )
    context.user_data["state"] = d["state"]

# ---------- Инфо внутри категорий ----------
async def category_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    info = {
        "📋 Виды линолеума": "Виды: гомогенный (однослойный, сверхпрочный) и гетерогенный (многослойный, лучше звукоизоляция).",
        "⭐ Классы": "Классы износа: 21–23 (спальни), 31–33 (кухни/коридоры) — оптимально, 41–43 (коммерция).",
        "📋 Классы ламината": "Классы нагрузки: 31 (AC3) – спальня, 32 (AC4) – гостиная/детская, 33 (AC5) – кухня/прихожая, 34 (AC6) – офисы.",
        "🔒 Типы замков": "Click – защёлкивается под углом (проще), Lock – забивной (дешевле).",
        "💧 Влагостойкий": "Для кухни и прихожей выбирай ламинат с влагостойкой пропиткой и воском на замках.",
        "📋 Виды кварц-винила": "SPC – каменный композит (жёсткий), LVT замковый – удобен для дома, LVT клеевой – для больших площадей.",
        "🆚 Отличие от линолеума": "Линолеум – рулон, мягче, служит 5–10 лет. Кварц-винил – плитка, прочнее, 20–25 лет.",
        "🔥 Тёплый пол": "Кварц-винил совместим с тёплым полом (почти все модели). Линолеум – только со спецмаркировкой.",
        "📋 Типы обоев": "Бумажные, виниловые, флизелиновые, стеклообои, текстильные, жидкие.",
        "🧼 Моющиеся": "Виниловые и стеклообои — отлично моются, подходят для кухни и прихожей.",
        "🖌️ Под покраску": "Флизелиновые и стеклообои можно перекрашивать, скрывают неровности.",
        "🍳 Что лучше на кухню?": "Кварц-винил идеален. Если эконом — полукоммерческий линолеум.",
        "🔥 Что на тёплый пол?": "Кварц-винил однозначно. Линолеум — проверяй маркировку.",
    }
    if text in info:
        await update.message.reply_text(info[text])
    elif text == "💰 Цена":
        await update.message.reply_text(
            "Цены: предлагаю связаться с консультантом — он на месте и поможет подобрать подходящее."
        )
    elif text == "🆚 Сравнить с кварц-винилом":
        await update.message.reply_text("Сравнение: линолеум vs кварц-винил. /compare")
    else:
        await update.message.reply_text("Выбери пункт меню.")

# ---------- Визуальный подбор (визард) ----------
async def start_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Давай подберём идеальное покрытие! 🏠\nДля начала скажи — для какой комнаты выбираем?"
    kb = ReplyKeyboardMarkup(
        [
            ["🍳 Кухня", "🛋️ Гостиная"],
            ["🛏️ Спальня", "👶 Детская"],
            ["🚪 Прихожая", "🛁 Ванная"],
            ["🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=kb)
    context.user_data["state"] = CHOOSE_ROOM
    context.user_data["wizard"] = {}

async def choose_room_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    rooms = ["🍳 Кухня", "🛋️ Гостиная", "🛏️ Спальня", "👶 Детская", "🚪 Прихожая", "🛁 Ванная"]
    if text not in rooms:
        await update.message.reply_text("Выбери комнату на клавиатуре.")
        return
    context.user_data["wizard"]["room"] = text

    if text == "🛁 Ванная":
        question = "Ванная — повышенная влажность! 💧\nУточню: важна ли влагостойкость?"
        kb = ReplyKeyboardMarkup(
            [["💧 Важна влагостойкость"], ["⬅ Другая комната", "🏠 В начало"]], resize_keyboard=True
        )
    elif text in ("🍳 Кухня", "🚪 Прихожая"):
        question = f"{text} — отличный выбор! 🏠\nТеперь уточню: есть ли дома дети или животные? Это важно для выбора прочности покрытия."
        kb = ReplyKeyboardMarkup(
            [
                ["🐕 Есть питомцы", "👶 Есть дети"],
                ["👨 Только взрослые"],
                ["⬅ Другая комната", "🏠 В начало"],
            ],
            resize_keyboard=True,
        )
    else:
        question = f"{text} — уютное место! 🏡\nЕсть ли дома дети или животные? А может, у кого-то аллергия?"
        kb = ReplyKeyboardMarkup(
            [
                ["🐕 Есть питомцы", "👶 Есть дети"],
                ["👨 Только взрослые", "🤧 Аллергия (важно!)"],
                ["⬅ Другая комната", "🏠 В начало"],
            ],
            resize_keyboard=True,
        )

    await update.message.reply_text(question, reply_markup=kb)
    context.user_data["state"] = CHOOSE_LOAD

async def choose_load_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if text == "⬅ Другая комната":
        await start_wizard(update, context)
        return
    valid_loads = ["🐕 Есть питомцы", "👶 Есть дети", "👨 Только взрослые", "🤧 Аллергия (важно!)", "💧 Важна влагостойкость"]
    if text not in valid_loads:
        await update.message.reply_text("Выбери вариант нагрузки на клавиатуре.")
        return
    context.user_data["wizard"]["load"] = text

    question = "Понял, спасибо!\nПоследний вопрос — на какой бюджет ориентируемся?"
    kb = ReplyKeyboardMarkup(
        [
            ["💰 Эконом", "💎 Средний"],
            ["👑 Премиум", "🤔 Не знаю"],
            ["⬅ Назад", "🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(question, reply_markup=kb)
    context.user_data["state"] = CHOOSE_BUDGET

async def choose_budget_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if text not in ("💰 Эконом", "💎 Средний", "👑 Премиум", "🤔 Не знаю"):
        await update.message.reply_text("Выбери бюджет на клавиатуре.")
        return
    context.user_data["wizard"]["budget"] = text
    await show_recommendation(update, context)

async def show_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    w = context.user_data["wizard"]
    room = w.get("room", "")
    load = w.get("load", "")
    budget = w.get("budget", "")

    if room in ("🍳 Кухня", "🛁 Ванная"):
        if budget == "💰 Эконом":
            mat = "полукоммерческий линолеум (31–33 класс)"
            desc = "Бюджетный, водостойкий, без стыков."
        else:
            mat = "кварц-винил (SPC)"
            desc = "100% водостойкий, не боится воды и грязи, служит 20–25 лет."
    elif room == "🚪 Прихожая":
        if load in ("🐕 Есть питомцы", "👶 Есть дети"):
            if budget == "💰 Эконом":
                mat = "полукоммерческий линолеум"
                desc = "Бюджетное решение, легко моется."
            else:
                mat = "кварц-винил (SPC или LVT)"
                desc = "Прочный, не боится когтей и грязи, тёплый."
        else:
            if budget == "💰 Эконом":
                mat = "полукоммерческий линолеум"
                desc = "Надёжный и недорогой вариант."
            else:
                mat = "ламинат 32–33 класса или кварц-винил"
                desc = "Эстетично и устойчиво к истиранию."
    else:
        if load == "🤧 Аллергия (важно!)":
            if budget == "💰 Эконом":
                mat = "натуральный линолеум (мармолеум)"
                desc = "Гипоаллергенный, из натуральных компонентов."
            else:
                mat = "кварц-винил (LVT)"
                desc = "Безопасен, не собирает пыль, тёплый."
        else:
            if budget == "💰 Эконом":
                mat = "ламинат 32 класса"
                desc = "Оптимальный по цене и качеству."
            elif budget == "👑 Премиум":
                mat = "кварц-винил или инженерная доска"
                desc = "Премиальный вид и высокая износостойкость."
            else:
                mat = "ламинат 32 класса или LVT замковый"
                desc = "Хорошая имитация дерева, простота укладки."

    text = (
        f"Исходя из твоих ответов:\n"
        f"▪️ Комната: {room}\n"
        f"▪️ Нагрузка: {load}\n"
        f"▪️ Бюджет: {budget}\n\n"
        f"Мой совет — {mat}. Вот почему:\n"
        f"✅ {desc}\n\n"
        "Если хочешь узнать цену — нажми «Связаться с консультантом», менеджер подберёт варианты под твой бюджет."
    )
    kb = ReplyKeyboardMarkup(
        [
            ["📞 Связаться с консультантом", "📋 Подробнее про материал"],
            ["🔄 Подобрать заново"],
            ["🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=kb)
    context.user_data["state"] = RECOMMENDATION

# ---------- Сравнение ----------
async def compare_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "⚖️ СРАВНЕНИЕ: ЛИНОЛЕУМ vs КВАРЦ-ВИНИЛ\n\n"
        "Коротко о главном:\n\n"
        "ЛИНОЛЕУМ:\n"
        "➕ Дёшево, комната без стыков\n"
        "➖ Мягкий, мебель продавливает, служит 5–10 лет\n\n"
        "КВАРЦ-ВИНИЛ:\n"
        "➕ Жёсткий, водостойкий 100%, служит 20–25 лет\n"
        "➖ Дороже линолеума\n\n"
        "Что именно тебя интересует?"
    )
    kb = ReplyKeyboardMarkup(
        [
            ["🟫 Подробнее про линолеум", "⬜ Подробнее про кварц-винил"],
            ["🍳 Что лучше на кухню?", "🔥 Что на тёплый пол?"],
            ["💡 Помоги подобрать"],
            ["🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=kb)
    context.user_data["state"] = COMPARE_MENU

async def compare_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    await category_info_handler(update, context, text)

# ---------- Лайфхаки ----------
async def tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tip = random.choice(TIPS)
    kb = ReplyKeyboardMarkup(
        [
            ["🔧 Ещё лайфхак"],
            ["💡 Помоги подобрать", "🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(f"🔧 ЛАЙФХАК ДНЯ\n\n{tip}", reply_markup=kb)
    context.user_data["state"] = TIPS_MENU

# ---------- Консультант ----------
async def consult_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Хочешь пообщаться с живым консультантом? 🙋‍♂️\n"
        "Он на месте и поможет подобрать вариант, сориентирует по цене и наличию.\n"
        "Просто напиши свой вопрос и контакты (телефон или @username), и я передам обращение менеджеру.\n"
        "Мы работаем с 9:00 до 18:30 — свяжемся в ближайшее время!"
    )
    kb = ReplyKeyboardMarkup(
        [["💡 Помоги подобрать", "⬅ Назад"], ["🏠 В начало"]],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=kb)
    context.user_data["state"] = CONSULT

async def consult_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Спасибо! Я передал твой вопрос. Ожидай ответа.")
    await start(update, context)

# ---------- Обратная связь ----------
async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Нам важно твоё мнение! 💬\n"
        "Расскажи, что случилось или просто поделись впечатлениями о магазине «Авангард». Я передам обращение менеджеру, и с тобой свяжутся в ближайшее время.\n"
        "Чтобы мы могли быстрее помочь, уточни, пожалуйста:\n"
        "— Когда была покупка?\n"
        "— Что именно пошло не так или что хочешь отметить?\n\n"
        "Я внимательно тебя слушаю 👇"
    )
    kb = ReplyKeyboardMarkup(
        [
            ["🛍️ Проблема с товаром", "👍 Всё отлично"],
            ["🤔 Есть вопрос"],
            ["🏠 В начало"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=kb)
    context.user_data["state"] = FEEDBACK_INIT

async def feedback_init_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if text in ("🛍️ Проблема с товаром", "👍 Всё отлично", "🤔 Есть вопрос"):
        await update.message.reply_text("Спасибо! Расскажи подробнее, и я передам менеджеру.")
        context.user_data["feedback_type"] = text
        context.user_data["state"] = FEEDBACK_TEXT
    else:
        await update.message.reply_text("Выбери вариант на клавиатуре.")

async def feedback_text_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    context.user_data["feedback_text"] = text
    await update.message.reply_text("Когда была покупка? Напиши дату, и я передам менеджеру.")
    context.user_data["state"] = FEEDBACK_DATE

async def feedback_date_step(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    await update.message.reply_text("Спасибо! Я передал информацию менеджеру. С тобой свяжутся в ближайшие 15–20 минут.")
    await start(update, context)

# ---------- Точка входа (вебхуки) ----------
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Получаем порт от Render
    port = int(os.environ.get("PORT", 8443))

    # Формируем webhook URL
    # Приоритет: явно заданный WEBHOOK_URL, затем RENDER_EXTERNAL_URL + /telegram
    webhook_url = os.environ.get("WEBHOOK_URL")
    if not webhook_url:
        external_url = os.environ.get("RENDER_EXTERNAL_URL")
        if external_url:
            webhook_url = f"{external_url}/telegram"
        else:
            # Если ничего не задано — только для локального тестирования
            webhook_url = f"https://localhost:{port}/telegram"

    logger.info(f"Устанавливаю вебхук: {webhook_url}")
    await app.bot.set_webhook(url=webhook_url)

    # Запускаем веб-сервер
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    asyncio.run(main())
