import requests
import urllib.parse
from abc import ABCMeta, abstractmethod
import os, toml
import diffbot
from . import const
from .error import DiffbotTokenError, DiffbotJobStatusError, DiffbotResponseError

"""this file contains Client, JobOperator and Extractor class
Generalized web_data fetcher using Diffbot.
"""
class Client():

    def __init__(self, token):
        self.token = token

    """base GET method for raw_data
    _fetch_raw_data(self, api_type: str, *, query: dict, headers: dict)
    """
    def _fetch_raw_data(self, api_type, *, query={}, headers={}):
        query.update({"token": self.token})

        # GET body content should be in querystring format (key/value pairs) in diffbot
        response_data = requests.get(self._get_end_point(api_type),
                            params=urllib.parse.urlencode(query),
                            headers=headers,
                            ).json()
        return self._check_response(response_data)

    def _post_raw_data(self, api_type, *, payload=None, headers=None):
        """base POST method for raw data
        base GET method for raw_data
        _fetch_raw_data(self, api_type: str, *, query: dict, headers: dict)
        """
        payload = payload or {}
        headers = headers or {}
        # POST body content should be in querystring format (key/value pairs) in diffbot
        response_data = requests.post(self._get_end_point(api_type),
                             data=urllib.parse.urlencode(payload),
                             headers=headers,
                             ).json()

        return self._check_response(response_data)

    # private API
    @classmethod
    def _get_end_point(cls, api_type):
        """get url in each diffbot api"""
        return "{}/v{}/{}".format(const.diffbot_url, const.diffbot_version, api_type)


    @staticmethod
    def _check_response(response_data):
        """raise exception if response_data contains error"""
        if isinstance(response_data, dict) and response_data.get("error") is not None:
            raise DiffbotResponseError(response_data["errorCode"], response_data["error"])
        return response_data


class JobOperator(Client, metaclass=ABCMeta):
    """wrapper of both bulk API and Crawlbot API"""

    def __init__(self, token, job_name, api_type):
        super().__init__(token)
        self.job_name = job_name
        self.api_type = api_type

    @classmethod
    def generate_apiurl(cls, apiurl_type, *, args=None):
        if args is None:
            return cls._get_end_point(apiurl_type)
        else:
            return cls._get_end_point(apiurl_type) + "?" + urllib.parse.urlencode(args)

    @staticmethod
    def _generate_args(*, custom_headers=None, notify_email=None, notify_webhook=None, repeat=None,
                                     max_rounds=None, page_process_pattern=None):
        return drop_none_value({
            "customHeaders" : custom_headers,
            "notifyEmail" : notify_email,
            "notifyWebhook" : notify_webhook,
            "repeat" : repeat,
            "maxRounds" : max_rounds,
            "pageProcessPattern" : page_process_pattern,
        })

    def lazy_fetch_extractors(self, job_index=0):
        """"""
        data = self.fetch_raw_data()
        if len(data) == 0:
            return []
        else:
            for datum in data:
                Extractor = diffbot.select_extractor(datum['type'])
                yield Extractor(datum)


    def fetch_raw_data(self, format=None, job_index=0):
        """format : json or csv"""
        if self._check_job_completed(job_index):
            return self._fetch_raw_data(
                api_type = "{}/data".format(self.api_type),
                query=self._compose_bot_data_query(format=format)
            )
        return []

    def _check_job_completed(self, job_index):
        """get searcher object"""
        status = self._fetch_job_status(job_index)
        # check whether "Job has completed and no repeat is scheduled" or not
        if status["status"] != 9:
            raise DiffbotJobStatusError(status["status"], status["message"])
        else:
            return True

    def _fetch_job_status(self, job_index):
        job = self._fetch_job(job_index)
        return job["jobStatus"]

    def _fetch_job(self, job_index):
        data = self._fetch_jobs()
        return data["jobs"][job_index]

    def _fetch_jobs(self):
        return self._fetch_raw_data(
            api_type=self.api_type,
            query={
                "name": self.job_name,
            },
        )

    def fetch_completed_searcher(self):
        """get searcher object"""
        if self._check_job_completed():
            return self._get_searcher()

    def _get_searcher(self):
        return diffbot.Searcher(self.token, self.job_name)

    def _compose_bot_data_query(self, format=None):
        """compose query of https://api.diffbot.com/v3/{}/data.format(self.api_type)
        see also section of Retrieving Crawlbot API data.
        """
        return {
            "name" : self.job_name,
            "format": format or "json",
        }

    @abstractmethod
    def start_job(self, target_url_list, apiurl, *, args=None, headers=None):
        pass

    def resume_job(self):
        self._control_job(action="resume")

    def pause_job(self):
        self._control_job(action="pause")

    def restart_job(self):
        self._control_job(action="restart")

    def delete_job(self):
        self._control_job(action="delete")

    def _control_job(self, action):
        """
        control crawl/bulk job depending on action in which we can assign pause/resume/restart/delete.
        """
        control_dic = {
            "pause": {
                "pause": 1,
            },
            "resume": {
                "pause": 0,
            },
            "restart": {
                "restart": 1,
            },
            "delete": {
                "delete": 1,
            }
        }

        return self._fetch_raw_data(
            api_type=self.api_type,
            query={
                "name": self.job_name,
                **control_dic[action]
            },
        )

    @abstractmethod
    def _compose_query(self, target_url_list, apiurl, *, args=None):
        pass


class Extractor():
    """base class of ooExtractor"""
    def __init__(self, data):
        self.data = data

    def get_raw_data(self):
        return self.data

    def get_resolved_url(self):
        return self.data.get("resolvedPageUrl")

    def get_page_url(self):
        return self.data["pageUrl"]

    def get_title(self):
        return self.data['title']


def drop_none_value(dic):
    return {key: value for key, value in dic.items() if value is not None}
