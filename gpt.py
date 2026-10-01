import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=settings.OPENAI_TIMEOUT
)


async def ask(system_prompt: str, user_message: str | None = None) -> str | None:
    """Одиночний запит: системний промпт + (необовʼязково) одне повідомлення."""
    messages = [ {"role": "system", "content": system_prompt} ]

    if user_message:
        messages.append( {"role": "user", "content": user_message} )

    return await complete(messages)


async def ask_history(system_prompt: str, history: list[dict[str, str]]) -> str | None:
    """Запит з історією діалогу: системний промпт + усі попередні репліки."""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        *history
    ]
    return await complete(messages)


async def complete(messages: list[dict[str, str]]) -> str | None:
    """Повертає текст відповіді або None, якщо модель недоступна чи мовчить."""
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            reasoning_effort=settings.OPENAI_REASONING,
            max_completion_tokens=settings.OPENAI_MAX_TOKENS
        )
    except RateLimitError as e:
        logger.error("Забагато запитів до OpenAI: %r", e)
        return None
    except APITimeoutError as e:
        logger.error("Сервер OpenAI не відповідає: %r", e)
        return None
    except APIConnectionError as e:
        logger.error("Не вийшло зʼєднатись з OpenAI: %r", e)
        return None
    except APIStatusError as e:
        logger.error("OpenAI повернув помилку %s: %r", e.status_code, e)
        return None
    except Exception:
        logger.exception("Невідома помилка при запиті до OpenAI")
        return None

    choice = response.choices[0]
    content = (choice.message.content or "").strip()

    if not content:
        logger.warning(
            "ChatGPT повернув порожню відповідь: finish_reason=%s, токенів=%s",
            choice.finish_reason,
            response.usage.completion_tokens,
        )
        return None

    return content
