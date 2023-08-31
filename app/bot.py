from aiogram import Bot, Dispatcher, executor, types

import re
import db
import api
import settings
import asyncio

if settings.SENTRY_DSN:
    import logging
    import sentry_sdk
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            AsyncioIntegration(),
            LoggingIntegration(level=logging.ERROR),
        ],
        traces_sample_rate=1.0
    )


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)


# Admin Bot Commands

def require_admin(message):
    return message.chat.type == types.ChatType.PRIVATE and message.chat.id == settings.OWNER_ID


@dp.message_handler(require_admin, commands=['check',], content_types=[types.ContentType.TEXT])
async def check(message: types.Message):
    wait_msg = await message.reply('Обработка результатов за последние 12 часов...')

    top_performers = await _get_top_performers()
    header = 'Решенные задачи за 12 часов\n\n'
    text = '\n'.join([f'<b>{len(subs)}</b>: {_user_to_str(u)} {[s.name for s in subs]}' for u, subs in top_performers.items()])

    await wait_msg.delete()

    await _chunked_response(header + text, message)


async def _get_top_performers() -> dict[db.User, list[api.Submission]]:
    user_submissions = {}

    for u in db.list_users():
        if subs := await api.fetch_latest_submissions(u.profile_url):
            user_submissions[u] = subs
        await asyncio.sleep(0.5)

    return dict(sorted(user_submissions.items(), key=lambda item: len(item[1]), reverse=True))


def _user_to_str(u: db.User) -> str:
    if u.username:
        return f'@{u.username}'
    return f'[{u.name}]({u.profile_url})'


# Public Bot Commands


def require_private(message: types.Message):
    return message.chat.type == types.ChatType.PRIVATE


@dp.message_handler(require_private, commands=['start', 'help'])
async def welcome(message: types.Message):
    text = '''Отправьте ссылку на свой leetcode профиль: "https://leetcode.com/username/"'''
    await message.reply(text, disable_web_page_preview=True)


@dp.message_handler(require_private, content_types=[types.ContentType.TEXT])
async def handle_text(message: types.Message):
    profile_url = message.text
    if not _is_valid_profile_url(profile_url):
        await message.reply('Отправьте ссылку на свой leetcode профиль "https://leetcode.com/username/"')
        return

    await _set_up_profile(message, profile_url)


async def _set_up_profile(message: types.Message, profile_url: str):
    try:
        latest_submissions = await api.fetch_latest_submissions(profile_url, today_only=False)
        if not latest_submissions:
            await message.reply(f'Не найдено ни одного решения')
            return
    except ValueError as err:
        logging.exception('Error fetch submission')
        await message.reply(f'Ошибка {err}')
        return

    db.add_profile(message.from_user.id, message.from_user.username, message.from_user.full_name, profile_url)
    await message.reply(f'Профиль добавлен')


async def _chunked_response(text: str, message: types.Message):
    i = 0
    chunk_size = 4000  # telegram limit
    while True:
        if chunk := text[i: i + chunk_size]:
            await message.reply(chunk, parse_mode=types.ParseMode.HTML)
            i += chunk_size
        else:
            return

def _is_valid_profile_url(url):
    pattern = r"https://leetcode\.com/[a-zA-Z0-9_]+/?"
    return bool(re.fullmatch(pattern, url))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
