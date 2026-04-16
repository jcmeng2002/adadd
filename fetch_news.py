#!/usr/bin/env python3
"""
ADADD 动态资讯抓取器 v2.0 — 精简稳定版
每小时执行，从可用RSS源抓取最新广告/营销资讯
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
    'Accept': 'application/rss+xml,application/xml,text/xml,*/*;q=0.9',
}

# ====== 可用RSS源（已验证可达） ======
RSS_SOURCES = [
    {
        'url': 'https://www.36kr.com/feed',
        'name': '36氪',
        'source_key': '36kr',
        'keywords': ['广告','营销','投放','品牌','MarTech','程序化','DSP','RTA','DMP','CDP','增长','私域','转化','ROI','效果','AIGC','AI'],
        'max_items': 30,
    },
    {
        'url': 'https://www.meihua.info/feed/',
        'name': '梅花网',
        'source_key': 'industry-media',
        'keywords': [],  # 全量收录
        'max_items': 15,
    },
    {
        'url': 'https://www.infoq.cn/feed',
        'name': 'InfoQ',
        'source_key': 'tech-media',
        'keywords': ['广告','营销','推荐','搜索','增长','数据','推荐系统','算法'],
        'max_items': 20,
    },
]

CATEGORY_RULES = [
    (r'(AI|人工智能|大模型|LLM|AIGC|生成式|Copilot|Agent)', 'AI营销工具'),
    (r'(直播|带货|主播|抖音电商|快手电商)', '直播电商'),
    (r'(短视频|抖音|快手|小红书|B站)', '短视频营销'),
    (r'(私域|社群|企微|微信生态|会员|留存)', '私域运营'),
    (r'(品牌|IP|定位|心智)', '品牌营销'),
    (r'(投放|竞价|ROI|ROAS|转化|效果|CTR|CPC|CPM|oCPM|RTA|程序化|DSP)', '效果广告'),
    (r'MarTech|营销技术|DMP|CDP|CRM|MA|SCRM', 'MarTech'),
    (r'(数据|分析|洞察|归因|监测|追踪)', '数据分析'),
    (r'(增长|获客|拉新|裂变|用户)', '增长策略'),
    (r'(内容|种草|KOL|KOC|达人|媒介)', '内容营销'),
    (r'(公关|舆情|危机|口碑)', '公关危机'),
    (r'(出海|跨境|海外|全球化)', '品牌出海'),
    (r'(监管|法规|合规|执法|处罚|广告法|反垄断|个人信息|个保法)', '监管合规'),
    (r'(报告|白皮书|年度|趋势|预测|市场规模)', '行业报告'),
    (r'(开源|GitHub|框架|SDK|API)', '开源项目'),
    (r'(搜索|SEM|SEO|信息流)', '搜索营销'),
]

TAG_PATTERNS = [
    r'AI(?:人工智能)?', r'AIGC', r'大模型', r'LLM', r'ChatGPT', r'Sora',
    r'抖音', r'快手', r'小红书', r'B站', r'微信', r'微博',
    r'程序化', r'DSP|SSP|ADX', r'RTA', r'DMP|CDP', r'CRM|SCRM',
    r'MarTech', r'AdTech', r'隐私计算', r'联邦学习',
    r'品牌', r'私域', r'增长', r'转化', r'ROI', r'归因',
    r'直播', r'短视频', r'内容', r'KOL|KOC',
    r'出海', r'跨境',
    r'监管|合规|广告法', r'数据安全|隐私',
    r'元宇宙|VR|AR', r'数字人|虚拟人',
    r'搜索|SEO|SEM', r'信息流',
]


def log(msg):
    print(f'[{datetime.now(CST).strftime("%H:%M:%S")}] {msg}', flush=True)


def fetch_url(url, timeout=12):
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
        log(f'  ⚠️ 抓取失败 [{url[:50]}]: {e}')
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
    return re.sub(r'<[^>]+>', '', s).strip()


# ====== RSS解析核心 ======

def parse_rss(xml_text, source_config, existing_urls):
    """解析RSS XML，返回文章列表"""
    articles = []
    
    # 兼容 RSS 2.0 和 Atom
    items = re.findall(r'<item[^>]*>(.*?)</item>', xml_text, re.S)
    if not items:
        items = re.findall(r'<entry[^>]*>(.*?)</entry>', xml_text, re.S)
    
    sk = source_config['source_key']
    kws = source_config.get('keywords', [])
    name = source_config['name']
    
    for item_xml in items[:source_config['max_items']]:
        # 标题
        t_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>|<title[^>]*>(.*?)</title>', item_xml, re.S)
        if not t_m: continue
        title = (t_m.group(1) or t_m.group(2) or t_m.group(3) or '').strip()
        
        # 链接
        l_m = re.search(r'<link>(.*?)</link>|<link[^>]*href=["\']([^"\']+)["\']', item_xml)
        url = ((l_m.group(1) or l_m.group(2) or '').split('<')[0]).strip().rstrip('/')
        if not url: continue
        
        # 去重
        norm_url = url.rstrip('/')
        if norm_url in existing_urls: continue
        
        # 关键词过滤（空列表表示全量收录）
        if kws:
            t_lower = title.lower()
            if not any(kw in t_lower for kw in kws): continue
        
        # 时间
        date_str = TODAY
        p_m = re.search(r'<pubDate>(.*?)</pubDate>|<published>(.*?)</published>|<updated>(.*?)</updated>', item_xml, re.S)
        if p_m:
            try:
                dt_str = p_m.group(1) or p_m.group(2) or p_m.group(3) or ''
                dt = parsedate_to_datetime(dt_str.strip())
                pub_date = dt.astimezone(CST).date()
                # 超过3天的不收录
                if (TODAY_DATE - pub_date).days > 3: continue
                date_str = pub_date.strftime('%Y-%m-%d')
            except: pass
        
        # 摘要
        d_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>|<summary[^>]*>(.*?)</summary>', item_xml, re.S)
        desc = clean_html(d_m.group(1) or d_m.group(2) or d_m.group(3) or '')[:300]
        
        impact = 'high' if sk == 'gov' else ('medium' if sk in ('research','zhihu') else 'low')
        
        articles.append({
            'id': gen_id(url, title),
            'title': title,
            'original_title': title,
            'summary': desc or f'{name}最新报道',
            'body': f'## {title}\n\n{desc}\n\n---\n*来源：{name} · 自动抓取于 {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}*',
            'source': sk,
            'category': pick_cat(title, desc),
            'tags': extract_tags(title + ' ' + desc),
            'impact': impact,
            'year': date_str[:4],
            'date': date_str,
            'url': url,
            'readCount': 0, 'shareCount': 0, 'commentCount': 0,
            'updatedAt': TODAY,
        })
        existing_urls.add(norm_url)
    
    return articles


# ====== 主流程 ======

def main():
    log('=' * 50)
    log('ADADD 动态抓取 v2.0')
    log(f'今日: {TODAY}')
    log('=' * 50)
    
    t0 = time.time()
    existing_data, existing_urls, _ = load_data()
    log(f'现有: {len(existing_data)} 条')
    
    all_new = []
    
    for src in RSS_SOURCES:
        log(f'\n🔍 [{src["name"]}] {src["url"][:50]}...')
        xml = fetch_url(src['url'])
        if not xml: continue
        arts = parse_rss(xml, src, existing_urls)
        all_new.extend(arts)
        if arts:
            log(f'  ✅ +{len(arts)} 篇')
        else:
            log(f'  ℹ️ 无新文章')
    
    if not all_new:
        log('\n📭 本轮无新增，跳过构建')
        return 0
    
    # 合并 → 排序 → 写入
    merged = all_new + existing_data
    merged.sort(key=lambda x: x.get('date',''), reverse=True)
    
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    log(f'\n✨ 新增 {len(all_new)} 篇! 总计 {len(merged)} 条')
    
    # 构建
    log('🔨 build_v8.py ...')
    try:
        r = subprocess.run([sys.executable, BUILD_SCRIPT], capture_output=True, text=True, cwd=BASE, timeout=60)
        log(f'  {"✅" if r.returncode==0 else "⚠️"} 构建完成')
        if r.stdout.strip(): log(f'  {r.stdout.strip()}')
    except Exception as e:
        log(f'❌ 构建异常: {e}')
    
    log(f'\n⏱️ 总耗时 {time.time()-t0:.1f}s | +{len(all_new)}篇')
    return len(all_new)


if __name__ == '__main__':
    exit(main() or 0)
