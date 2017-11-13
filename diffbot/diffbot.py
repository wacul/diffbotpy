from .meta import Client, JobOperator, drop_none_value, Extractor

class SingleFetcher(Client):
    """wrapper of analyze/article/discussion/image/product/video API"""
    def __init__(self, token):
        super().__init__(token)

    def _fetch_extractors(self, api_type, target_url, args=None, headers=None):
        data = self.fetch_raw_data(
            api_type=api_type,
            target_url=target_url,
            args = args,
            headers = headers,
        )
        Extractor = select_extractor(api_type)

        res = []
        for i in range(len(data["objects"])):
            res.append(Extractor(data["objects"][i]))
        return res

    def fetch_article_extractors(self, target_url, *, args=None, headers=None):
        """using analyze API, get data
        To customize headers, use SingleFetcher.get_http_headers(**kwargs)
        """
        args = args or {}
        headers = headers or {}

        return self._fetch_extractors(
            api_type="article",
            target_url=target_url,
            args = args,
            headers = headers
        )

    def fetch_analyze_extractors(self, target_url, *, args=None, headers=None):
        """using article API, get article data
        see also https://www.diffbot.com/dev/docs/article/
        """

        data = self.fetch_raw_data(
            api_type="analyze",
            target_url=target_url,
            args=args,
            headers=headers
        )
        Extractor = select_extractor("analyze")
        return [Extractor(data)]


    def fetch_discussion_extractors(self, target_url, *, args=None, headers=None):
        """using discussion API, get data
        see also https://www.diffbot.com/dev/docs/discussion/
        """

        return self._fetch_extractors(
            api_type="discussion",
            target_url=target_url,
            args=args,
            headers=headers
        )

    def fetch_image_extractors(self, target_url, *, args=None, headers=None):
        """using image API, get data
        see also https://www.diffbot.com/dev/docs/image/
        """
        return self._fetch_extractors(
            api_type="image",
            target_url=target_url,
            args=args,
            headers=headers
        )

    def fetch_product_extractors(self, target_url, *, args=None, headers=None):
        """using product API, get data
        see also https://www.diffbot.com/dev/docs/product/
        """
        return self._fetch_extractors(
            api_type="product",
            target_url=target_url,
            args=args,
            headers=headers
        )

    def fetch_video_extractors(self, target_url, *, args=None, headers=None):
        """using video API, get data
        see also https://www.diffbot.com/dev/docs/video/
        """
        return self._fetch_extractors(
            api_type="video",
            target_url=target_url,
            args=args,
            headers=headers
        )


    def fetch_raw_data(self, api_type, target_url, *, args=None, headers=None):
        """fetch raw data in ${api_type} API
        To fetch raw data, use this method.
        """
        args = args or {}
        headers = headers or {}
        return self._fetch_raw_data(
            api_type=api_type,
            query=self._compose_query(target_url, args=args),
            headers=headers,
        )

    @staticmethod
    def generate_analyze_args(*, mode=None, fallback=None, fields=None, discussion=None, timeout=None, callback=None):
        analyze_optional_dict = {
            "mode" : mode,
            "fallback" : fallback,
            "discussion" : discussion,
            **SingleFetcher._generate_args(
                fields=fields,
                timeout=timeout,
                callback=callback,
            )
        }
        return drop_none_value(analyze_optional_dict)

    @staticmethod
    def generate_article_args(*, fields=None, paging=None, max_tags=None, tag_confidence=None, discussion=None,
                                       timeout=None, callback=None):
        return drop_none_value({
            "paging" : paging,
            "maxTags" : max_tags,
            "tagConfidence" : tag_confidence,
            "discussion" : discussion,
            **SingleFetcher._generate_args(
                fields = fields,
                timeout = timeout,
                callback = callback,
            )
        })

    @staticmethod
    def generate_discussion_args(*, fields=None, timeout=None, callback=None, max_pages=None):
        return drop_none_value({
            "maxPages" : max_pages,
            **SingleFetcher._generate_args(
                fields = fields,
                timeout = timeout,
                callback = callback,
            )
        })


    @staticmethod
    def generate_image_args(*, fields=None, timeout=None, callback=None):
        return SingleFetcher._generate_args(
                fields = fields,
                timeout = timeout,
                callback = callback,
        )

    @staticmethod
    def generate_product_args(*, fields=None, discussion=None, timeout=None, callback=None):
        return drop_none_value({
            "discussion" : discussion,
            **SingleFetcher._generate_args(
                    fields = fields,
                    timeout = timeout,
                    callback = callback,
            )
        })


    @staticmethod
    def generate_video_args(*, fields=None, timeout=None, callback=None):
        return SingleFetcher._generate_args(
                fields = fields,
                timeout = timeout,
                callback = callback,
        )

    def _compose_query(self, target_url, *, args=None):
        """compose query of url"""
        params = {
            "url": target_url
        }
        params.update(args)

        return params

    @staticmethod
    def _generate_args(*, fields=None, timeout=None, callback=None):
        analyze_dict = {
            "fields" : fields,
            "timeout" : timeout,
            "callback" : callback,
        }

        return drop_none_value(analyze_dict)


class BulkJobOperator(JobOperator):
    """use bulk API then search API.
    see also bulk API document, https://www.diffbot.com/dev/docs/bulk/api.jsp
    # Set your Content-Type header to application/x-www-form-urlencoded
    """

    def __init__(self, token, job_name):
        super().__init__(token, job_name, "bulk")

    def start_job(self, target_url_list, apiurl, *, args=None, headers=None):
        args = args or {}
        headers = headers or {}

        content_type = {"Content-Type" : "application/x-www-form-urlencoded"}

        return self._post_raw_data(
            api_type=self.api_type,
            payload=self._compose_query(target_url_list, apiurl,
                                        args=args
            ),
            headers={**headers, **content_type},
        )

    # abstruct API
    def _compose_query(self, target_url_list, apiurl, *, args=None):
        """along with Bulk API, override _compose_bot_query"""
        args = args or {}
        params = {
            "name": self.job_name,
            "urls": " ".join(target_url_list),  # Space-delimited list of URLs to process.
            "apiUrl": apiurl,
        }

        params.update(args)

        return params

    @staticmethod
    def generate_args(*, custom_headers=None, notify_email=None, notify_webhook=None, repeat=None,
                                     max_rounds=None, page_process_pattern=None):
        return JobOperator._generate_args(
            custom_headers = custom_headers,
            notify_email = notify_email,
            notify_webhook = notify_webhook,
            repeat = repeat,
            max_rounds = max_rounds,
            page_process_pattern = page_process_pattern,
        )


class CrawlJobOperator(JobOperator):
    """use crawling API
    see also crawling API document, https://www.diffbot.com/dev/docs/crawl/.
    """
    def __init__(self, token, job_name):
        super().__init__(
            token=token,
            job_name=job_name,
            api_type="crawl",
        )

    def start_job(self, target_url_list, apiurl, *, args=None, headers=None):
        args = args or {}
        headers = headers or {}

        return self._fetch_raw_data(
            api_type=self.api_type,
            query=self._compose_query(target_url_list, apiurl,
                args=args
            ),
            headers=headers,
        )

    # abstruct API
    def _compose_query(self, target_url_list, apiurl, *, args=None):
        """along with Crawling API, override _compose_bot_query"""
        args = args or {}
        params = {
            "seeds": " ".join(target_url_list),
            "name": self.job_name,
            "apiUrl": apiurl,
        }

        params.update(args)

        return params

    @staticmethod
    def _generate_args(*, url_crawl_pattern=None, url_crawl_reg_ex=None, url_process_pattern=None,
                                      url_process_reg_ex=None, page_process_pattern=None,
                                      custom_headers=None, obey_robots=None, restrict_domain=None, use_proxies=None,
                                      max_hops= None, max_to_crawl=None, max_to_process=None, notify_email=None, notify_webhook=None,
                                      crawl_delay=None, repeat=None, only_process_if_new=None, max_rounds=None):

        return drop_none_value({
            "urlCrawlPattern" : url_crawl_pattern,
            "urlCrawlRegEx" : url_crawl_reg_ex,
            "urlProcessPattern" : url_process_pattern,
            "urlProcessRegEx" : url_process_reg_ex,
            "obeyRobots" : obey_robots,
            "restrictDomain" : restrict_domain,
            "useProxies" : use_proxies,
            "maxHops" : max_hops,
            "maxToCrawl" : max_to_crawl,
            "maxToProcess" : max_to_process,
            "crawlDelay" : crawl_delay,
            "onlyProcessIfNew" : only_process_if_new,
            **JobOperator._generate_args(
                custom_headers=custom_headers,
                notify_webhook=notify_webhook,
                notify_email=notify_email,
                repeat=repeat,
                max_rounds=max_rounds,
                page_process_pattern=page_process_pattern
            )
        })

class Searcher(Client):
    """using search API"""
    def __init__(self, token, job_name):
        super().__init__(token)
        self.job_name = job_name

    def fetch_search_extractors(self, *, query, args=None):
        args = args or {}
        data = self.fetch_raw_data(
            query,
            args=args
        )
        exts = []

        for i in range(len(data["objects"])):
            Extractor = select_extractor(data["objects"][i]["type"])
            exts.append(Extractor(data["objects"][i]))
        return exts

    def fetch_raw_data(self, query, *, args=None):
        """using search API, search data with query
        For more information about kwargs,
        see also search API document, https://www.diffbot.com/dev/docs/search/
        """
        args = args or {}
        return self._fetch_raw_data(
            api_type="search",
            query=self._compose_query(
                query=query,
                args=args
            )
        )

    @staticmethod
    def generate_args(*, num=None, start=None):
        return drop_none_value({
            "num" : num,
            "start" : start,
        })

    def _compose_query(self, query, *, args=None):
        params = {
            "col": self.job_name,
            "query": query,
        }
        params.update(args)

        return params



def select_extractor(api_type):
    """select Extractor class corresponding api_type"""
    dic = {
        "article": ArticleExtractor,
        "analyze": AnalyzeExtractor,
        "discussion": DiscussionExtractor,
        "video": VideoExtractor,
        "image": ImageExtractor,
        "product": ProductExtractor,
    }
    return dic[api_type]


class DiscussionExtractor(Extractor):
    """support Discussion API"""
    def __init__(self, data):
        super().__init__(data)

    def get_posts(self):
        return self.data["posts"]


class AnalyzeExtractor(Extractor):
    """support Analyze API"""
    def __init__(self, data):
        super().__init__(data)


class ArticleExtractor(Extractor):
    """support Article API"""
    def __init__(self, data):
        super().__init__(data)

    def get_html(self, plain=False):
        if plain == False:
            return self.data['html']
        else:
            return self.data['text']

    def get_site_name(self):
        return self.data["siteName"]

    def get_language(self):
        return self.data['humanLanguage']


class ImageExtractor(Extractor):
    """support Image API"""
    def __init__(self, data):
        super().__init__(data)


class ProductExtractor(Extractor):
    """support Product API"""
    def __init__(self, data):
        super().__init__(data)


class VideoExtractor(Extractor):
    """support Video API"""
    def __init__(self, data):
        super().__init__(data)

