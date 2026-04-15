#!/usr/bin/env python3
"""
ADADD 数据生成器 V2 - 生成 220 条广告行业全量资讯数据
覆盖 2016-2026 十年，7大数据源，30个分类
"""

import json, os, sys, random, re
from datetime import datetime, timedelta

# ============================================================
# 基础数据定义
# ============================================================

SOURCES = ['weibo', 'zhihu', 'wechat', 'github', 'tech-media', 'industry-media', '36kr']

CATEGORIES = [
    'AI与机器学习', '程序化广告', '创意技术', '数据隐私', '品牌营销',
    '社交媒体', '视频广告', '电商广告', '效果营销', '内容营销',
    'MarTech', '广告技术', '用户增长', '移动广告', 'OTT/CTV广告',
    '搜索广告', 'KOL营销', '游戏广告', '出海营销', '合规监管',
    '元宇宙/Web3', 'AIGC', 'CDP', 'DMP', '广告投放平台', '数据分析',
    '消费者洞察', '媒介策略', '品牌升级', '行业趋势'
]

IMPACT_LEVELS = ['high', 'medium', 'low']

YEAR_WEIGHTS = {
    2026: 40, 2025: 35, 2024: 30, 2023: 25,
    2022: 18, 2021: 15, 2020: 12, 2019: 10,
    2018: 8, 2017: 5, 2016: 5,
}

YEAR_KEYWORDS = {
    2026: ['AIGC智能体', '多模态大模型', 'AI原生营销', '视频生成模型', '数字人直播', 'AI搜索广告'],
    2025: ['DeepSeek', 'Sora视频模型', 'GPT-5', 'Claude AI', 'AI Agent', '具身智能', '端侧大模型'],
    2024: ['ChatGPT生态', '文心一言', '通义千问', 'Midjourney', 'Stable Diffusion', 'AIGC落地', 'AI绘画'],
    2023: ['ChatGPT爆发', '大语言模型', 'AIGC元年', 'Prompt工程', 'AI写作工具', 'OpenAI'],
    2022: ['Web3营销', '元宇宙品牌', 'NFT营销', '虚拟偶像', '隐私计算', '全域经营'],
    2021: ['私域运营', 'CDP建设', '品牌自播', '短视频电商', '兴趣电商', '抖音电商'],
    2020: ['疫情下的营销转型', '线上化加速', '直播带货爆发', '小程序生态', '企业微信', '数字化转型'],
    2019: ['KOC崛起', '下沉市场红利', '私域流量', '抖音商业化', '信息流广告成熟', 'MarTech落地'],
    2018: ['抖音现象级增长', '社交裂变', '小程序元年', '信息流广告崛起', 'DMP建设', '品牌年轻化'],
    2017: ['短视频元年', '知识付费', '内容创业', 'IP营销', '新零售概念', '程序化广告起步'],
    2016: ['双微一抖格局初现', 'H5营销', '原生广告兴起', 'DSP发展', '移动端超越PC', '网红经济萌芽'],
}

PREMIUM_URLS = {
    ('github', 'ad-tech'): 'https://github.com/ruimo/adbooster',
    ('github', 'ai'): 'https://github.com/openai/whisper',
    ('github', 'mar'): 'https://github.com/facebookresearch/fairo',
    ('github', 'data'): 'https://github.com/apache/superset',
    ('github', 'programmatic'): 'https://github.com/prebid/Prebid.js',
}

SOURCE_SEARCH_URLS = {
    'weibo': 'https://s.weibo.com/weibo?q={}',
    'zhihu': 'https://www.zhihu.com/search?type=content&q={}',
    'wechat': 'https://weixin.sogou.com/weixin?type=2&query={}',
    'github': 'https://github.com/search?q={}&type=repositories',
    'tech-media': 'https://juejin.cn/search?q={}',
    'industry-media': 'https://www.google.com/search?q={}+广告+营销',
    '36kr': 'https://36kr.com/search/articles/{}',
}

# 摘要模板（每个只含一个 {} 占位符）
SUMMARY_TEMPLATES = [
    '深入分析{}在广告行业的应用现状，探讨对企业营销策略的深远影响。',
    '{}正在重塑整个广告产业链，从创意生产到效果投放都在发生革命性变化。',
    '行业专家指出{}将成为未来三年广告技术发展的核心驱动力。',
    '据最新数据显示，{}相关市场规模已突破千亿级别，年增长率超过50%。',
    '本案例详细拆解头部品牌如何利用{}实现营销效率大幅提升的实践路径。',
    '随着技术的快速迭代，{}正从概念验证阶段走向规模化商业落地。',
    '多家国际广告集团已宣布将{}纳入核心战略，预计带动新一轮行业洗牌。',
    '从消费者行为变化看，{}不仅改变了触达方式，更重新定义了品牌互动模式。',
]

# 正文模板（安全格式化）
BODY_TEMPLATE = '''## 背景

近年来，{topic}已经成为广告行业最受关注的领域之一。根据行业研究机构的报告显示，该领域的市场规模在过去三年内实现了年均50%以上的高速增长。

## 核心洞察

### 1. 技术驱动变革
{topic}技术的成熟正在从根本上改变广告行业的运作方式。传统的投放模式正在被智能化、自动化的解决方案所取代。头部企业已经开始大规模部署相关技术，并在实际应用中取得了显著成效。

### 2. 市场格局重塑
随着{topic}的普及，行业竞争格局也在发生深刻变化。新进入者凭借技术创新迅速抢占市场份额，传统玩家则面临转型压力。预计未来两年内，行业将经历一轮深度整合。

### 3. 实践案例分享
多个领先品牌已经在{topic}领域进行了积极探索：
- 某国际快消品牌通过相关技术将获客成本降低40%
- 国内电商平台利用智能化方案实现ROI提升200%
- 媒体公司借助新技术实现内容生产效率翻倍

## 行业展望

专家普遍认为，{topic}将在未来三到五年内成为行业标准配置。对于广告从业者而言，现在正是布局和积累经验的关键窗口期。建议关注以下方向：技术能力建设、数据资产积累、跨团队协作机制优化等。

## 结语

{topic}代表了广告行业未来的发展方向。无论是品牌方、代理商还是媒体平台，都需要积极拥抱这一趋势，才能在激烈的市场竞争中保持领先地位。'''

TITLE_PREFIXES = {
    'AI与机器学习': ['深度解析：', '重磅发布：', '行业观察：', '技术前沿：', '独家报道：'],
    'AIGC': ['AIGC革命：', 'AI创作新时代：', '生成式AI：', 'AIGC实战：'],
    '程序化广告': ['程序化购买', 'DSP/SSP', '实时竞价RTB', '广告交易平台'],
    '创意技术': ['创意自动化', '动态创意优化DCO', '沉浸式体验', '交互式广告'],
    '数据隐私': ['隐私计算', '数据合规', 'Cookie替代方案', '个人信息保护法'],
    '品牌营销': ['品牌数字化', '品牌升级战略', 'DTC模式', '品牌年轻化'],
    '社交媒体': ['社交裂变', '私域运营', '社群营销', 'KOL/KOC矩阵'],
    '视频广告': ['短视频营销', '直播带货', '视频号运营', '内容种草'],
    '电商广告': ['兴趣电商', '货架电商', '品效协同', '全链路营销'],
    '效果营销': ['ROAS提升', '转化率优化', '归因分析', '增量测量'],
    'CDP/DMP': ['客户数据平台', '数据中台', '用户画像', '精准触达'],
}


def safe_format(template: str, value: str) -> str:
    """安全的模板格式化，处理占位符数量不匹配的问题"""
    count = template.count('{}')
    if count == 0:
        return template
    elif count == 1:
        return template.format(value)
    else:
        # 多个占位符时用同一值填充
        return template.format(*(value for _ in range(count)))


def generate_title(year: int, category: str, keywords: list) -> str:
    """生成新闻标题"""
    kw = random.choice(keywords)
    
    # 根据年份调整标题风格
    if year >= 2024:
        styles = [
            f'{kw}引爆广告圈！2024-2026年度最强趋势报告',
            f'告别传统模式：{kw}如何重新定义{category}？',
            f'{category}新篇章：从{kw}看未来三年的行业变局',
            f'深度｜{kw}落地实践：10家头部品牌的真实数据',
            f'{kw}浪潮来袭：广告人必须掌握的核心能力',
            f'202{year % 100}年{category}白皮书：{kw}占据C位',
        ]
    elif year >= 2020:
        styles = [
            f'热点追踪：{kw}在{category}领域的最新进展',
            f'{category}观察：{kw}带来哪些新机会？',
            f'从业者必读：全面了解{kw}对广告行业的影响',
            f'{kw}应用指南：从入门到精通的完整路径',
            f'案例复盘：某品牌如何通过{kw}实现突破',
        ]
    else:
        styles = [
            f'{kw}兴起：{category}的新风向标',
            f'行业热议话题：{kw}的前景与应用',
            f'深度好文：{kw}背后的商业逻辑',
            f'从0到1理解{kw}及其在{category}中的作用',
        ]
    
    return random.choice(styles)


def get_source_search_url(source: str, title: str) -> str:
    """获取来源搜索URL"""
    template = SOURCE_SEARCH_URLS.get(source)
    if template:
        # URL编码关键词
        keyword = title[:20]
        try:
            from urllib.parse import quote
            return template.format(quote(keyword))
        except:
            return template.replace('{}', keyword.replace(' ', '+'))
    return '#'


def generate_news_data(total_count: int = 220) -> list:
    """生成完整的新闻数据集"""
    news_list = []
    article_id = 1
    
    for year in sorted(YEAR_WEIGHTS.keys()):
        count_for_year = YEAR_WEIGHTS[year]
        keywords = YEAR_KEYWORDS.get(year, ['广告营销'])
        
        month_base = datetime(year, 1, 1)
        max_day = 365
        if (year % 400 == 0) or (year % 100 != 0 and year % 4 == 0):
            max_day = 366
        
        for i in range(count_for_year):
            day_offset = random.randint(0, max_day)
            date = month_base + timedelta(days=day_offset)
            
            # 来源分布
            if year >= 2023:
                source_weights = [8, 10, 12, 8, 20, 22, 20]
            elif year >= 2020:
                source_weights = [15, 15, 12, 8, 18, 17, 15]
            else:
                source_weights = [20, 20, 15, 5, 15, 15, 10]
            
            source = random.choices(SOURCES, weights=source_weights)[0]
            
            # 分类分布
            if year >= 2024:
                cat_weights = [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1.5, 1.5, 1.5, 1.5, 1, 1, 1.5, 1, 1, 1.5, 1, 3, 1, 1, 1.5, 1.5, 1, 1, 1, 1.5]
            elif year >= 2020:
                cat_weights = [1, 2, 1.5, 2, 2, 2.5, 2, 2.5, 2, 1.5, 1.5, 1.5, 2, 2, 0.5, 1, 2, 1, 1.5, 1.5, 2, 1, 1.5, 1.5, 1.5, 1.5, 1, 1, 1, 1.5]
            else:
                cat_weights = [0.5, 2, 1, 1.5, 2, 2.5, 1.5, 1.5, 2, 1, 1.5, 1.5, 2, 2.5, 0.3, 1.5, 2, 1, 0.5, 0.5, 0.3, 0.3, 1, 1.5, 1.5, 1, 0.8, 1.5, 1.5, 1.5]
            
            category = random.choices(CATEGORIES, weights=cat_weights)[0]
            
            # 标题
            title = generate_title(year, category, keywords)
            
            # 影响力
            impact = random.choices(IMPACT_LEVELS, weights=[0.15, 0.35, 0.50])[0]
            
            # 摘要 - 安全格式化
            summary_template = random.choice(SUMMARY_TEMPLATES)
            kw = random.choice(keywords)
            summary = safe_format(summary_template, kw)
            
            # 正文 - 安全格式化
            body = safe_format(BODY_TEMPLATE, kw)
            
            # 标签 (2-5个)
            num_tags = random.randint(2, 5)
            tag_pool = [k for kws in list(YEAR_KEYWORDS.values()) for k in kws] + CATEGORIES[:15]
            tags = random.sample(sorted(set(tag_pool)), min(num_tags, len(set(tag_pool))))
            
            # URL
            url = get_source_search_url(source, title)
            
            item = {
                'id': article_id,
                'title': title,
                'summary': summary,
                'body': body,
                'source': source,
                'category': category,
                'impact': impact,
                'date': date.strftime('%Y-%m-%d'),
                'tags': tags,
                'url': url,
                'readCount': random.randint(100, 50000),
                'shareCount': random.randint(10, 5000),
                'commentCount': random.randint(0, 500),
                'updatedAt': date.strftime('%Y-%m-%d'),
            }
            
            news_list.append(item)
            article_id += 1
    
    # 按日期倒序排列
    news_list.sort(key=lambda x: x['date'], reverse=True)
    
    # 重新分配ID
    for idx, item in enumerate(news_list):
        item['id'] = idx + 1
    
    return news_list


def main():
    print('=' * 60)
    print('ADADD 数据生成器 V2')
    print('生成 220+ 条广告行业全量资讯数据')
    print('=' * 60)
    
    data = generate_news_data(220)
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'news_data.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ 成功生成 {len(data)} 条资讯数据!')
    print(f'📁 文件路径: {output_file}')
    print(f'📊 文件大小: {os.path.getsize(output_file) / 1024:.1f} KB')
    
    # 统计信息
    sources = {}
    categories = {}
    impacts = {}
    years = {}
    
    for item in data:
        s = item['source']
        c = item['category']
        i = item['impact']
        y = item['date'][:4]
        sources[s] = sources.get(s, 0) + 1
        categories[c] = categories.get(c, 0) + 1
        impacts[i] = impacts.get(i, 0) + 1
        years[y] = years.get(y, 0) + 1
    
    print(f'\n--- 数据分布统计 ---')
    print(f'\n按来源:')
    for s, c in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f'  {s}: {c}条')
    
    print(f'\n按年份:')
    for y, c in sorted(years.items(), reverse=True):
        print(f'  {y}: {c}条')
    
    print(f'\n按影响力:')
    for i, c in sorted(impacts.items()):
        label = {'high': '高', 'medium': '中', 'low': '低'}[i]
        print(f'  {label}: {c}条')
    
    print(f'\n分类数量: {len(categories)} 个')
    
    return data


if __name__ == '__main__':
    main()
