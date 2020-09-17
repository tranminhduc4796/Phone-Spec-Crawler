import unittest
from gsmarena_crawler.spiders.phone_spider import PhonesSpider
from gsmarena_crawler.tests.responses import fake_response_from_file


class PhoneSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = PhonesSpider()

    def _test_item_results(self, results, expectation):
        self.assertEqual(results, expectation)

    def test_parse(self):
        results = self.spider.parse(fake_response_from_file('phone/ipad.html', meta={'device_name': 'iPad Air 2020'}))
        expectation = {
            'name': 'iPad Air 2020',
            'size': 10.9,
            'resolution': {
                'width': 1640,
                'height': 2360
            }
        }
        self._test_item_results(results, expectation)
