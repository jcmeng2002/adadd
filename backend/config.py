# ADADD Backend Configuration

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, 'news_data.json')

# Flask config
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Crawler config
CRAWL_INTERVAL_HOURS = 6  # 每6小时抓取一次
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

# Source configurations - 搜索URL模板和数据源信息
SOURCES = {
    'weibo': {
        'name': '微博',
        'icon': '📱',
        'color': '#E6162D',
        'search_url': 'https://s.weibo.com/weibo?q={keyword}&typeall=1',
        'api_url': None  # 微博API需要授权，用搜索页替代
    },
    'zhihu': {
        'name': '知乎',
        'icon': '💡',
        'color': '#0084FF',
        'search_url': 'https://www.zhihu.com/search?type=content&q={keyword}',
    },
    'wechat': {
        'name': '微信公众号',
        'icon': '📨',
        'color': '#07C160',
        'search_url': 'https://weixin.sogou.com/weixin?type=2&query={keyword}',
    },
    'github': {
        'name': 'GitHub',
        'icon': '🐙',
        'color': '#24292E',
        'search_url': 'https://github.com/search?q={keyword}&type=repositories',
        'api_url': 'https://api.github.com/search/repositories?q={keyword}&sort=stars&per_page=20',
    },
    'tech-media': {
        'name': '技术社区',
        'icon': '⚙️',
        'color': '#ED7B2D',
        'search_url': 'https://juejin.cn/search?query={keyword}',
    },
    'industry-media': {
        'name': '行业媒体',
        'icon': '📰',
        'color': '#0052D9',
        'search_url': 'https://www.google.com/search?q={keyword}+site:madisonboom.com+OR+site:adquan.com+OR+site:socialbeta.com',
    },
    '36kr': {
        'name': '36氪',
        'icon': '🚀',
        'color': '#0066CC',
        'search_url': 'https://36kr.com/search/articles/{keyword}',
        'api_url': 'https://36kr.com/api/search-column/articles?page=1&keyword={keyword}',
    }
}

# Categories
CATEGORIES = [
    'AI与机器学习', '程序化广告', '创意技术', '数据隐私', '品牌营销',
    '社交媒体', '视频广告', '电商广告', '效果营销', '内容营销',
    'MarTech', '广告技术', '用户增长', '移动广告', 'OTT/CTV广告',
    '搜索广告', 'KOL营销', '游戏广告', '出海营销', '合规监管',
    '元宇宙/Web3', 'AIGC', 'CDP', 'DMP', '广告投放平台', '数据分析',
    '消费者洞察', '媒介策略', '品牌升级', '行业趋势'
]

# Impact levels
IMPACT_LEVELS = [
    {'id': 'high', 'label': '高影响力', 'color': '#E02020'},
    {'id': 'medium', 'label': '中影响力', 'color': '#ED7B2D'},
    {'id': 'low', 'label': '一般关注', 'color': '#00A870'},
]
