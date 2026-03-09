from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 模拟问卷关键词及词频（可以替换成真实数据）
word_freq = {
    "AI":60,
    "语音识别":55,
    "智能办公":50,
    "性价比":45,
    "年轻化":42,
    "设计感":40,
    "智能家居":38,
    "教育科技":36,
    "车载助手":30,
    "个性化":28,
    "社交媒体":26,
    "KOL合作":24,
    "品牌形象":22,
    "用户体验":20,
    "产品创新":18,
    "环保材料":16,
    "便携设备":15,
    "线上电商":14,
    "线下体验":13,
    "广告创意":12
}

# 中文字体路径（Windows一般用这个）
font_path = "simhei.ttf"

# 生成词云
wc = WordCloud(
    font_path=font_path,
    width=1000,
    height=600,
    background_color="white"
)

wc.generate_from_frequencies(word_freq)

# 显示词云
plt.figure(figsize=(10,6))
plt.imshow(wc)
plt.axis("off")
plt.show()

# 保存图片
wc.to_file("问卷词云.png")