import unittest
import diffbot
from .data import bulk_url_lst

class DiffbotClientTests(unittest.TestCase):

    def test_article(self):
        user_name = "sample"
        fetcher = diffbot.SingleFetcher(
            user_name=user_name,
        )

        extractors = fetcher.fetch_article_extractors(
            target_url="http://google.co.jp/",
            args={"fields":"meta"},
        )

        for extractor in extractors:
            data = extractor.get_raw_data()

            self.assertIn("meta", data)

            self.assertEqual(type(extractor.get_title()), str)

    def test_article_with_generate_args(self):
        fetcher = diffbot.SingleFetcher(
            user_name = "sample",
        )

        # use generate_article_args
        extractors = fetcher.fetch_article_extractors(
            target_url="http://google.co.jp/",
            args=diffbot.SingleFetcher.generate_article_args(
                    fields="meta",
                )
        )

        for extractor in extractors:
            data = extractor.get_raw_data()

            self.assertIn("meta", data)

            self.assertEqual(type(extractor.get_title()), str)

    def test_bulk(self):
        import uuid
        job_operator = diffbot.BulkJobOperator(
            user_name="sample",
            # bot_name should be under & equal to 30 chars
            bot_name="test_bulk_{}".format(uuid.uuid4())[:30],
        )
        # for new bot name
        response = job_operator.start_job(
            target_url_list=bulk_url_lst, # for STARTUP plan, you should at least 50 urls.
            apiurl=job_operator.generate_apiurl(
                "article",
                args=diffbot.SingleFetcher.generate_article_args(
                    fields="meta",
                )
            )
        )

        self.assertIn("jobs", response)
        self.assertIn("response", response)


if __name__ == "__main__":
    unittest.main()
