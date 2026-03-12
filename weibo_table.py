import jieba
import re
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

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

words = jieba.cut(text)
stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
             '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
             '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '们',
             '啊', '吧', '呢', '哦', '嗯', '科大讯飞', '讯飞', '转发', '微博','科大','展开'}

words_filtered = [w for w in words if w not in stopwords and len(w) >= 2]
counter = Counter(words_filtered)
top15 = counter.most_common(15)

# 画表格
fig, ax = plt.subplots(figsize=(8, 9), facecolor='#F8F9FC')
ax.set_xlim(0, 10)
ax.set_ylim(0, 17)
ax.axis('off')

# 标题
ax.text(5, 16.2, '微博高频词 Top 15', fontsize=18, fontweight='bold',
        ha='center', va='center', color='#1A3F6F')
ax.text(5, 15.6, '基于微博社交媒体数据分析', fontsize=9,
        ha='center', va='center', color='#AAAAAA', style='italic')

# 表头
header_box = FancyBboxPatch((0.3, 14.6), 9.4, 0.7,
                             boxstyle="round,pad=0.05",
                             facecolor='#2E5F8A', edgecolor='none')
ax.add_patch(header_box)
ax.text(1.8, 14.95, '序号', fontsize=11, fontweight='bold',
        ha='center', va='center', color='white')
ax.text(4.5, 14.95, '关键词', fontsize=11, fontweight='bold',
        ha='center', va='center', color='white')
ax.text(7.8, 14.95, '出现频次', fontsize=11, fontweight='bold',
        ha='center', va='center', color='white')

# 颜色配置
row_colors = ['#F0F4FA', '#FFFFFF']
bar_color_high = '#2E5F8A'
bar_color_low = '#8FBDD3'
max_count = top15[0][1]

for i, (word, count) in enumerate(top15):
    y = 14.1 - i * 0.88
    
    # 行背景
    row_box = FancyBboxPatch((0.3, y - 0.35), 9.4, 0.75,
                              boxstyle="round,pad=0.02",
                              facecolor=row_colors[i % 2], edgecolor='none')
    ax.add_patch(row_box)
    
    # 序号圆圈
    color = '#2E5F8A' if i < 3 else '#8FBDD3'
    circle = plt.Circle((1.8, y + 0.02), 0.28, color=color)
    ax.add_patch(circle)
    ax.text(1.8, y + 0.02, str(i+1), fontsize=10, fontweight='bold',
            ha='center', va='center', color='white')
    
    # 关键词
    ax.text(4.5, y + 0.02, word, fontsize=12, ha='center', va='center',
            color='#1A3F6F', fontweight='bold' if i < 3 else 'normal')
    
    # 频次条形
    bar_width = (count / max_count) * 2.8
    bar_color = bar_color_high if i < 3 else bar_color_low
    bar = FancyBboxPatch((6.2, y - 0.15), bar_width, 0.35,
                          boxstyle="round,pad=0.02",
                          facecolor=bar_color, edgecolor='none', alpha=0.85)
    ax.add_patch(bar)
    ax.text(6.2 + bar_width + 0.15, y + 0.02, str(count),
            fontsize=9, va='center', color='#555555')

# 底部说明
ax.text(5, 0.3, f'数据来源：微博平台  |  共分析{len(open("weibo_raw.txt", encoding="utf-8").readlines())}条相关内容',
        fontsize=8, ha='center', va='center', color='#AAAAAA')

plt.tight_layout()
plt.savefig('weibo_table.png', dpi=200, bbox_inches='tight', facecolor='#F8F9FC')
plt.show()