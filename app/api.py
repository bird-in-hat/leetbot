import aiohttp
from dataclasses import dataclass
import settings
import fake_agent
from bs4 import BeautifulSoup  # beautifulsoup4


@dataclass
class Submission:
    url: str
    name: str
    time: str


async def fetch_latest_submissions(profile_url, today_only=True) -> list[Submission]:
    soup = BeautifulSoup(await _fetch_profile(profile_url), 'html.parser')

    submissions = soup.find_all('a', href=lambda x: x and x.startswith('/submissions/detail/'))

    latest_submissions = []
    for s in submissions:
        span_tags = s.find_all('span')
        if today_only:
            if 'day' in span_tags[1].text:
                break
            if 'hours' in span_tags[1].text:
                hours_ago, _ = span_tags[1].text.split()
                if int(hours_ago) > 12:
                    break

        rel_url = s["href"].lstrip("/")
        abs_url = f'https://leetcode.com/{rel_url}'
        sub = Submission(url=abs_url, name=span_tags[0].text, time=span_tags[1])
        latest_submissions.append(sub)
    return latest_submissions


async def _fetch_profile(profile_url) -> str:
    headers = {
        'User-Agent': fake_agent.get_random_agent()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url, headers=headers, proxy=settings.PROXY, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
