# -*- coding: utf-8 -*-
"""
科大讯飞问卷聚类分析（简化清晰版）
分组：
  A组：品牌认知与印象（Q5+Q6）     10题
  B组：产品创新与需求（Q7+Q8+Q9）  15题
  C组：营销策略优化（Q10~Q14）      25题
每组独立聚类，K由轮廓系数自动选取。
基础信息（Q1~Q4）用于事后描述聚类画像。
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体（适应Windows/Mac/Linux）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 备选字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置颜色
colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B2']

# ==================== 1. 数据准备（模拟生成，可替换为真实数据）====================
def generate_sample_data(n=300):
    """生成模拟问卷数据，结构与真实问卷一致"""
    np.random.seed(42)
    # 基础信息
    df_demo = pd.DataFrame({
        'Q1_gender': np.random.choice(['男','女'], n),
        'Q2_age': np.random.choice(['16岁以下','16-30岁','30-45岁','45岁以上'], n, p=[0.1,0.4,0.3,0.2]),
        'Q3_occupation': np.random.choice(['在校学生','普通职工','专业人员','公务员','个体/自由职业','企业管理层','已退休'], n, p=[0.2,0.25,0.15,0.1,0.15,0.1,0.05]),
        'Q4_income': np.random.choice(['2000元以下','2000-5000元','5000-10000元','10000-30000元','30000元以上'], n, p=[0.1,0.3,0.35,0.2,0.05])
    })

    # 生成量表数据（基于4个潜在因子，使题目间有相关性）
    F1 = np.random.normal(0, 1, n)  # 品牌认知
    F2 = np.random.normal(0, 1, n)  # 产品创新
    F3 = np.random.normal(0, 1, n)  # 营销策略
    F4 = np.random.normal(0, 1, n)  # 渠道偏好

    def gen_items(factor, n_items, noise=0.5):
        """生成n_items个相关题目，每个都是1-5分"""
        scores = factor.reshape(-1,1) * np.random.uniform(0.5, 0.9, (1, n_items)) + np.random.normal(0, noise, (n, n_items))
        # 归一化到1-5
        scores = (scores - scores.min(axis=0)) / (scores.max(axis=0) - scores.min(axis=0)) * 4 + 1
        return np.round(np.clip(scores, 1, 5)).astype(int)

    # 生成各题组（列名按原问卷设计）
    df_scale = pd.DataFrame({
        # A组：品牌认知与印象
        **{f'Q5_{i}_品牌印象': gen_items(F1, 1).flatten() for i in range(1,6)},
        **{f'Q6_{i}_产品了解': gen_items(F1, 1).flatten() for i in range(1,6)},

        # B组：产品创新与需求
        **{f'Q7_{i}_创新方向': gen_items(F2, 1).flatten() for i in range(1,6)},
        **{f'Q8_{i}_新品兴趣': gen_items(F2, 1).flatten() for i in range(1,6)},
        **{f'Q9_{i}_年轻评价': gen_items(F2, 1).flatten() for i in range(1,6)},

        # C组：营销策略优化
        **{f'Q10_{i}_吸引策略': gen_items(F3, 1).flatten() for i in range(1,6)},
        **{f'Q11_{i}_改进方向': gen_items(F3, 1).flatten() for i in range(1,6)},
        **{f'Q12_{i}_营销改进': gen_items(F3, 1).flatten() for i in range(1,6)},
        **{f'Q13_{i}_渠道偏好': gen_items(F4, 1).flatten() for i in range(1,6)},
        **{f'Q14_{i}_研发投入': gen_items(F3, 1).flatten() for i in range(1,6)},
    })

    return pd.concat([df_demo, df_scale], axis=1)

# 如果你有真实数据，用下面两行替换上面的生成代码：
# df = pd.read_excel('你的问卷数据.xlsx')
# （并确保列名与下面的分组匹配，否则需要调整分组列名）

df = generate_sample_data(300)
print(f"数据加载完成，样本量：{len(df)}")

# ==================== 2. 数据清洗（简单处理）====================
# 提取所有量表题列（以Q开头且不是Q1-Q4）
scale_cols = [c for c in df.columns if c.startswith('Q') and not c.startswith(('Q1_','Q2_','Q3_','Q4_'))]

# 检查缺失值
if df[scale_cols].isnull().sum().sum() > 0:
    # 删除缺失超过3题的样本，其余用均值填充
    row_missing = df[scale_cols].isnull().sum(axis=1)
    df = df[row_missing <= 3].copy()
    df[scale_cols] = df[scale_cols].fillna(df[scale_cols].mean())

# 删除全选同一选项的无效问卷
df['row_std'] = df[scale_cols].std(axis=1)
df = df[df['row_std'] > 0].copy()
df.drop('row_std', axis=1, inplace=True)
print(f"清洗后样本量：{len(df)}")

# ==================== 3. 定义分组 ====================
groups = {
    'A组·品牌认知': [c for c in df.columns if c.startswith(('Q5_','Q6_'))],
    'B组·产品创新': [c for c in df.columns if c.startswith(('Q7_','Q8_','Q9_'))],
    'C组·营销策略': [c for c in df.columns if c.startswith(('Q10_','Q11_','Q12_','Q13_','Q14_'))]
}

# ==================== 4. 对每组进行聚类分析 ====================
results = {}  # 保存每组的结果

for group_name, cols in groups.items():
    print(f"\n======= 正在分析：{group_name} =======")
    X = df[cols].values
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 尝试K=2到6，计算轮廓系数和惯性
    k_range = range(2, 7)
    inertias = []
    sil_scores = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X_scaled, labels))

    # 选择轮廓系数最大的K
    best_k = k_range[np.argmax(sil_scores)]
    print(f"  最优K = {best_k}，轮廓系数 = {max(sil_scores):.4f}")

    # 用最优K重新聚类
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    results[group_name] = {'labels': labels, 'best_k': best_k, 'cols': cols}

    # PCA降维用于可视化
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    var_ratio = pca.explained_variance_ratio_

    # ---------- 绘制该组的多图组合 ----------
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(f'{group_name} 聚类分析 (K={best_k})', fontsize=16, fontweight='bold')

    # 子图1：肘部法则
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.plot(k_range, inertias, 'o-', color='#4C72B0')
    ax1.axvline(best_k, color='red', linestyle='--')
    ax1.set_title('肘部法则')
    ax1.set_xlabel('K')
    ax1.set_ylabel('惯性')

    # 子图2：轮廓系数
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(k_range, sil_scores, 's-', color='#DD8452')
    ax2.axvline(best_k, color='red', linestyle='--')
    ax2.set_title('轮廓系数')
    ax2.set_xlabel('K')
    ax2.set_ylabel('轮廓系数')

    # 子图3：PCA散点图
    ax3 = fig.add_subplot(2, 3, 3)
    for i in range(best_k):
        mask = labels == i
        ax3.scatter(X_pca[mask, 0], X_pca[mask, 1], c=colors[i], label=f'簇{i+1}', alpha=0.6, edgecolors='white', linewidths=0.5)
    ax3.legend()
    ax3.set_title(f'PCA散点 (解释方差：{sum(var_ratio)*100:.1f}%)')
    ax3.set_xlabel(f'PC1 ({var_ratio[0]*100:.1f}%)')
    ax3.set_ylabel(f'PC2 ({var_ratio[1]*100:.1f}%)')

    # 子图4：簇大小
    ax4 = fig.add_subplot(2, 3, 4)
    counts = pd.Series(labels).value_counts().sort_index()
    bars = ax4.bar([f'簇{i+1}' for i in range(best_k)], counts.values, color=colors[:best_k])
    for bar, v in zip(bars, counts.values):
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(v), ha='center', fontsize=9)
    ax4.set_title('各簇样本量')
    ax4.set_ylabel('人数')

    # 子图5：各簇在各题目上的平均得分（热力图）
    ax5 = fig.add_subplot(2, 3, (5,6))
    df_tmp = df[cols].copy()
    df_tmp['cluster'] = labels
    cluster_means = df_tmp.groupby('cluster').mean()
    # 简化列名显示
    short_cols = [c.split('_', 2)[-1] for c in cols]
    cluster_means.columns = short_cols
    sns.heatmap(cluster_means, ax=ax5, cmap='RdYlGn', center=3, annot=True, fmt='.1f', linewidths=0.5, cbar_kws={'label': '平均分(1-5)'})
    ax5.set_title('各簇在各题目上的平均分')

    plt.tight_layout()
    plt.savefig(f'{group_name[:2]}_聚类结果.png', dpi=150)
    plt.show()
    print(f"  图表已保存为 {group_name[:2]}_聚类结果.png")

# ==================== 5. 聚类结果与基础信息交叉分析 ====================
# 将三组的聚类标签添加到原数据框中
for group_name, res in results.items():
    df[f'cluster_{group_name[:2]}'] = res['labels']

# 定义基础信息列
demo_cols = ['Q1_gender', 'Q2_age', 'Q3_occupation', 'Q4_income']
demo_labels = ['性别', '年龄', '职业', '收入']

# 绘制交叉分析图：每行是一组，每列是一个基础信息变量
fig, axes = plt.subplots(len(results), len(demo_cols), figsize=(16, 4*len(results)))
fig.suptitle('各组聚类结果与基础信息交叉分析', fontsize=16)

for row, (group_name, res) in enumerate(results.items()):
    cluster_col = f'cluster_{group_name[:2]}'
    for col, demo in enumerate(demo_cols):
        ax = axes[row, col]
        # 计算交叉频数
        cross = pd.crosstab(df[cluster_col], df[demo], normalize='index')
        cross.index = [f'簇{i+1}' for i in range(res['best_k'])]
        cross.plot(kind='bar', ax=ax, color=colors[:len(cross.columns)], edgecolor='white', width=0.7)
        ax.set_title(f'{group_name}\n{demo_labels[col]}分布')
        ax.set_xlabel('')
        ax.set_ylabel('比例')
        ax.legend(fontsize=8)
        ax.tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('聚类_人口画像.png', dpi=150)
plt.show()
print("\n人口画像图已保存为 聚类_人口画像.png")

# ==================== 6. 输出文字总结 ====================
print("\n\n========== 聚类特征总结 ==========")
for group_name, res in results.items():
    print(f"\n【{group_name}】最佳K = {res['best_k']}")
    df_tmp = df[res['cols']].copy()
    df_tmp['cluster'] = res['labels']
    for i in range(res['best_k']):
        size = (res['labels'] == i).sum()
        mean_score = df_tmp[df_tmp['cluster']==i][res['cols']].mean().mean()
        print(f"  簇{i+1}：{size}人，平均得分 {mean_score:.2f}")

print("\n分析完成！如需替换为真实数据，请修改 generate_sample_data 部分。")