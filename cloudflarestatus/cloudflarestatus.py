#!/usr/bin/env python
import argparse
import json
import logging
import re
import time

import requests
from bs4 import BeautifulSoup

UNKNOWN = "unknown"
OPERATIONAL = "operational"
PARTIAL_OUTAGE = "partial_outage"
UNDER_MAINTENANCE = "under_maintenance"

# Raw status to formatted status.
STATUS = {
    "operational": OPERATIONAL,
    "partial outage": PARTIAL_OUTAGE,
    "under maintenance": UNDER_MAINTENANCE,
    "unknown": UNKNOWN,
}


class CloudflarestatusException(Exception):
    pass


class Cloudflarestatus:
    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Make Cloudflarestatus a singleton.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url="https://www.cloudflarestatus.com/", ttl=60):
        self.url = url
        self.ttl = ttl
        self.session = requests.Session()
        if not self._initialized:
            self.cached_response = dict(timestamp=0, content=None)
            self._initialized = True

    def get(self, url, timeout=5, max_tries=3):
        response = None

        tries = max_tries
        while tries > 0:
            try:
                response = self.session.get(url, timeout=timeout)
            except requests.exceptions.RequestException as err:
                logging.error(f"url={url} - err={err}")
            else:
                logging.debug(f"url={url} - status_code={response.status_code}")
                if response.status_code == 200:
                    break
                response = None
            logging.warning(f"retrying url={url}")
            tries -= 1
            time.sleep(1)

        return response

    def get_cached_response(self):
        now = int(time.time())
        if now - self.cached_response["timestamp"] > self.ttl:
            response = self.get(self.url)
            if response is not None:
                self.cached_response = dict(timestamp=now, content=response.content)
            else:
                raise CloudflarestatusException(f"Unable to fetch {self.url}")

        return self.cached_response

    def all_dc(self):
        all_dc_status = {}

        cache = self.get_cached_response()
        if not cache["content"]:
            raise CloudflarestatusException(f"No content from {self.url}")

        soup = BeautifulSoup(cache["content"], "html.parser")
        datacenters = soup.find_all(class_="component-inner-container")
        for datacenter in datacenters:
            raw_name = datacenter.find(class_="name").text.strip()
            raw_status = datacenter.find(class_="component-status").text.strip()
            match = re.match(r"^(?P<name>.*?)\s*-\s*\((?P<code>\w+)\)$", raw_name)
            if match:
                name = match.group("name")
                code = match.group("code")
                status = STATUS.get(raw_status.lower(), UNKNOWN)
                logging.debug(f"code={code} - name={name} - status={status}")
                all_dc_status[code] = dict(
                    code=code,
                    name=name,
                    status=status,
                    timestamp=cache["timestamp"],
                )

        return dict(sorted(all_dc_status.items()))

    def dc(self, *args):
        all_dc_status = self.all_dc()
        if not args:
            return all_dc_status
        args = [arg.upper() for arg in args]
        return dict((k, v) for k, v in all_dc_status.items() if k in args)


def dc(*args):
    cloudflarestatus = Cloudflarestatus()
    return cloudflarestatus.dc(*args)


def main():
    parser = argparse.ArgumentParser(
        prog="cloudflarestatus",
        description="Parse Cloudflare System Status from https://www.cloudflarestatus.com",
    )

    parser.add_argument(
        "-d",
        "--data-center",
        nargs="+",
        default=[],
        help="(Optional) Get status for the specified space-separated data centers. "
        "If unspecified, status for all data centers will be shown. "
        "Example: -d hba syd",
    )

    args = parser.parse_args()
    data_center = args.data_center

    cloudflarestatus = Cloudflarestatus()
    results = cloudflarestatus.dc(*data_center)

    results = json.dumps(results)
    print(results)


if __name__ == "__main__":
    main()
