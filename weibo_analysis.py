import jieba
import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 读取数据
with open('weibo_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 清洗：去除HTML实体、表情、标点、英文、数字
text = re.sub(r'&[a-zA-Z]+;', '', text)      # 去HTML实体如&amp;
text = re.sub(r'#[^#]+#', '', text)           # 去话题标签
text = re.sub(r'@\S+', '', text)              # 去@用户名
text = re.sub(r'http\S+', '', text)           # 去链接
text = re.sub(r'[a-zA-Z0-9]', '', text)       # 去英文数字
text = re.sub(r'[^\u4e00-\u9fff]', '', text)  # 只保留中文

# jieba分词
words = jieba.cut(text)

# 停用词
stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
             '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
             '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '们',
             '啊', '吧', '呢', '哦', '嗯', '科大讯飞', '讯飞', '转发', '微博','科大','展开'}

# 过滤停用词和单字
words_filtered = [w for w in words if w not in stopwords and len(w) >= 2]

# 词频统计
counter = Counter(words_filtered)
top15 = counter.most_common(15)

print("Top 15 高频词：")
for i, (word, count) in enumerate(top15, 1):
    print(f"{i:2}. {word}: {count}")