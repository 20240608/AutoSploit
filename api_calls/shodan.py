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


class ShodanAPIHook(object):

    """
    Shodan API hook, saves us from having to install another dependency
    """

    def __init__(self, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.token = token
        self.query = query
        self.proxy = proxy
        self.user_agent = agent
        self.host_file = HOST_FILE
        self.save_mode = save_mode

    def search(self):
        """
        connect to the API and grab all IP addresses associated with the provided query
        """
        start_animation("searching Shodan with given query '{}'".format(self.query))
        discovered_shodan_hosts = set()
        try:
            req = requests.get(
                API_URLS["shodan"].format(query=self.query, token=self.token),
                proxies=self.proxy, headers=self.user_agent,
                timeout=30
            )

            # Check HTTP status code
            if req.status_code != 200:
                raise AutoSploitAPIConnectionError(
                    "Shodan API returned status code {}: {}".format(
                        req.status_code, req.text[:200]
                    )
                )

            json_data = json.loads(req.content)

            # Check if API returned an error
            if "error" in json_data:
                raise AutoSploitAPIConnectionError(
                    "Shodan API error: {}".format(json_data["error"])
                )

            # Check if matches field exists
            if "matches" not in json_data:
                warning("Shodan API response does not contain 'matches' field")
                return False

            if len(json_data["matches"]) == 0:
                warning("No results found for query '{}'".format(self.query))
                return False

            # Process results
            for match in json_data["matches"]:
                if "ip_str" in match:
                    discovered_shodan_hosts.add(match["ip_str"])

            if len(discovered_shodan_hosts) > 0:
                info("Found {} hosts from Shodan".format(len(discovered_shodan_hosts)))
                write_to_file(discovered_shodan_hosts, self.host_file, mode=self.save_mode)
            else:
                warning("No valid IP addresses found in Shodan results")

            return True

        except json.JSONDecodeError as e:
            raise AutoSploitAPIConnectionError("Failed to parse Shodan API response: {}".format(str(e)))
        except requests.exceptions.Timeout:
            raise AutoSploitAPIConnectionError("Shodan API request timed out")
        except requests.exceptions.ConnectionError:
            raise AutoSploitAPIConnectionError("Failed to connect to Shodan API")
        except AutoSploitAPIConnectionError:
            raise
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))


