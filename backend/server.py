#!/usr/bin/env python3
"""
ADADD 后端 API 服务器
Flask RESTful API + 数据聚合 + 实时搜索代理
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# 初始化 Flask
app = Flask(__name__, static_folder=None)
CORS(app)  # 允许跨域请求

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('adadd')

# ============================================================
# 数据加载
# ============================================================

_data_cache = {
    'data': None,
    'last_loaded': None,
    'stats': None,
}


def load_data(force=False):
    """加载数据（带缓存）"""
    if not force and _data_cache['data'] is not None:
        return _data_cache['data']
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _data_cache['data'] = data
            _data_cache['last_loaded'] = datetime.now().isoformat()
            logger.info(f"✅ 已加载 {len(data)} 条数据 from {DATA_FILE}")
            return data
        else:
            logger.warning(f"⚠️ 数据文件不存在: {DATA_FILE}，返回空列表")
            return []
    except Exception as e:
        logger.error(f"❌ 加载数据失败: {e}")
        return []


def get_stats():
    """计算统计数据"""
    if _data_cache['stats'] is not None:
        return _data_cache['stats']
    
    data = load_data()
    
    sources = {}
    categories = {}
    impacts = {}
    years = {}
    tag_counts = {}
    
    for item in data:
        s = item.get('source', 'unknown')
        c = item.get('category', '未分类')
        i = item.get('impact', 'low')
        d = item.get('date', '')
        y = d[:4] if len(d) >= 4 else '未知'
        tags = item.get('tags', [])
        
        sources[s] = sources.get(s, 0) + 1
        categories[c] = categories.get(c, 0) + 1
        impacts[i] = impacts.get(i, 0) + 1
        years[y] = years.get(y, 0) + 1
        
        for t in tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    
    stats = {
        'total': len(data),
        'sources': sources,
        'categories': categories,
        'impacts': impacts,
        'years': dict(sorted(years.items(), reverse=True)),
        'topTags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:30],
        'dateRange': {'earliest': min(years.keys()) if years else '', 'latest': max(years.keys()) if years else ''},
    }
    
    _data_cache['stats'] = stats
    return stats


def clear_cache():
    """清除数据缓存"""
    _data_cache['data'] = None
    _data_cache['stats'] = None
    _data_cache['last_loaded'] = None


# ============================================================
# API 路由
# ============================================================

@app.route('/')
def serve_frontend():
    """提供前端页面"""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    
    # Fallback: 尝试根目录的index.html
    root_index = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
    if os.path.exists(root_index):
        return send_file(root_index)
    
    return jsonify({'error': 'Frontend not found'}), 404


@app.route('/api/health')
def health_check():
    """健康检查"""
    data = load_data()
    return jsonify({
        'status': 'ok',
        'service': 'ADADD Backend',
        'version': '2.0.0',
        'data_count': len(data),
        'cache_time': _data_cache['last_loaded'],
        'timestamp': datetime.now().isoformat(),
    })


@app.route('/api/news')
def get_news():
    """
    获取资讯列表（支持分页、筛选、排序、搜索）
    
    Query Params:
    - page: 页码 (default: 1)
    - pageSize: 每页数量 (default: 12, max: 50)
    - source: 来源筛选 (可选，逗号分隔多个)
    - category: 分类筛选 (可选，逗号分隔多个)
    - impact: 影响力筛选 (high/medium/low)
    - year: 年份筛选 (可选，逗号分隔多个)
    - keyword: 关键词搜索
    - sort: 排序方式 (latest/oldest/hot, default: latest)
    - viewMode: 视图模式 (card/timeline)
    """
    data = load_data()
    
    # 解析参数
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('pageSize', 12)), 50)
    source_filter = request.args.get('source', '').split(',') if request.args.get('source') else []
    category_filter = request.args.get('category', '').split(',') if request.args.get('category') else []
    impact_filter = request.args.get('impact', '')
    year_filter = request.args.get('year', '').split(',') if request.args.get('year') else []
    keyword = request.args.get('keyword', '').strip().lower()
    sort_by = request.args.get('sort', 'latest')
    
    # 过滤
    filtered = []
    for item in data:
        # 来源筛选
        if source_filter and source_filter != ['']:
            if item.get('source') not in source_filter:
                continue
        
        # 分类筛选
        if category_filter and category_filter != ['']:
            if item.get('category') not in category_filter:
                continue
        
        # 影响力筛选
        if impact_filter and item.get('impact') != impact_filter:
            continue
        
        # 年份筛选
        if year_filter and year_filter != ['']:
            item_year = item.get('date', '')[:4]
            if item_year not in year_filter:
                continue
        
        # 关键词搜索（标题+摘要+标签）
        if keyword:
            searchable = f"{item.get('title','')} {item.get('summary','')} {item.get('summary','')} {' '.join(item.get('tags',[]))}"
            if keyword.lower() not in searchable.lower():
                continue
        
        filtered.append(item)
    
    # 排序
    if sort_by == 'oldest':
        filtered.sort(key=lambda x: x.get('date', ''))
    elif sort_by == 'hot':
        filtered.sort(key=lambda x: int(x.get('readCount', 0)), reverse=True)
    else:  # latest
        filtered.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]
    
    # 时间轴模式分组
    timeline_groups = {}
    if request.args.get('viewMode') == 'timeline':
        for item in filtered:
            y = item.get('date', '')[:4]
            if y not in timeline_groups:
                timeline_groups[y] = []
            timeline_groups[y].append(item)
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'items': items,
            'total': total,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size if total > 0 else 1,
            'timelineGroups': dict(sorted(timeline_groups.items(), reverse=True)) if timeline_groups else None,
            'filtersApplied': bool(source_filter or category_filter or impact_filter or year_filter or keyword),
        }
    })


@app.route('/api/news/<int:item_id>')
def get_news_detail(item_id):
    """获取单条新闻详情"""
    data = load_data()
    for item in data:
        if item.get('id') == item_id:
            return jsonify({'code': 0, 'data': item})
    return jsonify({'code': 404, 'message': 'Not found'}), 404


@app.route('/api/stats')
def get_api_stats():
    """获取统计数据"""
    stats = get_stats()
    
    # 补充来源配置信息
    source_details = {}
    for s, count in stats['sources'].items():
        cfg = SOURCES.get(s, {})
        source_details[s] = {
            'name': cfg.get('name', s),
            'icon': cfg.get('icon', '📄'),
            'color': cfg.get('color', '#666'),
            'count': count,
        }
    
    return jsonify({
        'code': 0,
        'data': {
            **stats,
            'sourceDetails': source_details,
            'sourceConfigs': SOURCES,
            'categories': CATEGORIES,
            'impactLevels': IMPACT_LEVELS,
        }
    })


@app.route('/api/sources')
def get_sources():
    """获取数据源列表及统计"""
    stats = get_stats()
    result = []
    for sid, cfg in SOURCES.items():
        result.append({
            'id': sid,
            'name': cfg.get('name', sid),
            'icon': cfg.get('icon', ''),
            'color': cfg.get('color', '#666'),
            'searchUrl': cfg.get('search_url', ''),
            'count': stats['sources'].get(sid, 0),
        })
    return jsonify({'code': 0, 'data': result})


@app.route('/api/categories')
def get_categories():
    """获取分类列表及统计"""
    stats = get_stats()
    result = []
    for cat in CATEGORIES:
        result.append({
            'name': cat,
            'count': stats['categories'].get(cat, 0),
        })
    return jsonify({'code': 0, 'data': result})


@app.route('/api/search/live')
def live_search():
    """
    实时搜索 - 返回外部平台的搜索URL
    让前端直接跳转到各平台进行实时搜索
    
    Query Params:
    - keyword: 搜索关键词
    - sources: 要搜索的平台 (可选，默认全部)
    - category: 分类 (可选，追加到搜索词)
    """
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({
            'code': 400,
            'message': 'keyword is required',
            'data': []
        }), 400
    
    source_filter = request.args.get('sources', '').split(',') if request.args.get('sources') else []
    category = request.args.get('category', '')
    
    # 构建完整搜索词
    search_term = keyword
    if category:
        search_term += f' {category}'
    
    results = []
    for sid, cfg in SOURCES.items():
        if source_filter and sid not in source_filter:
            continue
        
        search_tpl = cfg.get('search_url', '')
        if search_tpl:
            try:
                from urllib.parse import quote
                url = search_tpl.format(quote(search_term))
            except:
                url = search_tpl.format(search_term.replace(' ', '+'))
            
            results.append({
                'source': sid,
                'name': cfg.get('name', sid),
                'icon': cfg.get('icon', ''),
                'url': url,
            })
    
    return jsonify({
        'code': 0,
        'data': {
            'keyword': search_term,
            'results': results,
        }
    })


@app.route('/api/news/<int:item_id>/related')
def get_related_news(item_id):
    """获取相关推荐（同分类或同标签的其他文章）"""
    data = load_data()
    target = None
    for item in data:
        if item.get('id') == item_id:
            target = item
            break
    
    if not target:
        return jsonify({'code': 404, 'message': 'Not found'}), 404
    
    target_cat = target.get('category', '')
    target_tags = set(target.get('tags', []))
    
    related = []
    for item in data:
        if item.get('id') == item_id:
            continue
        
        score = 0
        if item.get('category') == target_cat:
            score += 3
        common_tags = target_tags & set(item.get('tags', []))
        score += len(common_tags) * 2
        if item.get('source') == target.get('source'):
            score += 1
        
        if score > 0:
            related.append({**item, '_relevanceScore': score})
    
    # 按相关度排序，取前6条
    related.sort(key=lambda x: x.pop('_relevanceScore', 0), reverse=True)
    
    return jsonify({'code': 0, 'data': related[:6]})


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """刷新数据缓存（重新从文件加载）"""
    clear_cache()
    data = load_data(force=True)
    stats = get_stats()
    return jsonify({
        'code': 0,
        'message': f'Data refreshed, {len(data)} items loaded',
        'data': {'count': len(data), 'timestamp': datetime.now().isoformat()}
    })


# ============================================================
# 错误处理
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'code': 404, 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f'Server error: {e}')
    return jsonify({'code': 500, 'message': 'Internal server error'}), 500


# ============================================================
# 启动入口
# ============================================================

if __name__ == '__main__':
    print('\n' + '=' * 60)
    print('  ADADD 广告行业资讯聚合平台 - 后端服务')
    print('  Version 2.0.0')
    print('=' * 60)
    
    # 预加载数据
    print('\n📂 正在加载数据...')
    data = load_data()
    stats = get_stats()
    
    print(f'\n📊 数据概览:')
    print(f'   总计: {stats["total"]} 条资讯')
    print(f'   来源: {len(stats["sources"])} 个平台')
    print(f'   分类: {len(stats["categories"])} 个分类')
    print(f'   年份: {len(stats["years"])}年 ({min(stats["years"].keys())}-{max(stats["years"].keys())})')
    print(f'\n🚀 服务启动中...')
    print(f'   地址: http://{FLASK_HOST}:{FLASK_PORT}')
    print(f'   API文档: http://{FLASK_HOST}:{FLASK_PORT}/api/health')
    print(f'   前端页面: http://{FLASK_HOST}:{FLASK_PORT}/')
    print('=' * 60 + '\n')
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
