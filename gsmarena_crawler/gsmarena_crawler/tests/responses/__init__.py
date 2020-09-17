import os

from scrapy.http import HtmlResponse, Request


def fake_response_from_file(file_name, url=None, meta=None):
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url, meta=meta)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    with open(file_path, 'rb') as f:
        file_content = f.read()

    response = HtmlResponse(url=url,
                            request=request,
                            body=file_content, encoding='utf-8')

    return response
