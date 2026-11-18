
import requests
from bs4 import BeautifulSoup

# 크롤링할 국토교통부 보도자료 주소
url = "https://www.molit.go.kr/USR/NEWS/m_71/dtl.jsp?lcmspage=1&id=95092576"

# 웹페이지 HTML 가져오기
response = requests.get(url, timeout=15)
response.raise_for_status()
response.encoding = response.apparent_encoding

# HTML 분석하기
soup = BeautifulSoup(response.text, "html.parser")

# 보도자료 제목 찾기
title_element = soup.select_one("h4")

if title_element is not None:
    title = title_element.get_text(strip=True)
    print("보도자료 제목:", title)
else:
    print("보도자료 제목을 찾지 못했습니다.")

# 담당부서와 등록일 추출하기
info_items = soup.select("ul.bd_view_ul_info li")

for item in info_items:
    label = item.select_one("strong")
    value = item.select_one("span")

    if label is not None and value is not None:
        print(label.get_text(strip=True) + ":", value.get_text(strip=True))

from urllib.parse import urljoin

# 첨부파일 다운로드 링크 찾기
file_links = soup.select("li.file a[href]")

print("\n첨부파일 다운로드 링크:")

for link in file_links:
    file_name = link.get_text(" ", strip=True)
    download_url = urljoin(url, link.get("href"))

    print("파일명:", file_name)
    print("다운로드 URL:", download_url)
    print()

import pandas as pd

# 보도자료 기본 정보
department = ""
published_at = ""

for item in info_items:
    label = item.select_one("strong")
    value = item.select_one("span")

    if label is None or value is None:
        continue

    label_text = label.get_text(strip=True)
    value_text = value.get_text(strip=True)

    if label_text == "담당부서":
        department = value_text
    elif label_text == "등록일":
        published_at = value_text

# PDF 다운로드 주소 찾기
pdf_url = ""

for link in file_links:
    href = link.get("href", "")
    file_name = link.get_text(" ", strip=True)

    if ".pdf" in file_name.lower() and "바로보기" not in file_name:
        pdf_url = urljoin(url, href)
        break

# 수집 데이터 정리
data = {
    "제목": [title],
    "담당부서": [department],
    "등록일": [published_at],
    "원본URL": [url],
    "PDF_URL": [pdf_url]
}

df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv("trafficnews_crawling.csv", index=False, encoding="utf-8-sig")

print("\nCSV 저장 완료!")
print(df.to_string(index=False))
