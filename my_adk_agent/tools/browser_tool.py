import requests
from bs4 import BeautifulSoup
from google.adk.tools import FunctionTool

def browse_website_and_extract_text(url: str) -> str:
    """
    访问指定的 URL，获取其 HTML 内容，并提取纯文本。
    如果请求失败或无法解析内容，将返回错误信息。

    :param url: 需要访问的网站 URL。
    :return: 提取的纯文本内容，或错误信息。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # 如果请求失败 (状态码 4xx 或 5xx), 则抛出 HTTPError

        soup = BeautifulSoup(response.content, 'html.parser')

        # 移除脚本和样式元素
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # 获取文本
        text = soup.get_text()

        # 分割行并移除多余的空白
        lines = (line.strip() for line in text.splitlines())
        # 多空行合并为单空行
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk) # 注意这里从
改为 \n 以适应子任务的字符串处理

        if not text:
            return f"成功访问 URL {url}，但未能提取到有效文本内容。"

        max_length = 2000
        if len(text) > max_length:
            return text[:max_length] + "\n\n[内容过长，已截断]" # 注意这里从
改为 \n

        return text

    except requests.exceptions.RequestException as e:
        return f"访问 URL {url} 时发生网络错误: {e}"
    except Exception as e:
        return f"处理 URL {url} 时发生未知错误: {e}"

browse_tool = FunctionTool(
    func=browse_website_and_extract_text,
    name="BrowseWebsite",
    description="根据提供的URL访问一个网站并提取其主要的文本内容。用于获取网页信息。"
)

if __name__ == '__main__':
    test_url_success = "https://adk.wiki/"
    test_url_nonexistent = "http://thissitedoesnotexist12345.org"

    print(f"测试成功案例 ({test_url_success}):")
    content_success = browse_website_and_extract_text(test_url_success)
    print(content_success)
    print("\n" + "="*50 + "\n")

    print(f"测试不存在的域名 ({test_url_nonexistent}):")
    content_nonexistent = browse_website_and_extract_text(test_url_nonexistent)
    print(content_nonexistent)
