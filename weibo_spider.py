import requests
import json
import jieba
import re
from collections import Counter

# 你的cookie
COOKIE = "XSRF-TOKEN=VOGC-xbhgxH9hqyRwtnGcue2; SCF=Agk8ew4-vqmrrCIc--nImgtdc7jBC-Q6iNd4AccQRRosd8GeuEwgp_0Xm-f2wd9XbvzD_zAo_aGRuE_RTGOWbNo.; SUB=_2A25EttWQDeRhGeFL7VAR-SjIwzWIHXVnyldYrDV8PUNbmtANLU7jkW9NfcpZqBnIChddJyVLaqGVWmm7DmZhxD-1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5UHUeOS.dI0D6B1VY.9g3I5JpX5KzhUgL.FoMfSoz71KqX1h.2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNSKqEeh.cShn4; ALF=02_1775907520; WBPSESS=4lEIDfaqTPvtTnsAyxglp2Wx3OQt0-vPIN601bitPUd1baZzZwHiWN1wOgnC-ALwEWI7iyGrPMdtHFiH2bBFzqHi9PsyYukjUCkmeQQbNLYRFaP2VL3Bjp6oVpJB398PSpEqAk0A1W-J_bxyK-gS3w==; _s_tentry=weibo.com; Apache=1741315275099.0957.1773315575870; SINAGLOBAL=1741315275099.0957.1773315575870; ULV=1773315575871:1:1:1:1741315275099.0957.1773315575870:"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Cookie': COOKIE,
    'Referer': 'https://s.weibo.com/',
    'X-Requested-With': 'XMLHttpRequest',
}

def get_weibo_posts(keyword, pages=10):
    texts = []
    for page in range(1, pages+1):
        url = f'https://s.weibo.com/weibo?q={keyword}&page={page}'
        resp = requests.get(url, headers=headers)
        # 用正则提取帖子文本
        contents = re.findall(r'<p class="txt"[^>]*>(.*?)</p>', resp.text, re.DOTALL)
        for c in contents:
            # 去除HTML标签
            clean = re.sub(r'<[^>]+>', '', c).strip()
            if clean:
                texts.append(clean)
        print(f'第{page}页，已抓取{len(texts)}条')
    return texts

# 抓取50页
posts = get_weibo_posts('科大讯飞', pages=50)
print(f'\n共抓取 {len(posts)} 条微博')

# 保存原始数据
with open('weibo_raw.txt', 'w', encoding='utf-8') as f:
    for p in posts:
        f.write(p + '\n')

print('已保存到 weibo_raw.txt')