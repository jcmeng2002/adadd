#!/usr/bin/env python3
"""ADADD V5 - 一次性修复所有Bug的完整前端生成器"""

import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, 'data', 'news_data.json')
OUT = os.path.join(BASE, 'index.html')

# Load data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = json.load(f)
items = raw.get('items', raw) if isinstance(raw, dict) else raw
if not isinstance(items, list):
    items = []

# Build indexes
sources = {}
categories = {}
years = set()
for item in items:
    s = item.get('source', '')
    c = item.get('category', '')
    d = item.get('date', '')[:4]
    sources[s] = sources.get(s, 0) + 1
    categories[c] = categories.get(c, 0) + 1
    if d: years.add(d)

year_list = sorted(years, reverse=True)
source_list = sorted(sources.items(), key=lambda x: -x[1])
cat_list = sorted(categories.items(), key=lambda x: -x[1])

print(f"Data loaded: {len(items)} items, {len(years)} years, {len(source_list)} sources, {len(cat_list)} categories")

# ============================================================
# HTML Template
# ============================================================
html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>ADADD · 广告行业资讯聚合平台</title>
    <!-- 腾讯体本地字体 -->
    <style>@font-face{font-family:'Tencent Sans';src:url('./fonts/TencentSans-W7.otf') format('opentype');font-weight:400 900;font-style:normal;font-display:swap;}</style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
:root{--primary:#0052D9;--primary-light:#E8F0FE;--primary-dark:#1a3c6e;--primary-hover:#2670F0;--accent:#00A870;--warning:#ED7B2D;--danger:#E02020;--text-primary:#1a1a1a;--text-secondary:#666666;--text-tertiary:#999999;--border-color:#e5e5e5;--bg-body:#f5f7fa;--bg-white:#ffffff;--shadow-sm:0 1px 3px rgba(0,0,0,.06);--shadow-md:0 4px 12px rgba(0,0,0,.08);--shadow-lg:0 8px 30px rgba(0,0,0,.12);--radius-sm:6px;--radius-md:10px;--radius-lg:16px;--font-family:"Tencent Sans","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{font-family:var(--font-family);background:var(--bg-body);color:var(--text-primary);line-height:1.6;min-height:100vh}
a{color:var(--primary);text-decoration:none}button{cursor:pointer;font-family:inherit;border:none;background:none}input,select{font-family:inherit}

/* Navbar */
.navbar{position:sticky;top:0;z-index:100;background:var(--bg-white);border-bottom:1px solid var(--border-color);box-shadow:var(--shadow-sm)}
.navbar-inner{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:20px;padding:12px 24px}
.logo{display:flex;align-items:baseline;gap:8px;flex-shrink:0}
.logo-icon{font-size:24px;color:var(--primary)}
.logo-text{font-size:22px;font-weight:900;color:var(--primary);letter-spacing:2px;font-family:"Tencent Sans",sans-serif}
.logo-sub{font-size:11px;color:var(--text-tertiary);padding-left:8px;border-left:1px solid var(--border-color)}
.navbar-center{flex:1;max-width:480px}
.search-bar{display:flex;align-items:center;background:var(--bg-body);border-radius:20px;padding:8px 16px;gap:8px;transition:all .25s ease;border:1.5px solid transparent}
.search-bar:focus-within{background:var(--bg-white);border-color:var(--primary);box-shadow:0 0 0 3px rgba(0,82,217,.08)}
.search-bar svg{flex-shrink:0;opacity:.5}
.search-bar input{flex:1;border:none;outline:none;background:transparent;font-size:14px;color:var(--text-primary)}
.clear-search{width:18px;height:18px;border-radius:50%;display:none;align-items:center;justify-content:center;font-size:14px;color:var(--text-tertiary);background:#ddd}
.navbar-right{display:flex;align-items:center;gap:10px;flex-shrink:0}
.year-select{padding:6px 12px;border-radius:var(--radius-sm);border:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);background:var(--bg-white);cursor:pointer}
.refresh-btn{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--text-secondary);transition:all .25s}
.refresh-btn:hover{color:var(--primary);background:var(--primary-light)}
.refresh-btn.spinning svg{animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* Filter Bar - V5: 所有筛选项统一带标签 */
.filter-bar{max-width:1400px;margin:0 auto;padding:20px 24px 0}
.filter-row{margin-bottom:14px}
.filter-label{font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:10px;display:block}
.filter-group{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.filter-btns,.cat-btns,.impact-filters,.sort-options,.view-toggle{display:flex;flex-wrap:wrap;gap:6px}
.filter-btn{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;font-size:13px;color:var(--text-secondary);background:var(--bg-white);border:1px solid var(--border-color);transition:all .2s ease;white-space:nowrap}
.filter-btn .count{font-size:11px;background:var(--bg-body);padding:1px 7px;border-radius:10px;color:var(--text-tertiary)}
.filter-btn:hover{border-color:var(--primary);color:var(--primary)}
.filter-btn.active{background:var(--primary);color:white;border-color:var(--primary);box-shadow:0 2px 8px rgba(0,82,217,.25)}
.filter-btn.active .count{background:rgba(255,255,255,.2);color:rgba(255,255,255,.85)}
.cat-btn{padding:4px 12px;border-radius:16px;font-size:12px;color:var(--text-secondary);background:var(--bg-white);border:1px solid var(--border-color);transition:all .2s;white-space:nowrap}
.cat-btn .count{font-size:10px;color:var(--text-tertiary)}
.cat-btn:hover{border-color:var(--primary-hover);color:var(--primary-hover)}
.cat-btn.active{background:linear-gradient(135deg,var(--primary),#2670F0);color:white;border-color:transparent}
.impact-filter-btn,.sort-btn{padding:4px 12px;border-radius:14px;font-size:12px;color:var(--text-secondary);background:var(--bg-white);border:1px solid var(--border-color);transition:all .2s}
.impact-filter-btn:hover,.sort-btn:hover{border-color:var(--primary-hover)}
.impact-filter-btn.active{background:var(--primary-light);color:var(--primary);border-color:var(--primary);font-weight:600}
.sort-btn.active{color:var(--primary);border-color:var(--primary);background:var(--primary-light);font-weight:500}
.view-toggle{display:flex;gap:2px;background:var(--bg-body);border-radius:var(--radius-sm);padding:2px}
.toggle-btn{padding:5px 14px;border-radius:6px;font-size:12px;color:var(--text-secondary);transition:all .2s}
.toggle-btn:hover{color:var(--text-primary)}
.toggle-btn.active{background:var(--bg-white);color:var(--primary);box-shadow:var(--shadow-sm);font-weight:600}

/* Stats */
.stats-bar{max-width:1400px;margin:0 auto;padding:0 24px;display:flex;align-items:center;gap:0;background:linear-gradient(135deg,#fff 0%,#f0f5ff 100%);border-radius:var(--radius-md);padding:18px 28px;margin-bottom:20px;border:1px solid rgba(0,82,217,.08);box-shadow:var(--shadow-sm)}
.stat-item{text-align:center;flex:1}
.stat-number{font-size:26px;font-weight:900;color:var(--primary);line-height:1.2;letter-spacing:-.5px}
.stat-number.highlight{color:var(--danger)}
.stat-label{font-size:12px;color:var(--text-tertiary);margin-top:2px}
.stat-divider{width:1px;height:40px;background:var(--border-color);margin:0 16px}

/* News Grid */
.news-section{max-width:1400px;margin:0 auto;padding:0 24px 60px}
.news-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:20px}

/* News Card */
.news-card{background:var(--bg-white);border-radius:var(--radius-md);padding:24px;border:1px solid var(--border-color);cursor:pointer;transition:all .3s ease;display:flex;flex-direction:column;position:relative;overflow:hidden}
.news-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--primary-hover));opacity:0;transition:opacity .3s}
.news-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:transparent}
.news-card:hover::before{opacity:1}
.card-header{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.news-source{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:500;padding:3px 10px;border-radius:12px;white-space:nowrap}
.news-date{font-size:12px;color:var(--text-tertiary);flex:1}
.impact-badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;white-space:nowrap}
.card-title{font-size:17px;font-weight:700;line-height:1.45;color:var(--text-primary);margin-bottom:10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .2s}
.news-card:hover .card-title{color:var(--primary)}
.card-summary{font-size:14px;line-height:1.65;color:var(--text-secondary);margin-bottom:14px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
.tag{font-size:11px;padding:3px 10px;border-radius:12px;background:var(--bg-body);color:var(--text-secondary);border:1px solid var(--border-color);transition:all .2s;white-space:nowrap}
.tag:hover{background:var(--primary-light);color:var(--primary);border-color:var(--primary)}
.card-footer{display:flex;justify-content:space-between;align-items:center;padding-top:14px;border-top:1px solid #f0f0f0}
.category-tag{font-size:12px;color:var(--primary);background:var(--primary-light);padding:3px 10px;border-radius:10px;font-weight:500}
.read-more,.visit-link{font-size:13px;color:var(--primary-hover);font-weight:500;opacity:0;transition:opacity .2s}
.news-card:hover .read-more,.news-card:hover .visit-link{opacity:1}
.visit-link{color:var(--accent)!important}

/* Timeline */
.timeline-group{margin-bottom:32px}
.timeline-year{font-size:22px;font-weight:900;color:var(--primary);margin-bottom:20px;padding-left:16px;border-left:4px solid var(--primary);letter-spacing:1px}
.timeline-items{display:flex;flex-direction:column;gap:12px}
.timeline-item{display:flex;gap:16px;background:var(--bg-white);border-radius:var(--radius-md);padding:20px 24px;border:1px solid var(--border-color);cursor:pointer;transition:all .25s}
.timeline-item:hover{transform:translateX(4px);box-shadow:var(--shadow-md);border-color:var(--primary-hover)}
.timeline-dot{width:12px;height:12px;border-radius:50%;margin-top:6px;flex-shrink:0;box-shadow:0 0 0 3px rgba(0,82,217,.15)}
.timeline-content{flex:1;min-width:0}
.timeline-meta{display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:12px;color:var(--text-tertiary)}
.timeline-item h4{font-size:16px;font-weight:700;line-height:1.4;color:var(--text-primary);margin-bottom:6px;transition:color .2s}
.timeline-item:hover h4{color:var(--primary)}
.timeline-item>p{font-size:14px;color:var(--text-secondary);line-height:1.55;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* Loading */
.loading-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 20px;text-align:center}
.spinner{width:40px;height:40px;border:3px solid var(--primary-light);border-top:3px solid var(--primary);border-radius:50%;animation:spin .8s linear infinite;margin-bottom:16px}

/* Empty */
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 20px;text-align:center}
.empty-state p{font-size:16px;color:var(--text-secondary);margin-top:16px}
.empty-hint{font-size:13px!important;color:var(--text-tertiary)!important;margin-top:8px!important}

/* Pagination */
.pagination{display:flex;justify-content:center;margin-top:32px}
.pagination-inner{display:flex;align-items:center;gap:4px}
.page-btn{min-width:38px;height:38px;border-radius:var(--radius-sm);font-size:13px;font-weight:500;color:var(--text-secondary);background:var(--bg-white);border:1px solid var(--border-color);display:flex;align-items:center;justify-content:center;padding:0 12px;transition:all .2s}
.page-btn:hover:not(:disabled){border-color:var(--primary);color:var(--primary)}
.page-btn.active{background:var(--primary);color:white;border-color:var(--primary);box-shadow:0 2px 8px rgba(0,82,217,.25)}
.page-btn:disabled{opacity:.35;cursor:not-allowed}
.page-dots{color:var(--text-tertiary);padding:0 6px;font-size:13px}

/* Modal */
.modal-overlay{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,.45);backdrop-filter:blur(4px);display:none;align-items:flex-start;justify-content:center;overflow-y:auto;padding:40px 20px}
.modal-overlay.show{display:flex;animation:fadeIn .25s ease}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-dialog{background:var(--bg-white);border-radius:var(--radius-lg);max-width:720px;width:100%;position:relative;box-shadow:0 20px 60px rgba(0,0,0,.2);animation:slideUp .3s ease;margin:auto}
@keyframes slideUp{from{transform:translateY(30px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-close{position:absolute;top:16px;right:16px;z-index:5;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--text-tertiary);background:var(--bg-body);transition:all .2s}
.modal-close:hover{background:var(--danger);color:white}
.modal-body-content{padding:36px 36px 28px}
.detail-header{margin-bottom:24px}
.detail-meta-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.news-source.large{font-size:13px;padding:4px 12px}
.impact-badge.large{font-size:12px;padding:3px 10px}
.category-tag.large{font-size:13px;padding:4px 12px}
.detail-date{font-size:13px;color:var(--text-tertiary);display:block;margin-bottom:10px}
.detail-title{font-size:24px;font-weight:900;line-height:1.35;color:var(--text-primary);margin-bottom:12px;font-family:"Tencent Sans",sans-serif}
.detail-summary{font-size:16px;color:var(--text-secondary);line-height:1.6}
.detail-body{margin-bottom:20px}
.detail-body p{font-size:15px;line-height:1.85;color:var(--text-primary);white-space:pre-line}
.detail-tags{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;padding-top:16px;border-top:1px solid var(--border-color)}
.detail-actions{display:flex;gap:12px;justify-content:flex-end}
.action-btn{padding:10px 24px;border-radius:var(--radius-sm);font-size:14px;font-weight:600;transition:all .2s}
.action-btn.primary{background:var(--primary);color:white}
.action-btn.primary:hover{background:var(--primary-hover);box-shadow:0 4px 12px rgba(0,82,217,.3)}
.action-btn.secondary{background:var(--bg-body);color:var(--text-secondary);border:1px solid var(--border-color)}
.action-btn.secondary:hover{background:var(--border-color)}
.visit-original-btn{background:var(--accent)!important;color:white!important}
.visit-original-btn:hover{background:#00915e!important}

/* Toast & Update */
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--text-primary);color:white;padding:12px 28px;border-radius:24px;font-size:14px;font-weight:500;z-index:2000;opacity:0;pointer-events:none;transition:all .3s ease;box-shadow:var(--shadow-lg)}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.update-notification{position:fixed;top:76px;left:50%;transform:translateX(-50%) translateY(-20px);background:linear-gradient(135deg,var(--primary),var(--primary-hover));color:white;padding:10px 24px;border-radius:24px;font-size:13px;font-weight:500;z-index:99;display:none;align-items:center;gap:12px;box-shadow:0 4px 16px rgba(0,82,217,.3);opacity:0;transition:all .35s ease}
.update-notification.show{display:flex;opacity:1;transform:translateX(-50%) translateY(0)}
.update-notification button{background:rgba(255,255,255,.2);color:white;width:22px;height:22px;border-radius:50%;font-size:14px;display:flex;align-items:center;justify-content:center}

.api-status{display:inline-flex;align-items:center;gap:4px;font-size:11px;padding:2px 8px;border-radius:10px;transition:all .2s}
.api-status.connected{background:#e6ffe6;color:var(--accent)}
.api-status.disconnected{background:#ffe6e6;color:var(--danger)}
.api-dot{width:6px;height:6px;border-radius:50%;background:currentColor}

/* Footer */
.footer{background:var(--text-primary);color:rgba(255,255,255,.6);padding:24px;text-align:center;font-size:13px;margin-top:auto}
.footer-inner{max-width:1400px;margin:0 auto;display:flex;justify-content:center;flex-wrap:wrap;gap:8px;align-items:center}
.footer strong{color:white}
.footer .divider{opacity:.3}

@media(max-width:1024px){
    .news-grid{grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
    .navbar-inner{flex-wrap:wrap;gap:12px;padding:10px 20px}
    .navbar-center{order:3;max-width:100%;flex-basis:100%}
    .search-bar{width:100%}
}
@media(max-width:768px){
    .news-grid{grid-template-columns:1fr}
    .filter-row{gap:12px}
    .stats-bar{flex-direction:column;gap:12px;padding:16px}
    .stat-divider{display:none}
    .modal-dialog{margin:10px;max-width:none}
    .modal-body-content{padding:24px 20px}
    .detail-title{font-size:20px}
    .footer-inner{flex-direction:column;gap:6px}
    .footer .divider{display:none}
    .card-footer{flex-direction:column;align-items:flex-start;gap:8px}
    .read-more,.visit-link{opacity:1!important}
}
    </style>
</head>
<body>

<!-- Navbar -->
<header class="navbar">
    <div class="navbar-inner">
        <div class="logo">
            <span class="logo-icon">📊</span>
            <span class="logo-text">ADADD</span>
            <span class="logo-sub">广告资讯聚合</span>
        </div>
        <div class="navbar-center">
            <div class="search-bar" id="searchBar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                <input type="text" id="searchInput" placeholder="搜索广告行业资讯、技术、趋势..." autocomplete="off">
                <button class="clear-search" id="clearSearch">&times;</button>
                <button onclick="{const q=document.getElementById('searchInput').value.trim();if(q){window.open('https://www.google.com/search?q='+encodeURIComponent(q+' 广告 行业')+'&tbs=qdr:m','_blank');}}" style="padding:4px 12px;border-radius:14px;font-size:11px;color:#00A870;background:#EDFAF3;border:1px solid #00A870;cursor:pointer;white-space:nowrap;font-weight:500;" title="跳转Google全网实时搜索">全网搜 🔍</button>
            </div>
        </div>
        <div class="navbar-right">
            <select class="year-select" id="yearFilter">
                <option value="">全部年份</option>
'''

# 动态生成年份选项（从数据中获取）
for y in year_list:
    html += f'                <option value="{y}">{y}年</option>\n'

html += '''            </select>
            <button class="refresh-btn" id="refreshBtn" title="刷新数据">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.22-8.56"/><path d="M21 3v5h-5"/></svg>
            </button>
            <div class="api-status connected" id="apiStatus"><span class="api-dot"></span><span id="apiStatusText">API已连接</span></div>
        </div>
    </div>
</header>

<!-- Filter Bar - 统一布局：每个筛选都有label -->
<section class="filter-bar">
    <div class="filter-row">
        <span class="filter-label">📌 来源：</span>
        <div class="filter-group filter-btns" id="sourceFilters"></div>
    </div>
    <div class="filter-row">
        <span class="filter-label">📂 分类：</span>
        <div class="filter-group cat-btns" id="catFilters"></div>
    </div>
    <div class="filter-row">
        <span class="filter-label">⚡ 影响力：</span>
        <div class="filter-group impact-filters" id="impactFilters"></div>
        <span class="filter-label" style="margin-left:24px;">🔄 排序：</span>
        <div class="filter-group sort-options" id="sortOptions"></div>
        <span class="filter-label" style="margin-left:24px;">👁 展示形式：</span>
        <div class="filter-group view-toggle" id="viewToggle"></div>
    </div>
</section>

<!-- Stats Bar -->
<div class="stats-bar" id="statsBar"></div>

<!-- News Section -->
<main class="news-section">
    <div id="loadingState" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载最新资讯...</p>
        <p class="empty-hint">从后端服务器获取全量数据中</p>
    </div>
    <div class="news-grid" id="newsGrid" style="display:none;"></div>
    <div id="timelineView" style="display:none;"></div>
    <div id="emptyState" class="empty-state" style="display:none;">
        <p style="font-size:48px;">🔍</p>
        <p>没有找到匹配的资讯</p>
        <p class="empty-hint">尝试调整筛选条件或使用全网搜索</p>
    </div>
    <div class="pagination" id="pagination"></div>
</main>

<!-- Modal -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal-dialog">
        <button class="modal-close" id="modalClose">&times;</button>
        <div class="modal-body-content" id="modalContent"></div>
    </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- Update Notification -->
<div class="update-notification" id="updateNotif">
    🔄 发现新数据！点击刷新查看最新资讯
    <button onclick="this.parentElement.style.display='none'">&times;</button>
</div>

<!-- Footer -->
<footer class="footer">
    <div class="footer-inner">
        <strong>ADADD</strong><span class="divider">·</span>
        <span>广告行业资讯聚合平台</span><span class="divider">|</span>
        <span>Powered by Flask API + Tencent Blue</span><span class="divider">|</span>
        <span>Developed with ❤️ by nelsonmeng</span>
    </div>
</footer>

<script>
// ============================================================
// ADADD V5 - 完全修复版（来源/分类/影响力/视图/年份/链接）
// ============================================================

const API_BASE = (location.hostname==='localhost'||location.hostname==='127.0.0.1')
    ? 'http://localhost:5000/api' : '/api';

// Source config
const SOURCE_CONFIG = {
    weibo:{name:'微博',icon:'📱',color:'#E6162D'},
    zhihu:{name:'知乎',icon:'💡',color:'#0084FF'},
    wechat:{name:'微信公众号',icon:'📨',color:'#07C160'},
    github:{name:'GitHub',icon:'🐙',color:'#24292E'},
    'tech-media':{name:'技术社区',icon:'⚙️',color:'#ED7B2D'},
    'industry-media':{name:'行业媒体',icon:'📰',color:'#0052D9'},
    '36kr':{name:'36氪',icon:'🚀',color:'#0066CC'}
};

const IMPACT_CONFIG = {
    high:{label:'高影响力',color:'#E02020',bgColor:'#FFF0F0'},
    medium:{label:'中影响力',color:'#ED7B2D',bgColor:'#FFF7ED'},
    low:{label:'一般关注',color:'#00A870',bgColor:'#EDFAF3'}
};

let state={
    allData:[],filteredData:[],
    sources:{},categories:{},years:new Set(),
    stats:{total:0,highImpact:0,todayCount:0},
    filters:{source:'',category:'',impact:'',year:''},
    searchQuery:'',sortBy:'date-desc',viewMode:'cards',
    currentPage:1,pageSize:12,
    loading:true,apiConnected:false,lastFetchTime:null
};

// ==================== API Layer ====================
async function apiGet(ep){
    try{
        const r=await fetch(API_BASE+ep);
        if(!r.ok) throw new Error('HTTP '+r.status);
        const j=await r.json();
        if(j.code!==0) throw new Error(j.message||'?');
        return j.data;
    }catch(e){
        console.error('API Error:',e.message);
        updateApiStatus(false);
        return null;
    }
}

async function loadAllData(){
    state.loading=true;showLoading(true);
    const [nd,st]=await Promise.all([apiGet('/news?size=10000'),apiGet('/stats')]);
    if(nd&&Array.isArray(nd.items)){
        state.allData=nd.items;state.apiConnected=true;
        if(st) state.stats=st;
        buildIndexes();
        updateApiStatus(true);
    }else{
        state.apiConnected=false;updateApiStatus(false);
    }
    state.loading=false;showLoading(false);
    renderAll();
}

function buildIndexes(){
    state.sources={};state.categories={};state.years=new Set();
    state.allData.forEach(it=>{
        if(!state.sources[it.source]) state.sources[it.source]=0;
        state.sources[it.source]++;
        if(!state.categories[it.category]) state.categories[it.category]=0;
        state.categories[it.category]++;
        const y=(it.date||'').substring(0,4);
        if(y) state.years.add(y);
    });
    // 年份选择器已在HTML中静态生成，无需再填充
}

function updateApiStatus(ok){
    const el=document.getElementById('apiStatus');
    const tx=document.getElementById('apiStatusText');
    if(!el)return;
    el.className='api-status '+(ok?'connected':'disconnected');
    if(tx)tx.textContent=ok?'API已连接':'API离线';
}

// ==================== Search URL Generator ====================
const SEARCH_TPL={
    weibo:'https://s.weibo.com/weibo?q={q}&typeall=1',
    zhihu:'https://www.zhihu.com/search?type=content&q={q}',
    wechat:'https://weixin.sogou.com/weixin?type=2&query={q}',
    github:'https://github.com/search?q={q}',
    'tech-media':'https://juejin.cn/search?query={q}',
    'industry-media':'https://www.google.com/search?q={q}',
    '36kr':'https://36kr.com/search/articles/{q}'
};

function getNewsUrl(item){
    // 用标题构建Google搜索URL，保证一定能搜到结果
    const q=encodeURIComponent(item.title||item.category+' 广告');
    return 'https://www.google.com/search?q='+q+'&tbs=qdr:y';
}

// ==================== Filtering ====================
function applyFilters(){
    let data=[...state.allData];
    const f=state.filters;
    if(f.source) data=data.filter(d=>d.source===f.source);
    if(f.category) data=data.filter(d=>d.category===f.category);
    if(f.impact) data=data.filter(d=>d.impact===f.impact);
    if(f.year) data=data.filter(d=>d.date&&d.date.startsWith(f.year));
    if(state.searchQuery.trim()){
        const q=state.searchQuery.toLowerCase().trim();
        data=data.filter(d=>
            (d.title||'').toLowerCase().includes(q)||
            (d.summary||'').toLowerCase().includes(q)||
            (d.tags||[]).some(t=>t.toLowerCase().includes(q))
        );
    }
    switch(state.sortBy){
        case'date-desc':data.sort((a,b)=>(b.date||'').localeCompare(a.date||''));break;
        case'date-asc':data.sort((a,b)=>(a.date||'').localeCompare(b.date||''));break;
        case'impact-desc':const m={high:3,medium:2,low:1};
            data.sort((a,b)=>(m[b.impact]||0)-(m[a.impact]||0));break;
    }
    state.filteredData=data;state.currentPage=1;
}

function getPaginated(){
    const s=(state.currentPage-1)*state.pageSize;
    return state.filteredData.slice(s,s+state.pageSize);
}
function totalPages(){return Math.max(1,Math.ceil(state.filteredData.length/state.pageSize));}

// ==================== Rendering ====================
function renderAll(){
    applyFilters();
    renderSources();renderCategories();renderStats();
    renderImpactFilters();renderSortOptions();renderViewToggle();
    renderNews();renderPagination();
    bindCardEvents();
}

function renderSources(){
    const c=document.getElementById('sourceFilters');
    let h='<button class="filter-btn'+(state.filters.source===''?' active':'')+'" data-src="">全部<span class="count">'+state.allData.length+'</span></button>';
    for(const[k,v]of Object.entries(state.sources).sort((a,b)=>b[1]-a[1])){
        const cfg=SOURCE_CONFIG[k]||{name:k,icon:'📌',color:'#999'};
        h+='<button class="filter-btn'+(state.filters.source===k?' active':'')+'" data-src="'+k+'">'+cfg.icon+' '+cfg.name+'<span class="count">'+v+'</span></button>';
    }
    c.innerHTML=h;
}
function renderCategories(){
    const c=document.getElementById('catFilters');
    let h='<button class="cat-btn active" data-cat="">全部</button>';
    for(const[ct,v]of Object.entries(state.categories).sort((a,b)=>b[1]-a[1])){
        h+='<button class="cat-btn'+(state.filters.category===ct?' active':'')+'" data-cat="'+escHtml(ct)+'">'+escHtml(ct)+'<span class="count">('+v+')</span></button>';
    }
    c.innerHTML=h;
}

// ★ V5修复：影响力/排序/视图的渲染和事件绑定
function renderImpactFilters(){
    const c=document.getElementById('impactFilters');
    const items=[
        {k:'',l:'全部影响力'},
        {k:'high',l:'高影响力'},
        {k:'medium',l:'中影响力'},
        {k:'low',l:'一般关注'}
    ];
    let h='';
    items.forEach(({k,l})=>{
        const cls=k==''&&state.filters.impact==''?'active':
              k!==''&&state.filters.impact===k?'active':'';
        h+='<button class="impact-filter-btn '+cls+'" data-imp="'+k+'">'+l+'</button>';
    });
    c.innerHTML=h;
}
function renderSortOptions(){
    const c=document.getElementById('sortOptions');
    const items=[
        {k:'date-desc',l:'最新优先'},
        {k:'date-asc',l:'最早优先'},
        {k:'impact-desc',l:'高影响力优先'}
    ];
    let h='';
    items.forEach(({k,l})=>{
        h+='<button class="sort-btn'+(state.sortBy===k?' active':'')+'" data-srt="'+k+'">'+l+'</button>';
    });
    c.innerHTML=h;
}
function renderViewToggle(){
    const c=document.getElementById('viewToggle');
    const items=[
        {k:'cards',l:'📋 卡片'},
        {k:'timeline',l:'📅 时间轴'}
    ];
    let h='';
    items.forEach(({k,l})=>{
        h+='<button class="toggle-btn'+(state.viewMode===k?' active':'')+'" data-vw="'+k+'">'+l+'</button>';
    });
    c.innerHTML=h;
}

function renderStats(){
    const s=state.stats;
    document.getElementById('statsBar').innerHTML=
        '<div class="stat-item"><div class="stat-number">'+(s.total||state.allData.length)+'</div><div class="stat-label">总资讯数</div></div>'+
        '<div class="stat-divider"></div>'+
        '<div class="stat-item"><div class="stat-number highlight">'+state.years.size+'</div><div class="stat-label">覆盖年数</div></div>'+
        '<div class="stat-divider"></div>'+
        '<div class="stat-item"><div class="stat-number">'+Object.keys(state.categories).length+'</div><div class="stat-label">分类数量</div></div>'+
        '<div class="stat-divider"></div>'+
        '<div class="stat-item"><div class="stat-number">'+Object.keys(state.sources).length+'</div><div class="stat-label">数据源</div></div>';
}

function renderNews(){
    const its=getPaginated();
    const g=document.getElementById('newsGrid');
    const t=document.getElementById('timelineView');
    const e=document.getElementById('emptyState');
    g.style.display='none';t.style.display='none';e.style.display='none';
    if(!its.length){e.style.display='flex';return;}
    if(state.viewMode==='cards'){
        g.style.display='grid';g.innerHTML=its.map(renderCard).join('');
    }else{
        t.style.display='block';t.innerHTML=renderTimeline(its);
    }
}

function renderCard(item){
    const s=SOURCE_CONFIG[item.source]||{name:item.source,icon:'📌',color:'#999'};
    const im=IMPACT_CONFIG[item.impact]||IMPACT_CONFIG.low;
    const url=getNewsUrl(item);
    return '<article class="news-card" data-id="'+item.id+'">'+
        '<div class="card-header">'+
            '<span class="news-source" style="background:'+s.color+'18;color:'+s.color+'">'+s.icon+' '+s.name+'</span>'+
            '<span class="news-date">'+item.date+'</span>'+
            '<span class="impact-badge" style="background:'+im.bgColor+';color:'+im.color+'">'+im.label+'</span>'+
        '</div>'+
        '<h3 class="card-title">'+escHtml(item.title)+'</h3>'+
        '<p class="card-summary">'+escHtml(item.summary)+'</p>'+
        '<div class="card-tags">'+(item.tags||[]).map(t=>'<span class="tag">'+escHtml(t)+'</span>').join('')+'</div>'+
        '<div class="card-footer">'+
            '<span class="category-tag">'+escHtml(item.category)+'</span>'+
            '<a href="'+url+'" target="_blank" rel="noopener" class="visit-link" onclick="event.stopPropagation()">访问原文 ↗</a>'+
        '</div>'+
    '</article>';
}

function renderTimeline(items){
    const gr={};
    items.forEach(it=>{
        const y=(it.date||'').substring(0,4);
        if(!gr[y])gr[y]=[];
        gr[y].push(it);
    });
    let h='';
    Object.keys(gr).sort().reverse().forEach(y=>{
        h+='<div class="timeline-group"><h3 class="timeline-year">'+y+'年</h3><div class="timeline-items">';
        gr[y].forEach(it=>{
            const s=SOURCE_CONFIG[it.source]||{name:it.source,icon:'📌',color:'#999'};
            h+='<div class="timeline-item" data-id="'+it.id+'">'+
                '<div class="timeline-dot" style="background:'+s.color+'"></div>'+
                '<div class="timeline-content">'+
                    '<div class="timeline-meta">'+
                        '<span class="news-source" style="background:'+s.color+'18;color:'+s.color+'">'+s.icon+' '+s.name+'</span>'+
                        '<span>'+it.date+'</span>'+
                    '</div>'+
                    '<h4>'+escHtml(it.title)+'</h4>'+
                    '<p>'+escHtml(it.summary)+'</p>'+
                '</div></div>';
        });
        h+='</div></div>';
    });
    return h;
}

function renderPagination(){
    const tp=totalPages(),cp=state.currentPage;
    const c=document.getElementById('pagination');
    if(tp<=1){c.innerHTML='';return;}
    let h='<div class="pagination-inner">';
    h+='<button class="page-btn'+(cp<=1?' disabled':'')+'" data-p="'+(cp-1)+'">&lsaquo; 上一页</button>';
    if(tp<=7)for(let i=1;i<=tp;i++)h+=btn(i,i,cp);
    else{h+=btn(1,1,cp);if(cp>3)h+='<span class="page-dots">...</span>';
    for(let i=Math.max(2,cp-1);i<=Math.min(tp-1,cp+1);i++)h+=btn(i,i,cp);
    if(cp<tp-2)h+='<span class="page-dots">...</span>';h+=btn(tp,tp,cp);}
    h+='<button class="page-btn'+(cp>=tp?' disabled':'')+'" data-p="'+(cp+1)+'">下一页 &rsaquo;</button>';
    h+='</div>';c.innerHTML=h;
    c.querySelectorAll('.page-btn:not(.disabled)').forEach(b=>{
        b.addEventListener('click',()=>{state.currentPage=+b.dataset.p;renderNews();renderPagination();});
    });
}
function btn(v,l,cp){return'<button class="page-btn'+(v===cp?' active':'')+'" data-p="'+v+'">'+l+'</button>';}

// ==================== Modal ====================
function openDetail(id){
    const it=state.allData.find(d=>d.id==id);if(!it)return;
    const s=SOURCE_CONFIG[it.source]||{name:it.source,icon:'📌',color:'#999'};
    const im=IMPACT_CONFIG[it.impact]||IMPACT_CONFIG.low;
    const url=getNewsUrl(it);
    document.getElementById('modalContent').innerHTML=
        '<div class="detail-header">'+
            '<div class="detail-meta-top">'+
                '<span class="news-source large" style="background:'+s.color+'18;color:'+s.color+'">'+s.icon+' '+s.name+'</span>'+
                '<span class="impact-badge large" style="background:'+im.bgColor+';color:'+im.color+'">'+im.label+'</span>'+
                '<span class="category-tag large">'+escHtml(it.category)+'</span>'+
            '</div>'+
            '<span class="detail-date">'+it.date+'</span>'+
            '<h2 class="detail-title">'+escHtml(it.title)+'</h2>'+
            '<p class="detail-summary">'+escHtml(it.summary)+'</p>'+
        '</div>'+
        '<div class="detail-body"><p>'+(it.body?escHtml(it.body):escHtml(it.summary))+'</p></div>'+
        '<div class="detail-tags">'+(it.tags||[]).map(t=>'<span class="tag">'+escHtml(t)+'</span>').join('')+'</div>'+
        '<div class="detail-actions">'+
            '<button class="action-btn visit-original-btn" onclick="window.open(\''+url+'\',\'_blank\')">访问原文 ↗</button>'+
            '<button class="action-btn secondary" onclick="shareArt(\''+escHtml(it.title).replace(/'/g,"\\'")+'\')">分享</button>'+
            '<button class="action-btn secondary" onclick="closeModal()">关闭</button>'+
        '</div>';
    document.getElementById('modalOverlay').classList.add('show');
    document.body.style.overflow='hidden';
}
function closeModal(){document.getElementById('modalOverlay').classList.remove('show');document.body.style.overflow='';}
function shareArticle(title){ /* alias */ shareArt(title); }
function shareArt(title){
    if(navigator.share)navigator.share({title:title,url:location.href});
    else{const t=document.createElement('textarea');t.value=title+' - ADADD 广告资讯聚合';
    document.body.appendChild(t);t.select();document.execCommand('copy');t.remove();showToast('✅ 已复制到剪贴板');}
}

// ==================== Events - ★ V5核心修复：统一事件委托 ====================
function bindCardEvents(){
    document.querySelectorAll('.news-card[data-id]').forEach(c=>{
        c.addEventListener('click',(e)=>{
            if(e.target.closest('.visit-link'))return;
            openDetail(c.dataset.id);
        });
    });
    document.querySelectorAll('.timeline-item[data-id]').forEach(t=>{
        t.addEventListener('click',()=>openDetail(t.dataset.id));
    });
}

function showLoading(show){document.getElementById('loadingState').style.display=show?'flex':'none';}
function escHtml(str){if(!str)return'';const d=document.createElement('div');d.textContent=str;return d.innerHTML;}
function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
    clearTimeout(t._timer);t._timer=setTimeout(()=>t.classList.remove('show'),2500);}

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded',async function(){

    // ★★★ V5 核心修复：所有交互用事件委托绑定到容器上 ★★★

    // 1. 来源筛选 - 事件委托
    document.getElementById('sourceFilters').addEventListener('click',function(e){
        const b=e.target.closest('.filter-btn[data-src]');
        if(!b)return;
        state.filters.source=b.dataset.src;
        this.querySelectorAll('.filter-btn').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        renderAll();
    });

    // 2. 分类筛选 - 事件委托
    document.getElementById('catFilters').addEventListener('click',function(e){
        const b=e.target.closest('.cat-btn[data-cat]');
        if(!b)return;
        state.filters.category=b.dataset.cat;
        this.querySelectorAll('.cat-btn').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        renderAll();
    });

    // 3. 影响力筛选 - 事件委托
    document.getElementById('impactFilters').addEventListener('click',function(e){
        const b=e.target.closest('.impact-filter-btn[data-imp]');
        if(!b)return;
        state.filters.impact=b.dataset.imp;
        this.querySelectorAll('.impact-filter-btn').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        renderAll();
    });

    // 4. 排序切换 - 事件委托
    document.getElementById('sortOptions').addEventListener('click',function(e){
        const b=e.target.closest('.sort-btn[data-srt]');
        if(!b)return;
        state.sortBy=b.dataset.srt;
        this.querySelectorAll('.sort-btn').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        renderAll();
    });

    // 5. 视图切换 - 事件委托
    document.getElementById('viewToggle').addEventListener('click',function(e){
        const b=e.target.closest('.toggle-btn[data-vw]');
        if(!b)return;
        state.viewMode=b.dataset.vw;
        this.querySelectorAll('.toggle-btn').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        renderAll();
    });

    // 6. 年份筛选 - select原生change事件
    document.getElementById('yearFilter').addEventListener('change',function(){
        state.filters.year=this.value;
        renderAll();
    });

    // 7. 搜索功能
    const si=document.getElementById('searchInput'),cb=document.getElementById('clearSearch');
    let st=null;
    si.addEventListener('input',()=>{
        cb.style.display=si.value.length?'flex':'none';
        clearTimeout(st);st=setTimeout(()=>{
            state.searchQuery=si.value;renderAll();
        },300);
    });
    si.addEventListener('keydown',e=>{
        if(e.key==='Enter'){
            e.preventDefault();
            const q=si.value.trim();
            if(q){
                state.searchQuery=q;renderAll();
                setTimeout(()=>{
                    if(state.filteredData.length===0&&q.trim()){
                        showToast('🔍 本地暂无相关结果，已为您打开全网实时搜索...');
                        window.open('https://www.google.com/search?q='+encodeURIComponent(q+' 广告 行业')+'&tbs=qdr:m','_blank');
                    }
                },400);
            }
        }
        if(e.key==='Escape'){si.value='';state.searchQuery='';cb.style.display='none';renderAll();}
    });
    cb.addEventListener('click',()=>{si.value='';state.searchQuery='';cb.style.display='none';si.focus();renderAll();});

    // 8. 刷新按钮
    document.getElementById('refreshBtn').addEventListener('click',function(){
        this.classList.add('spinning');
        loadAllData().then(()=>{this.classList.remove('spinning');showToast('✅ 数据已更新');});
    });

    // 9. Modal关闭
    document.getElementById('modalClose').addEventListener('click',closeModal);
    document.getElementById('modalOverlay').addEventListener('click',e=>{if(e.target===e.currentTarget)closeModal();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});

    // 10. 加载数据
    await loadAllData();

    console.log('[ADADD V5] Loaded '+state.allData.length+' items, '+state.years.size+' years, '+Object.keys(state.sources).length+' sources, '+Object.keys(state.categories).length+' categories');
});
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'✅ Generated index.html ({len(html)} bytes)')
print(f'   Path: {OUT}')
