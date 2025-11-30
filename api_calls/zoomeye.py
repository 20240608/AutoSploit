import json

import requests

from lib.settings import start_animation
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    API_URLS,
    HOST_FILE,
    write_to_file
)
from lib.output import info, warning


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
                    "User-Agent": self.user_agent.get("User-Agent", "")
                }
            params = {"query": self.query, "page": "1", "facet": "ipv4"}
            req = requests.get(
                API_URLS["zoomeye"],
                params=params, headers=headers, proxies=self.proxy,
                timeout=30
            )

            # Check HTTP status code
            if req.status_code == 401 or req.status_code == 403:
                raise AutoSploitAPIConnectionError(
                    "ZoomEye API authentication failed - check your API key"
                )

            if req.status_code != 200:
                raise AutoSploitAPIConnectionError(
                    "ZoomEye API returned status code {}: {}".format(
                        req.status_code, req.text[:200]
                    )
                )

            _json_data = req.json()

            # Check if API returned an error
            if "error" in _json_data:
                raise AutoSploitAPIConnectionError(
                    "ZoomEye API error: {}".format(_json_data["error"])
                )

            # Check if matches field exists
            if "matches" not in _json_data:
                warning("ZoomEye API response does not contain 'matches' field")
                return False

            if len(_json_data["matches"]) == 0:
                warning("No results found for query '{}'".format(self.query))
                return False

            # Process results
            for item in _json_data["matches"]:
                if "ip" in item:
                    if isinstance(item["ip"], list):
                        if len(item["ip"]) > 0:
                            for ip in item["ip"]:
                                discovered_zoomeye_hosts.add(ip)
                    else:
                        discovered_zoomeye_hosts.add(str(item["ip"]))

            if len(discovered_zoomeye_hosts) > 0:
                info("Found {} hosts from ZoomEye".format(len(discovered_zoomeye_hosts)))
                write_to_file(discovered_zoomeye_hosts, self.host_file, mode=self.save_mode)
            else:
                warning("No valid IP addresses found in ZoomEye results")

            return True

        except json.JSONDecodeError as e:
            raise AutoSploitAPIConnectionError("Failed to parse ZoomEye API response: {}".format(str(e)))
        except requests.exceptions.Timeout:
            raise AutoSploitAPIConnectionError("ZoomEye API request timed out")
        except requests.exceptions.ConnectionError:
            raise AutoSploitAPIConnectionError("Failed to connect to ZoomEye API")
        except AutoSploitAPIConnectionError:
            raise
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))

