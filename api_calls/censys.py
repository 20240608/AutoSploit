import json

import requests

import lib.settings
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    HOST_FILE,
    API_URLS,
    write_to_file
)
from lib.output import info, warning


class CensysAPIHook(object):

    """
    Censys API hook
    """

    def __init__(self, identity=None, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.id = identity
        self.token = token
        self.query = query
        self.proxy = proxy
        self.user_agent = agent
        self.host_file = HOST_FILE
        self.save_mode = save_mode

    def search(self):
        """
        connect to the Censys API and pull all IP addresses from the provided query
        """
        discovered_censys_hosts = set()
        try:
            lib.settings.start_animation("searching Censys with given query '{}'".format(self.query))
            req = requests.post(
                API_URLS["censys"], auth=(self.id, self.token),
                json={"query": self.query}, headers=self.user_agent,
                proxies=self.proxy,
                timeout=30
            )

            # Check HTTP status code
            if req.status_code == 401 or req.status_code == 403:
                raise AutoSploitAPIConnectionError(
                    "Censys API authentication failed - check your API credentials"
                )

            if req.status_code != 200:
                raise AutoSploitAPIConnectionError(
                    "Censys API returned status code {}: {}".format(
                        req.status_code, req.text[:200]
                    )
                )

            json_data = req.json()

            # Check if API returned an error
            if "error" in json_data:
                raise AutoSploitAPIConnectionError(
                    "Censys API error: {}".format(json_data["error"])
                )

            # Check if results field exists (Censys uses 'results' instead of 'matches')
            if "results" not in json_data:
                warning("Censys API response does not contain 'results' field")
                return False

            if len(json_data["results"]) == 0:
                warning("No results found for query '{}'".format(self.query))
                return False

            # Process results
            for item in json_data["results"]:
                if "ip" in item:
                    discovered_censys_hosts.add(str(item["ip"]))

            if len(discovered_censys_hosts) > 0:
                info("Found {} hosts from Censys".format(len(discovered_censys_hosts)))
                write_to_file(discovered_censys_hosts, self.host_file, mode=self.save_mode)
            else:
                warning("No valid IP addresses found in Censys results")

            return True

        except json.JSONDecodeError as e:
            raise AutoSploitAPIConnectionError("Failed to parse Censys API response: {}".format(str(e)))
        except requests.exceptions.Timeout:
            raise AutoSploitAPIConnectionError("Censys API request timed out")
        except requests.exceptions.ConnectionError:
            raise AutoSploitAPIConnectionError("Failed to connect to Censys API")
        except AutoSploitAPIConnectionError:
            raise
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))