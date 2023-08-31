import aiohttp
from dataclasses import dataclass
import settings
from bs4 import BeautifulSoup  # beautifulsoup4


@dataclass
class Submission:
    url: str
    name: str
    time: str


async def fetch_latest_submissions(profile_url, today_only=True) -> list[Submission]:
    text = await _fetch_profile(profile_url)
    soup = BeautifulSoup(text, 'html.parser')

    submissions = soup.find_all('a', href=lambda x: x and x.startswith('/submissions/detail/'))

    latest_submissions = []
    for s in submissions:
        rel_url = s["href"].lstrip("/")
        abs_url = f'https://leetcode.com/{rel_url}'

        span_tags = s.find_all('span')
        name = span_tags[0].text
        time = span_tags[1].text

        if today_only:
            if 'year' in time:
                break
            if 'month' in time:
                break
            if 'day' in time:
                break
            if 'hours' in time:
                hours_ago = time.split()[0]
                if int(hours_ago) > 12:
                    break

        latest_submissions.append(Submission(url=abs_url, name=name, time=time))
    return latest_submissions


async def _fetch_profile(profile_url) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url, proxy=settings.PROXY, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
