import requests
import threading
import logging

logger = logging.getLogger("scraper")


class CookiesManager:

    def __init__(self, headers):
        self._headers = headers
        self.renew_cookies()
        self._start_cookie_renewal_thread()

    def renew_cookies(self):
        logger.info("Renewing cookies")
        response = requests.get("https://www.vinted.fr", headers=self._headers)
        cookies = "; ".join(
            [f"{cookie.name}={cookie.value}" for cookie in response.cookies]
        )
        self._headers["Cookie"] = cookies

    def _start_cookie_renewal_thread(self):
        renewal_thread = threading.Thread(
            target=self._periodic_cookie_renewal, daemon=True
        )
        renewal_thread.start()

    def _periodic_cookie_renewal(self):
        while True:
            threading.Event().wait(60 * 10)  # 10 minutes
            self.renew_cookies()
