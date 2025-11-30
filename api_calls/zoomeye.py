import os
import json

import requests

from lib.settings import start_animation
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    API_URLS,
    HOST_FILE,
    write_to_file
)


class ZoomEyeAPIHook(object):

    """
    API hook for the ZoomEye API using API-KEY authentication
    """

    def __init__(self, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.api_key = token
        self.query = query
        self.host_file = HOST_FILE
        self.proxy = proxy
        self.user_agent = agent
        self.save_mode = save_mode

    def search(self):
        """
        connect to the API and pull all the IP addresses that are associated with the
        given query
        """
        start_animation("searching ZoomEye with given query '{}'".format(self.query))
        discovered_zoomeye_hosts = set()
        try:
            if self.user_agent is None:
                headers = {"API-KEY": self.api_key}
            else:
                headers = {
                    "API-KEY": self.api_key,
                    "User-Agent": self.user_agent["User-Agent"]
                }
            params = {"query": self.query, "page": "1", "facet": "ipv4"}
            req = requests.get(
                API_URLS["zoomeye"],
                params=params, headers=headers, proxies=self.proxy
            )
            _json_data = req.json()
            for item in _json_data["matches"]:
                if len(item["ip"]) > 1:
                    for ip in item["ip"]:
                        discovered_zoomeye_hosts.add(ip)
                else:
                    discovered_zoomeye_hosts.add(str(item["ip"][0]))
            write_to_file(discovered_zoomeye_hosts, self.host_file, mode=self.save_mode)
            return True
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))

