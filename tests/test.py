import unittest
import diffbot


class DiffbotClientTests(unittest.TestCase):

    def test_article(self):
        user_name = "sample"
        fetcher = diffbot.SingleFetcher(
            user_name=user_name,
        )

        extractors = fetcher.fetch_article_extractors(
            target_url="http://google.co.jp/",
            args={"fields": "meta"},
        )

        for extractor in extractors:
            data = extractor.get_raw_data()

            self.assertIn("meta", data)

            self.assertEqual(type(extractor.get_title()), str)

    def test_article_with_generate_args(self):
        fetcher = diffbot.SingleFetcher(
            user_name="sample",
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


if __name__ == "__main__":
    unittest.main()
