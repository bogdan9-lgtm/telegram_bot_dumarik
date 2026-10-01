from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from catalog import LANGUAGES, PERSONS, QUIZ_TOPICS, RECOMMEND_CATEGORIES

CB_RANDOM_MORE = "random:more"
CB_FINISH = "common:finish"


class QuizTopicCallback(CallbackData, prefix="quiz_topic"):
    topic: str


class QuizActionCallback(CallbackData, prefix="quiz_action"):
    action: str


random_fact_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Хочу ще факт", callback_data=CB_RANDOM_MORE)],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)

finish_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)


# ==== QUIZ ====

def quiz_topics_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, name in QUIZ_TOPICS.items():
        builder.button(text=name, callback_data=QuizTopicCallback(topic=key))

    builder.adjust(2)
    return builder.as_markup()


quiz_result_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➡️ Ще питання",
                callback_data=QuizActionCallback(action="next").pack(),
            ),
            InlineKeyboardButton(
                text="🔄 Змінити тему",
                callback_data=QuizActionCallback(action="change_topic").pack(),
            ),
        ],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)

# ==== TALK ====

class TalkCallback(CallbackData, prefix="talk"):
    person: str


def talk_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, name in PERSONS.items():
        builder.button(text=name, callback_data=TalkCallback(person=key))

    builder.adjust(2)

    return builder.as_markup()


# ==== TRANSLATE ====

CB_TRANSLATE_CHANGE = "translate:change"

class LanguageCallback(CallbackData, prefix="language"):
    code: str


def languages_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for code, name in LANGUAGES.items():
        builder.button(text=name, callback_data=LanguageCallback(code=code))

    builder.adjust(2)
    return builder.as_markup()


translate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Інша мова", callback_data=CB_TRANSLATE_CHANGE)],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)


# ==== RECOMMEND ====

CB_RECOMMEND_DISLIKE = "recommend:dislike"


class CategoryCallback(CallbackData, prefix="category"):
    key: str


def choose_recommend_categories_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, name in RECOMMEND_CATEGORIES.items():
        builder.button(text=name, callback_data=CategoryCallback(key=key))

    builder.adjust(1)
    return builder.as_markup()


recommend_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👎 Не подобається", callback_data=CB_RECOMMEND_DISLIKE)],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)