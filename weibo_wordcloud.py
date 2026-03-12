import jieba
import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image, ImageDraw
import random

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
with open('weibo_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 清洗
text = re.sub(r'&[a-zA-Z]+;', '', text)
text = re.sub(r'#[^#]+#', '', text)
text = re.sub(r'@\S+', '', text)
text = re.sub(r'http\S+', '', text)
text = re.sub(r'[a-zA-Z0-9]', '', text)
text = re.sub(r'[^\u4e00-\u9fff]', '', text)

# 分词
words = jieba.cut(text)

# 停用词
stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
             '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
             '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '们',
             '啊', '吧', '呢', '哦', '嗯', '科大讯飞', '讯飞', '转发', '微博','科大','展开'}

words_filtered = [w for w in words if w not in stopwords and len(w) >= 2]
counter = Counter(words_filtered)
word_freq = dict(counter.most_common(80))

# 云朵mask
def create_cloud_mask(width=900, height=680):
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    circles = [
        (220, 380, 170), (380, 310, 210), (540, 330, 180),
        (680, 375, 150), (140, 445, 125), (730, 445, 115),
        (300, 445, 140), (460, 435, 148), (600, 438, 128),
    ]
    for x, y, r in circles:
        draw.ellipse([x-r, y-r, x+r, y+r], fill='black')
    return np.array(img)

mask = create_cloud_mask()

# nature3配色
colors = ['#0d1f4e', '#28437d', '#4675b0', '#6892c5', '#a6badf',
          '#eab7ca', '#d2798c', '#a03060', '#6b1040']

def nature_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return random.choice(colors)

wc = WordCloud(
    font_path='C:/Windows/Fonts/msyh.ttc',
    mask=mask,
    background_color='white',
    max_words=80,
    color_func=nature_color_func,
    prefer_horizontal=0.85,
    scale=3,
    margin=2,
)

wc.generate_from_frequencies(word_freq)

plt.figure(figsize=(13, 10), facecolor='white')
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('weibo_wordcloud.png', dpi=200, bbox_inches='tight')
plt.show()