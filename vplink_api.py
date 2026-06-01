import aiohttp
import logging

logger = logging.getLogger(__name__)

class VPLinkAPI:
    """
    Wrapper for vplink.in URL shortener API.
    API docs: https://vplink.in/api  (use your token)
    """

    BASE_URL = "https://vplink.in/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def shorten(self, long_url: str) -> str:
        """
        Shorten a URL using vplink.in API.
        Returns the shortened URL string, or original URL on failure.
        """
        if not self.api_key:
            logger.warning("VPLINK_API_KEY not set – returning original URL")
            return long_url

        params = {
            "api":  self.api_key,
            "url":  long_url,
            "format": "text"          # returns plain text URL
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        short = (await resp.text()).strip()
                        if short.startswith("http"):
                            return short
                        else:
                            logger.error(f"VPLink unexpected response: {short}")
                            return long_url
                    else:
                        logger.error(f"VPLink API error: HTTP {resp.status}")
                        return long_url
        except Exception as e:
            logger.error(f"VPLink request failed: {e}")
            return long_url   # Fallback to original Telegram invite link
