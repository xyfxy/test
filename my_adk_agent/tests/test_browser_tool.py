import unittest
from unittest.mock import patch, MagicMock
# requests 需要在测试时可用，即使是被mock的
try:
    import requests
except ImportError:
    # 创建一个虚拟的requests和其异常类，以便在没有安装requests的环境中测试脚本本身能加载
    class RequestsMock:
        class exceptions:
            class RequestException(Exception): pass
            class HTTPError(Exception): pass
    requests = RequestsMock()

from my_adk_agent.tools.browser_tool import browse_website_and_extract_text

class TestBrowserTool(unittest.TestCase):

    @patch('my_adk_agent.tools.browser_tool.requests.get')
    def test_browse_website_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><head><title>Test Page</title></head><body><p>Hello World!</p><script>alert('test');</script></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        url = "http://example.com"
        result = browse_website_and_extract_text(url)

        mock_get.assert_called_once_with(url, headers=unittest.ANY, timeout=15)
        self.assertIn("Hello World!", result)
        self.assertNotIn("<script>", result)

    @patch('my_adk_agent.tools.browser_tool.requests.get')
    def test_browse_website_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test network error")
        url = "http://example.com"
        result = browse_website_and_extract_text(url)
        self.assertTrue(result.startswith(f"访问 URL {url} 时发生网络错误:"))
        self.assertIn("Test network error", result)

    @patch('my_adk_agent.tools.browser_tool.requests.get')
    def test_browse_website_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError("404 Client Error"))
        mock_get.return_value = mock_response
        url = "http://example.com/notfound"
        result = browse_website_and_extract_text(url)
        self.assertTrue(result.startswith(f"访问 URL {url} 时发生网络错误:"))
        self.assertIn("404 Client Error", result)

    @patch('my_adk_agent.tools.browser_tool.requests.get')
    def test_browse_website_empty_text(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><body><script>var x=1;</script><style>p{color:red;}</style></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        url = "http://example.com/empty"
        result = browse_website_and_extract_text(url)
        self.assertEqual(result, f"成功访问 URL {url}，但未能提取到有效文本内容。")

if __name__ == '__main__':
    unittest.main()
