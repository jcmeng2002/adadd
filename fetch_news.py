#!/usr/bin/env python3
"""
ADADD 动态资讯抓取器 v3.0 — 全平台版
每小时执行，从10个来源抓取最新广告/营销资讯

已实现抓取的来源：
  1. 36氪     (RSS)          → source: 36kr
  2. 梅花网   (RSS)          → source: industry-media
  3. InfoQ    (RSS)          → source: tech-media
  4. 数英网   (RSS)          → source: industry-media
  5. GitHub   (Search API)   → source: github
  6. 政府网   (HTML scrape)  → source: gov
  7. 腾讯科技  (HTML scrape)  → source: tech-media
  8. IMA知识库 (web_fetch)    → source: tencent-ima

暂无法自动抓取（需登录或反爬）：
  - 知乎 (需认证API)
  - 微博 (反爬严格)
  - 微信公众号 (无公开RSS)
  - research (研究报告类，多为PDF/手动整理)
"""

import json, os, re, sys, time, hashlib, subprocess
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from email.utils import parsedate_to_datetime

# ====== 配置 ======
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, 'data', 'news_data.json')
BUILD_SCRIPT = os.path.join(BASE, 'build_v8.py')
CST = timezone(timedelta(hours=8))
TODAY = datetime.now(CST).strftime('%Y-%m-%d')
TODAY_DATE = datetime.now(CST).date()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml,application/xml,text/html,*/*;q=0.9',
}


def log(msg):
    print(f'[{datetime.now(CST).strftime("%H:%M:%S")}] {msg}', flush=True)


# 全局排除词：与广告行业无关的标题直接跳过
BLOCK_KEYWORDS = [
    '招聘','职位','诚聘','急招','Job ','实习','全职','兼职','简历',
    '融资','IPO','上市','财报','股价','市值','股票',
    '芯片半导体','硬件发布','手机发布','汽车发布','电动车','电池技术',
    '游戏发布','影视综艺','体育赛事','娱乐圈','明星','八卦',
    '房价楼市','医疗健康','疫苗药品','教育双减','房产交易',
    '天气预报','自然灾害','军事国防','国际政治','外交',
    # 纯技术无广告关联
    '编程语言入门','Python教程','Java基础','前端框架对比','后端架构',
    '数据库优化','运维部署','代码规范','开源协议','Git使用',
]

def is_relevant(title):
    """判断标题是否与广告/营销/MarTech相关"""
    t = title
    # 先检查排除词
    if any(kw in t for kw in BLOCK_KEYWORDS):
        return False
    return True


def fetch_url(url, timeout=12):
    """通用URL抓取，返回文本内容"""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            ct = resp.headers.get('Content-Type', '')
            m = re.search(r'charset=["\']?([^"\';\s]+)', ct, re.I)
            ch = (m.group(1) if m else 'utf-8').lower()
            if ch in ('iso-8859-1', 'ansi'): ch = 'utf-8'
            return data.decode(ch, errors='replace')
    except Exception as e:
        log(f'  ⚠️ 抓取失败 [{url[:60]}]: {e}')
        return None


def load_data():
    if not os.path.exists(DATA_PATH):
        return [], set(), 0
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            raw = f.read().strip()
            data = json.loads(raw if raw.startswith('[') else raw) if raw else []
        urls = {x.get('url','').rstrip('/') for x in data if x.get('url')}
        mid = max((x['id'] for x in data), default=0)
        return data, urls, mid
    except Exception as e:
        log(f'⚠️ 加载数据失败: {e}')
        return [], set(), 0


def gen_id(url, title):
    return int(hashlib.md5(f'{url}|{title}'.encode()).hexdigest()[:8], 16)


# ====== 分类与标签 ======

CATEGORY_RULES = [
    (r'(AI|人工智能|大模型|LLM|AIGC|生成式|Copilot|Agent|智能体)', 'AI营销工具'),
    (r'(直播|带货|主播|抖音电商|快手电商)', '直播电商'),
    (r'(短视频|抖音|快手|小红书|B站|视频号)', '短视频营销'),
    (r'(私域|社群|企微|微信生态|会员|留存)', '私域运营'),
    (r'(品牌|IP|定位|心智|品牌力)', '品牌营销'),
    (r'(投放|竞价|ROI|ROAS|转化|效果|CTR|CPC|CPM|oCPM|RTA|程序化|DSP|SSP)', '效果广告'),
    (r'MarTech|营销技术|DMP|CDP|CRM|MA|SCRM|CEP', 'MarTech'),
    (r'(数据|分析|洞察|归因|监测|追踪|BI)', '数据分析'),
    (r'(增长|获客|拉新|裂变|用户增长|PLG)', '增长策略'),
    (r'(内容|种草|KOL|KOC|达人|媒介|投放策略)', '内容营销'),
    (r'(公关|舆情|危机|口碑|PR)', '公关危机'),
    (r'(出海|跨境|海外|全球化|本地化)', '品牌出海'),
    (r'(监管|法规|合规|执法|处罚|广告法|反垄断|个人信息|个保法|算法推荐|深度合成)', '监管合规'),
    (r'(报告|白皮书|年度|趋势|预测|市场规模|调研)', '行业报告'),
    (r'(开源|GitHub|框架|SDK|API|工具)', '开源项目'),
    (r'(搜索|SEM|SEO|信息流|Feed流)', '搜索营销'),
]

TAG_PATTERNS = [
    r'AI(?:人工智能)?', r'AIGC', r'大模型', r'LLM', r'ChatGPT', r'Sora', r'Gemini',
    r'抖音', r'快手', r'小红书', r'B站', r'视频号', r'微信', r'微博',
    r'程序化', r'DSP|SSP|ADX', r'RTA', r'DMP|CDP', r'CRM|SCRM',
    r'MarTech', r'AdTech', r'隐私计算', r'联邦学习',
    r'品牌', r'私域', r'增长', r'转化', r'ROI', r'归因',
    r'直播', r'短视频', r'内容', r'KOL|KOC', r'种草',
    r'出海', r'跨境',
    r'监管|合规|广告法', r'数据安全|隐私',
    r'元宇宙|VR|AR', r'数字人|虚拟人',
    r'搜索|SEO|SEM', r'信息流',
    r'腾讯IMA', r'腾讯广告',
]


def pick_cat(title, summary=''):
    text = (title + ' ' + summary).lower()
    for pat, cat in CATEGORY_RULES:
        if re.search(pat, text): return cat
    return '行业动态'


def extract_tags(text, max_tags=4):
    tags = []
    for pat in TAG_PATTERNS:
        m = re.search(pat, text, re.I)
        if m and len(m.group()) >= 2 and m.group() not in tags:
            tags.append(m.group())
            if len(tags) >= max_tags: break
    return tags or ['广告营销']


def clean_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def make_article(url, title, summary, source_key, source_name, date_str=TODAY, impact='low'):
    """构造标准文章对象"""
    return {
        'id': gen_id(url, title),
        'title': title,
        'original_title': title,
        'summary': summary[:300] if summary else f'{source_name}最新报道',
        'body': f'## {title}\n\n{summary}\n\n---\n*来源：{source_name} · 自动抓取于 {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}*',
        'source': source_key,
        'category': pick_cat(title, summary),
        'tags': extract_tags(title + ' ' + summary),
        'impact': impact,
        'year': date_str[:4],
        'date': date_str,
        'url': url,
        'readCount': 0, 'shareCount': 0, 'commentCount': 0,
        'updatedAt': TODAY,
    }


# =====================================================================
#  抓取器 #1 — 36氪 RSS
# =====================================================================

def fetch_36kr(existing_urls):
    log('🔍 [36氪] 抓取中...')
    xml = fetch_url('https://www.36kr.com/feed', timeout=12)
    if not xml: return []

    articles = []
    items = re.findall(r'<item[^>]*>(.*?)</item>', xml, re.S)
    keywords = ['广告','营销','投放','品牌','MarTech','程序化','DSP','RTA','DMP','CDP','增长','私域',
                '转化','ROI','效果','AIGC','电商','内容营销','KOL','直播带货','信息流广告',
                '品牌出海','用户增长','流量','获客','复购','GMV','种草','达人']

    for item_xml in items[:30]:
        t_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', item_xml, re.S)
        if not t_m: continue
        title = (t_m.group(1) or t_m.group(2)).strip()

        l_m = re.search(r'<link>(.*?)</link>', item_xml)
        url = (l_m.group(1) or '').split('<')[0].strip().rstrip('/')
        if not url: continue
        if url.rstrip('/') in existing_urls: continue

        t_lower = title.lower()
        if not any(kw in t_lower for kw in keywords): continue
        if not is_relevant(title): continue  # 全局排除无关内容

        date_str = TODAY
        p_m = re.search(r'<pubDate>(.*?)</pubDate>', item_xml)
        if p_m:
            try:
                dt = parsedate_to_datetime(p_m.group(1).strip())
                pd = dt.astimezone(CST).date()
                if (TODAY_DATE - pd).days > 7: continue
                date_str = pd.strftime('%Y-%m-%d')
            except: pass

        d_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item_xml, re.S)
        desc = clean_html(d_m.group(1))[:300] if d_m else ''

        articles.append(make_article(url, title, desc, '36kr', '36氪', date_str))
        existing_urls.add(url.rstrip('/'))

    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #2 — 梅花网 RSS
# =====================================================================

def fetch_meihua(existing_urls):
    log('🔍 [梅花网] 抓取中...')
    xml = fetch_url('https://www.meihua.info/feed/', timeout=12)
    if not xml: return []

    articles = []
    items = re.findall(r'<item[^>]*>(.*?)</item>', xml, re.S)

    for item_xml in items[:15]:
        t_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', item_xml, re.S)
        if not t_m: continue
        title = (t_m.group(1) or t_m.group(2)).strip()
        # 过滤招聘信息
        if any(kw in title for kw in ['招聘','职位','诚聘','急招']): continue

        l_m = re.search(r'<link>(.*?)</link>', item_xml)
        url = (l_m.group(1) or '').split('<')[0].strip().rstrip('/')
        if not url: continue
        if url.rstrip('/') in existing_urls: continue

        date_str = TODAY
        p_m = re.search(r'<pubDate>(.*?)</pubDate>', item_xml)
        if p_m:
            try:
                dt = parsedate_to_datetime(p_m.group(1).strip())
                pd = dt.astimezone(CST).date()
                if (TODAY_DATE - pd).days > 14: continue
                date_str = pd.strftime('%Y-%m-%d')
            except: pass

        d_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item_xml, re.S)
        desc = clean_html(d_m.group(1))[:300] if d_m else ''

        articles.append(make_article(url, title, desc, 'industry-media', '梅花网', date_str))
        existing_urls.add(url.rstrip('/'))

    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #3 — InfoQ RSS
# =====================================================================

def fetch_infoq(existing_urls):
    log('🔍 [InfoQ] 抓取中...')
    xml = fetch_url('https://www.infoq.cn/feed', timeout=12)
    if not xml: return []

    articles = []
    items = re.findall(r'<item[^>]*>(.*?)</item>', xml, re.S)
    keywords = ['广告','营销','推荐系统','搜索广告','程序化广告','投放','增长',
                '数据驱动','AIGC营销','AI营销','智能投放','转化率','用户画像',
                '品牌策略','内容营销','KOL','信息流','流量变现']

    for item_xml in items[:20]:
        t_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', item_xml, re.S)
        if not t_m: continue
        title = (t_m.group(1) or t_m.group(2)).strip()

        l_m = re.search(r'<link>(.*?)</link>', item_xml)
        url = (l_m.group(1) or '').split('<')[0].strip().rstrip('/')
        if not url: continue
        if url.rstrip('/') in existing_urls: continue

        t_lower = title.lower()
        if not any(kw in t_lower for kw in keywords): continue
        if not is_relevant(title): continue  # 全局排除无关内容

        date_str = TODAY
        p_m = re.search(r'<published>(.*?)</published>|<pubDate>(.*?)</pubDate>', item_xml)
        if p_m:
            try:
                dt_str = (p_m.group(1) or p_m.group(2) or '').strip()
                dt = parsedate_to_datetime(dt_str)
                pd = dt.astimezone(CST).date()
                if (TODAY_DATE - pd).days > 14: continue
                date_str = pd.strftime('%Y-%m-%d')
            except: pass

        d_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>|<summary[^>]*>(.*?)</summary>', item_xml, re.S)
        desc = clean_html(d_m.group(1) or d_m.group(2) or '')[:300]

        articles.append(make_article(url, title, desc, 'tech-media', 'InfoQ', date_str))
        existing_urls.add(url.rstrip('/'))

    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #4 — 数英网（HTML爬取，RSS已下线）
# =====================================================================

def fetch_digitaling(existing_urls):
    log('🔍 [数英网] 抓取中...')
    html = fetch_url('https://www.digitaling.com/', timeout=12)
    if not html: return []

    articles = []
    # 从首页提取文章链接和标题
    links = re.findall(r'href="(https://www\.digitaling\.com/articles/\d+\.html)"[^>]*title="([^"]{10,80})"', html)
    
    for url, title in links[:25]:
        title = clean_html(title)
        if not title: continue
        # 只做排除词过滤（招聘/融资等无关内容）
        if not is_relevant(title): continue
        
        if url.rstrip('/') in existing_urls: continue
        
        articles.append(make_article(url, title, '', 'industry-media', '数英网', TODAY))
        existing_urls.add(url.rstrip('/'))

    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #5 — GitHub 搜索 (AdTech/MarTech相关项目)
# =====================================================================

def fetch_github(existing_urls):
    log('🔍 [GitHub] 搜索AdTech/MarTech项目中...')
    articles = []
    
    queries = [
        'adtech+advertising+pushed:>2026-04-01',
        'martech+marketing+analytics+pushed:>2026-04-01',
        'programmatic+DSP+RTA+pushed:>2026-04-01',
        'CDP+customer+data+platform+pushed:>2026-04-01',
        'advertising-sdk+ad-network+pushed:>2026-04-01',
    ]
    
    seen_urls = set()
    for q in queries[:2]:  # 避免太多请求
        try:
            api_url = f'https://api.github.com/search/repositories?q={q}&sort=updated&per_page=5&order=desc'
            req = Request(api_url, headers={'User-Agent': 'ADADD-Bot/1.0'})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            
            for repo in data.get('items', []):
                url = repo['html_url']
                if url in seen_urls or url.rstrip('/') in existing_urls: continue
                seen_urls.add(url)
                
                name = repo.get('full_name', '')
                desc = repo.get('description') or ''
                stars = repo.get('stargazers_count', 0)
                
                # 至少有描述和一定star数的才收录
                if not desc or stars < 1: continue
                
                title = f'[GitHub] {name} ⭐{stars}'
                summary = f"{desc} (⭐{stars} Stars, 语言:{repo.get('language','N/A')}, 最近更新:{repo.get('updated_at','')[:10]})"
                updated = repo.get('updated_at', '')[:10]
                
                articles.append(make_article(
                    url, title, summary, 'github', 'GitHub',
                    date_str=updated, impact='medium'
                ))
                existing_urls.add(url.rstrip('/'))
                
        except Exception as e:
            log(f'  ⚠️ GitHub搜索失败 [{q[:30]}]: {e}')
    
    log(f'  ✅ +{len(articles)} 个项目')
    return articles


# =====================================================================
#  抓取器 #6 — 政府网新闻 (监管/政策相关)
# =====================================================================

def fetch_gov(existing_urls):
    log('🔍 [政府网] 抓取监管/政策新闻中...')
    articles = []
    
    html = fetch_url('http://www.gov.cn/xinwen/yaowen.htm', timeout=15)
    if not html:
        # 备用：尝试其他页面
        html = fetch_url('http://www.gov.cn/', timeout=15)
    if not html: return []

    # 提取文章链接和标题 — 支持多种gov.cn页面格式
    links = re.findall(
        r'<a[^>]+href="([^"]+)"[^>]*>(?:<span[^>]*>)?([^<]{8,100})(?:</span>)?</a>',
        html
    )
    
    gov_keywords = ['广告','监管','平台经济','企业','互联网','数据安全','算法推荐',
                     '个人信息保护','消费者','竞争法','反垄断','处罚','执法',
                     '虚假宣传','互联网广告','直播带货','网红','流量']
    
    for raw_url, title in links:
        title = clean_html(title)
        if not any(k in title for k in gov_keywords): continue
        if not is_relevant(title): continue
        
        # 补全相对URL
        if raw_url.startswith('/'):
            url = f'http://www.gov.cn{raw_url}'
        elif raw_url.startswith('http'):
            url = raw_url
        else:
            continue
        
        if url.rstrip('/') in existing_urls: continue
        
        articles.append(make_article(
            url, title, '',
            'gov', '中国政府网',
            date_str=TODAY, impact='high'
        ))
        existing_urls.add(url.rstrip('/'))
        
        if len(articles) >= 10: break
    
    # 如果没找到足够内容，尝试搜索特定频道
    if len(articles) < 3:
        channels = [
            ('http://www.gov.cn/yaowen/liebiao.htm', '要闻'),
            ('http://www.gov.cn/xinwen/index.htm', '新闻'),
        ]
        for ch_url, ch_name in channels:
            ch_html = fetch_url(ch_url, timeout=10)
            if not ch_html: continue
            ch_links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*title="([^"]{10,80})"', ch_html)
            for ru, ti in ch_links:
                ti = clean_html(ti)
                if not any(k in ti for k in gov_keywords): continue
                full_url = f'http://www.gov.cn{ru}' if ru.startswith('/') else ru
                if full_url.rstrip('/') in existing_urls: continue
                articles.append(make_article(full_url, ti, '', 'gov', f'中国政府网-{ch_name}', TODAY, 'high'))
                existing_urls.add(full_url.rstrip('/'))
                if len(articles) >= 8: break
            if len(articles) >= 8: break
    
    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #7 — 腾讯科技 (HTML抓取)
# =====================================================================

def fetch_tech_qq(existing_urls):
    log('🔍 [腾讯科技] 抓取中...')
    articles = []
    
    html = fetch_url('https://tech.qq.com/', timeout=12)
    if not html: return []

    # 腾讯科技文章链接模式
    links = re.findall(r'<a[^>]+href="((/a/\d+\.htm)[^"]*)"[^>]*>([^<]{10,80})</a>', html)
    
    tech_keywords = ['广告','营销','投放','品牌','AIGC','大模型','数字营销','智能投放',
                      '搜索','推荐算法','增长黑客','用户运营','内容分发','流量',
                      '程序化','DSP','RTA','DMP','CDP','私域']
    
    for raw_url, path, title in links:
        title = clean_html(title)
        if not any(k in title for k in tech_keywords): continue
        if not is_relevant(title): continue
        
        url = f'https://tech.qq.com{raw_url}' if raw_url.startswith('/') else raw_url
        if url.rstrip('/') in existing_urls: continue
        
        articles.append(make_article(url, title, '', 'tech-media', '腾讯科技', TODAY))
        existing_urls.add(url.rstrip('/'))
        
        if len(articles) >= 8: break
    
    log(f'  ✅ +{len(articles)} 篇')
    return articles


# =====================================================================
#  抓取器 #8 — IMA知识库 (Playwright SPA渲染 + 本地缓存)
# =====================================================================

def fetch_ima(existing_urls):
    """
    腾讯IMA知识库抓取 — 使用Playwright渲染SPA页面

    策略：
      1. 优先读取 .ima_articles_full.json（Playwright预提取的完整数据）
      2. 若文件不存在或过期，尝试用Playwright实时抓取
      3. 匹配现有URL去重，只返回新增文章（近30天内的）
    """
    log('🔍 [腾讯IMA] 抓取中...')
    articles = []
    ima_data_path = os.path.join(BASE, '.ima_articles_full.json')
    ima_share_id = 'b5b4c214a31d4b924c4561307f77ba3e540455e4f20f56d36f98ea4fff10c742'
    ima_url = f'https://ima.qq.com/wiki/?shareId={ima_share_id}'

    # ====== 方案1：读取本地已提取的数据缓存 ======
    IMA_CACHE_MAX_DAYS = 3  # 缓存超过此天数自动走Playwright刷新
    if os.path.exists(ima_data_path):
        try:
            from datetime import datetime as dt
            ftime = dt.fromtimestamp(os.path.getmtime(ima_data_path)).date()
            age_days = (TODAY_DATE - ftime).days

            if age_days > IMA_CACHE_MAX_DAYS:
                log(f'  ⏰ 缓存已过期({age_days}天前)，跳过旧缓存，将使用Playwright实时抓取...')
            else:
                with open(ima_data_path, 'r', encoding='utf-8') as f:
                    ima_items = json.load(f)

                if isinstance(ima_items, list) and len(ima_items) > 0:
                    import urllib.parse
                    for item in ima_items:
                        title = item.get('title', '')
                        url = item.get('url', '')
                        date_str = item.get('date', TODAY)
                        if not title: continue

                        norm_url = url.rstrip('/') if url else f"ima://{title}"
                        if norm_url in existing_urls: continue

                        # 只收录近30天文章
                        try:
                            article_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            if (TODAY_DATE - article_date).days > 30: continue
                        except Exception: pass

                        tags_str = ', '.join(item.get('tags', []))
                        summary = f"[腾讯IMA知识库] {tags_str}" if tags_str else '腾讯广告官方营销知识库'

                        articles.append(make_article(
                            url or ima_url, title, summary,
                            'tencent-ima', '腾讯IMA', date_str, impact='medium'
                        ))
                        existing_urls.add(norm_url)

                    log(f'  ✅ 从本地缓存 +{len(articles)} 篇 (共{len(ima_items)}条, 缓存{age_days}天前)')
                    return articles

        except Exception as e:
            log(f'  ⚠️ 读取本地IMA缓存失败: {e}')

    # ====== 方案2：用Playwright实时抓取SPA页面 ======
    log('  尝试Playwright实时抓取...')
    try:
        from playwright.sync_api import sync_playwright
        import urllib.parse

        with sync_playwright() as pwr:
            browser = pwr.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(ima_url, timeout=40000, wait_until='networkidle')
            time.sleep(2)

            # 反复滚动+点击加载更多
            for _ in range(50):
                page.evaluate('() => window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(0.3)
                clicked = page.evaluate('''() => {
                    for (const el of document.querySelectorAll('*')) {
                        const t = (el.innerText||'').trim();
                        if ((t==='加载更多'||t==='查看更多') && el.offsetParent !== null) { el.click(); return true; }
                    }
                    return false;
                }''')
                if clicked: time.sleep(0.8)
                elif _ > 15: break

            time.sleep(2)

            body_text = page.inner_text('body')
            lines = [l.strip() for l in body_text.split('\n') if l.strip()]

            start_idx = next((i+1 for i,l in enumerate(lines) if '订阅知识库' in l), None)
            end_idx = next((i for i,l in enumerate(lines) if '基于知识库提问' in l), len(lines))

            if start_idx:
                art_lines = lines[start_idx:end_idx]
                date_re = re.compile(r'^\d{2}/\d{1,2}/\d{2}$')

                cur_title, cur_tags = '', []
                all_items = []

                for line in art_lines:
                    if date_re.match(line):
                        if cur_title:
                            parts = line.split('/')
                            dstr = f"20{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                            all_items.append({'title': cur_title, 'date': dstr, 'tags': list(cur_tags)})
                        cur_title, cur_tags = '', []
                    elif cur_title == '' and len(line) > 5:
                        cur_title, cur_tags = line, []
                    else:
                        if line: cur_tags.append(line)

                # 缓存到文件
                with open(ima_data_path, 'w', encoding='utf-8') as cf:
                    json.dump(all_items, cf, ensure_ascii=False, indent=2)

                # 构建文章对象
                for item in all_items:
                    title = item['title']
                    dstr = item['date']
                    url = f"{ima_url}&title={urllib.parse.quote(title)}"
                    if url.rstrip('/') in existing_urls: continue

                    try:
                        adate = datetime.strptime(dstr, '%Y-%m-%d').date()
                        if (TODAY_DATE - adate).days > 30: continue
                    except Exception: pass

                    tags_str = ', '.join(item.get('tags', []))
                    summary = f"[腾讯IMA知识库] {tags_str}" if tags_str else '腾讯广告官方营销知识库'

                    articles.append(make_article(url, title, summary, 'tencent-ima', '腾讯IMA', dstr, 'medium'))
                    existing_urls.add(url.rstrip('/'))

                log(f'  ✅ Playwright抓取 +{len(articles)} 篇 (总计{len(all_items)}条, 已缓存)')

            browser.close()

        return articles

    except ImportError:
        log('  ⚠️ playwright未安装，跳过。运行: pip install playwright && playwright install chromium')
    except Exception as e:
        log(f'  ⚠️ Playwright抓取异常: {e}')

    if not articles:
        log('  ℹ️ 本轮IMA无新文章（需playwright或提供 .ima_articles_full.json）')

    return articles


# =====================================================================
#  主流程
# =====================================================================

def main():
    log('=' * 55)
    log('ADADD 动态抓取 v3.0 — 全平台版')
    log(f'今日: {TODAY}')
    log('=' * 55)
    
    t0 = time.time()
    existing_data, existing_urls, _ = load_data()
    log(f'现有: {len(existing_data)} 条 | 已知URL: {len(existing_urls)}')
    
    all_new = []
    
    # 按优先级依次执行各源抓取
    fetchers = [
        ('36氪', fetch_36kr),
        ('梅花网', fetch_meihua),
        ('InfoQ', fetch_infoq),
        ('数英网', fetch_digitaling),
        ('GitHub', fetch_github),
        ('政府网', fetch_gov),
        ('腾讯科技', fetch_tech_qq),
        ('腾讯IMA', fetch_ima),
    ]
    
    for name, fetcher_fn in fetchers:
        try:
            arts = fetcher_fn(existing_urls)
            all_new.extend(arts)
        except Exception as e:
            log(f'  ❌ [{name}] 异常: {e}')
    
    if not all_new:
        log('\n📭 本轮无新增，跳过构建')
        return 0
    
    # 合并 → 排序 → 写入
    merged = all_new + existing_data
    merged.sort(key=lambda x: x.get('date',''), reverse=True)
    
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    # 统计各来源新增量
    from collections import Counter
    src_cnt = Counter(a['source'] for a in all_new)
    src_summary = ', '.join([f'{k}(+{v})' for k, v in src_cnt.most_common()])
    
    log(f'\n✨ 新增 {len(all_new)} 篇! 总计 {len(merged)} 条')
    log(f'   来源分布: {src_summary}')
    
    # 构建
    log('🔨 build_v8.py ...')
    try:
        r = subprocess.run([sys.executable, BUILD_SCRIPT], capture_output=True, text=True, cwd=BASE, timeout=60)
        log(f'  {"✅" if r.returncode==0 else "⚠️"} 构建完成')
        if r.stdout.strip(): log(f'  stdout: {r.stdout.strip()[:200]}')
    except Exception as e:
        log(f'❌ 构建异常: {e}')
    
    # 推送到 GitHub Pages（有新增内容才推）
    if all_new:
        log('🚀 推送到 GitHub ...')
        try:
            subprocess.run(['git', 'add', 'index.html', 'data/news_data.json'], 
                          capture_output=True, text=True, cwd=BASE)
            today = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            msg = f'auto: +{len(all_new)}篇 ({src_summary}) | {today}'
            r = subprocess.run(['git', 'commit', '-m', msg],
                              capture_output=True, text=True, cwd=BASE)
            if r.returncode == 0:
                r2 = subprocess.run(['git', 'push'], capture_output=True, text=True, cwd=BASE, timeout=30)
                log(f'  {"✅ 已上线" if r2.returncode==0 else f"⚠️ push失败"}')
            else:
                log('  ⏭️ 无变更（可能已提交）')
        except Exception as e:
            log(f'  ❌ 推送异常: {e}')
    
    elapsed = time.time() - t0
    log(f'\n⏱️ 总耗时 {elapsed:.1f}s | +{len(all_new)}篇 ({src_summary})')
    return len(all_new)


if __name__ == '__main__':
    exit(main() or 0)
