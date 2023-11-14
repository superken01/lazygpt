import requests
import tiktoken
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from html2text import html2text
from playwright.sync_api import sync_playwright

ua = UserAgent()


# url = "https://www.coindesk.com/markets/2023/11/13/grayscale-discount-continues-to-narrow-as-spot-bitcoin-ether-etf-euphoria-works-through-markets/"

url = "https://www.mobile01.com/topicdetail.php?f=754&t=6873205"

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     # page.goto(url, wait_until="domcontentloaded")
#     try:
#         page.goto(url, timeout=3000)
#     except:
#         pass
#     elements = page.locator("*", has_text="*").all()
#     print(len(elements))
#     # i = 1
#     for element in elements:
#         bb = element.bounding_box()
#         text = element.text_content()
#         print(bb, len(text), element.name, text[0:100])
#     print(i)
#     if bb:
#         try:
#             print(bb, len(element.inner_text()))
#         except:
#             print(bb)
#         i += 1
# print(element.inner_text())
# print(e)
# tags = page.query_selector_all("*")
# page.wait_for_selector("*", 1000)
# for tag in tags:
#     print(tag.inner_text())
# page.wait_for_timeout(1000)
# raw_html = page.content()
# print(raw_html)
# browser.close()

response = requests.get(url, headers={"User-Agent": ua.random})
raw_html = response.text

soup = BeautifulSoup(raw_html, "html.parser")

# head = soup.find("head")
# head.decompose()
# for script_tag in soup.find_all("script"):
#     script_tag.decompose()

# for tag in soup.find_all(True):
#     tag.attrs = {}

html = soup.prettify()
with open("test1.html", "w") as f:
    f.write(html)

for tag in soup.find_all(True):
    if tag.name in ["header", "footer"]:
        tag.decompose()
    elif len(tag.get_text(strip=True)) == 0:
        tag.decompose()


html = soup.prettify()
with open("test2.html", "w") as f:
    f.write(html)

md = html2text(html, bodywidth=1000000)
with open("test.md", "w") as f:
    f.write(md)

encoding = tiktoken.get_encoding("cl100k_base")
num_tokens = len(encoding.encode(md))
print(num_tokens)


# # 移除所有的 <style> 標籤
# for style_tag in soup.find_all("style"):
#     style_tag.decompose()

# # 印出處理後的 HTML
# print(soup.prettify())
