/**
 * AdPulse - 广告行业资讯聚合平台
 * 核心交互逻辑：筛选、搜索、时间轴、详情展示
 */

// ===== 状态管理 =====
const state = {
    allData: [],           // 全量数据
    filteredData: [],      // 筛选后数据
    currentPage: 1,
    pageSize: 9,
    activeSource: 'all',   // 当前选中的来源筛选
    activeCategory: 'all', // 当前选中的分类筛选
    searchQuery: '',       // 搜索关键词
    activeImpact: 'all',   // 影响力筛选
    sortMode: 'date-desc', // 排序方式
    viewMode: 'card',      // 视图模式: card | timeline
    selectedNews: null,    // 当前查看详情的资讯
};

// ===== 来源配置 =====
const SOURCE_CONFIG = {
    weibo:     { name: '微博',        icon: '📱', color: '#FF8200' },
    zhihu:     { name: '知乎',        icon: '💡', color: '#0066CC' },
    wechat:    { name: '微信公众号',  icon: '📨', color: '#07C160' },
    github:    { name: 'GitHub',      icon: '🐙', color: '#181717' },
    'tech-media':{ name: '技术社区',   icon: '⚙️',  color: '#0052D9' },
    industry:  { name: '行业媒体',    icon: '📰', color: '#E02020' },
    '36kr':    { name: '36氪',        icon: '🚀', color: '#0066CC' },
};

const IMPACT_CONFIG = {
    high:   { label: '高影响', color: '#E02020', bg: '#FFF2F0' },
    medium: { label: '中影响', color: '#FA8C16', bg: '#FFF7E6' },
    normal: { label: '一般',   color: '#8C8C8C', bg: '#F5F5F5' },
};

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // 加载数据
    state.allData = [...AD_NEWS_DATA].sort((a, b) => new Date(b.date) - new Date(a.date));
    state.filteredData = [...state.allData];
    
    // 渲染UI
    renderSources();
    renderCategories();
    renderStats();
    renderNews();
    
    // 更新页脚总数
    const footerTotal = document.getElementById('footerTotal');
    if (footerTotal) footerTotal.textContent = state.allData.length;
    
    bindEvents();
    
    // 模拟自动更新提示
    showUpdateNotification();
}

// ===== 渲染来源筛选标签 =====
function renderSources() {
    const container = document.getElementById('sourceFilters');
    if (!container) return;
    
    const sources = ['all', ...Object.keys(SOURCE_CONFIG)];
    
    container.innerHTML = sources.map(src => {
        if (src === 'all') {
            return `<button class="filter-btn active" data-source="all">
                <span>全部来源</span>
                <span class="count">${state.allData.length}</span>
            </button>`;
        }
        const cfg = SOURCE_CONFIG[src];
        const count = state.allData.filter(n => n.source === src).length;
        return `<button class="filter-btn" data-source="${src}">
            <span>${cfg.icon} ${cfg.name}</span>
            <span class="count">${count}</span>
        </button>`;
    }).join('');
}

// ===== 渲染分类筛选 =====
function renderCategories() {
    const container = document.getElementById('categoryFilters');
    if (!container) return;
    
    const cats = ['all', ...new Set(state.allData.map(n => n.category))];
    
    container.innerHTML = cats.map(cat => {
        const count = cat === 'all' 
            ? state.allData.length 
            : state.allData.filter(n => n.category === cat).length;
        const isActive = cat === 'all' ? 'active' : '';
        return `<button class="cat-btn ${isActive}" data-category="${cat}">${cat === 'all' ? '全部分类' : cat}<span class="count">(${count})</span></button>`;
    }).join('');
}

// ===== 渲染统计信息 =====
function renderStats() {
    const el = document.getElementById('totalStats');
    if (!el) return;
    
    const total = state.filteredData.length;
    const highImpact = state.filteredData.filter(n => n.impact === 'high').length;
    const latestDate = state.filteredData.length > 0 
        ? state.filteredData[0].date 
        : '--';
    
    el.innerHTML = `
        <div class="stat-item">
            <div class="stat-number">${total}</div>
            <div class="stat-label">条资讯</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-number highlight">${highImpact}</div>
            <div class="stat-label">高影响力</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-number">${latestDate}</div>
            <div class="stat-label">最新更新</div>
        </div>
    `;
}

// ===== 渲染资讯卡片列表 =====
function renderNews() {
    const container = document.getElementById('newsList');
    const emptyState = document.getElementById('emptyState');
    
    if (state.filteredData.length === 0) {
        container.innerHTML = '';
        emptyState.style.display = 'flex';
        renderPagination(0);
        return;
    }
    
    emptyState.style.display = 'none';
    
    // 分页
    const total = state.filteredData.length;
    const totalPages = Math.ceil(total / state.pageSize);
    const start = (state.currentPage - 1) * state.pageSize;
    const end = Math.min(start + state.pageSize, total);
    const pageData = state.filteredData.slice(start, end);
    
    if (state.viewMode === 'timeline') {
        container.innerHTML = renderTimelineView(pageData);
    } else {
        container.innerHTML = pageData.map(news => renderCard(news)).join('');
    }
    
    renderPagination(totalPages);
}

// ===== 单个资讯卡片 =====
function renderCard(news) {
    const srcCfg = SOURCE_CONFIG[news.source] || { name: news.sourceName, icon: '📌', color: '#666' };
    const impactCfg = IMPACT_CONFIG[news.impact] || IMPACT_CONFIG.normal;
    const dateObj = new Date(news.date);
    const dateStr = `${dateObj.getFullYear()}年${dateObj.getMonth()+1}月${dateObj.getDate()}日`;
    
    return `
        <article class="news-card" data-id="${news.id}" onclick="openDetail(${news.id})">
            <div class="card-header">
                <span class="news-source" style="color:${srcCfg.color};background:${srcCfg.color}15;border:1px solid ${srcCfg.color}30;">
                    ${srcCfg.icon} ${srcCfg.name}
                </span>
                <span class="news-date">${dateStr}</span>
                <span class="impact-badge" style="background:${impactCfg.bg};color:${impactCfg.color};border:1px solid ${impactCfg.color}40;">
                    ${impactCfg.label}
                </span>
            </div>
            <h3 class="card-title">${news.title}</h3>
            <p class="card-summary">${news.summary}</p>
            <div class="card-tags">
                ${news.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <div class="card-footer">
                <span class="category-tag">${news.category}</span>
                <span class="read-more">阅读全文 →</span>
            </div>
        </article>
    `;
}

// ===== 时间轴视图 =====
function renderTimelineView(data) {
    // 按年份分组
    const groups = {};
    data.forEach(item => {
        const year = item.date.substring(0, 4);
        if (!groups[year]) groups[year] = [];
        groups[year].push(item);
    });
    
    return Object.entries(groups)
        .sort((a, b) => b[0] - a[0])
        .map(([year, items]) => `
            <div class="timeline-group">
                <div class="timeline-year">${year}年</div>
                <div class="timeline-items">
                    ${items.map(item => {
                        const srcCfg = SOURCE_CONFIG[item.source] || { name: item.sourceName, icon: '📌', color: '#666' };
                        const impactCfg = IMPACT_CONFIG[item.impact] || IMPACT_CONFIG.normal;
                        return `
                            <div class="timeline-item" onclick="openDetail(${item.id})">
                                <div class="timeline-dot" style="background:${srcCfg.color}"></div>
                                <div class="timeline-content">
                                    <div class="timeline-meta">
                                        <span style="color:${srcCfg.color}">${srcCfg.icon} ${srcCfg.name}</span>
                                        <span>${item.date.substring(5)}</span>
                                        <span class="impact-badge small" style="background:${impactCfg.bg};color:${impactCfg.color}">${impactCfg.label}</span>
                                    </div>
                                    <h4>${item.title}</h4>
                                    <p>${item.summary}</p>
                                    <div class="card-tags mini">${item.tags.slice(0,3).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `).join('');
}

// ===== 分页渲染 =====
function renderPagination(totalPages) {
    const container = document.getElementById('pagination');
    if (!container || totalPages <= 1) {
        if (container) container.innerHTML = '';
        return;
    }
    
    let html = '<div class="pagination-inner">';
    
    // 上一页
    html += `<button class="page-btn" ${state.currentPage <= 1 ? 'disabled' : ''} onclick="goPage(${state.currentPage-1})">‹ 上一页</button>';
    
    // 页码
    const maxVisible = 5;
    let startPage = Math.max(1, state.currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    if (startPage > 1) {
        html += `<button class="page-btn" onclick="goPage(1)">1</button>`;
        if (startPage > 2) html += `<span class="page-dots">...</span>`;
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="page-btn ${i === state.currentPage ? 'active' : ''}" onclick="goPage(${i})">${i}</button>`;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<span class="page-dots">...</span>`;
        html += `<button class="page-btn" onclick="goPage(${totalPages})">${totalPages}</button>`;
    }
    
    // 下一页
    html += `<button class="page-btn" ${state.currentPage >= totalPages ? 'disabled' : ''} onclick="goPage(${state.currentPage+1})">下一页 ›</button>`;
    
    html += '</div>';
    container.innerHTML = html;
}

function goPage(page) {
    const totalPages = Math.ceil(state.filteredData.length / state.pageSize);
    if (page < 1 || page > totalPages) return;
    state.currentPage = page;
    renderNews();
    // 滚动到列表顶部
    document.getElementById('newsList').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== 打开详情模态框 =====
function openDetail(id) {
    const news = state.allData.find(n => n.id === id);
    if (!news) return;
    
    state.selectedNews = news;
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('detailContent');
    
    const srcCfg = SOURCE_CONFIG[news.source] || { name: news.sourceName, icon: '📌', color: '#666' };
    const impactCfg = IMPACT_CONFIG[news.impact] || IMPACT_CONFIG.normal;
    const dateObj = new Date(news.date);
    const dateStr = dateObj.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
    
    // 将content中的换行转为HTML段落
    const formattedContent = news.content
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    content.innerHTML = `
        <div class="detail-header">
            <div class="detail-meta-top">
                <span class="news-source large" style="color:${srcCfg.color};background:${srcCfg.color}10;border:1px solid ${srcCfg.color}30;">
                    ${srcCfg.icon} ${srcCfg.name}
                </span>
                <span class="impact-badge large" style="background:${impactCfg.bg};color:${impactCfg.color};border:1px solid ${impactCfg.color}50;">
                    ${impactCfg.label}
                </span>
                <span class="category-tag large">${news.category}</span>
            </div>
            <time class="detail-date">${dateStr}</time>
            <h2 class="detail-title">${news.title}</h2>
            <p class="detail-summary">${news.summary}</p>
        </div>
        <div class="detail-body">
            <p>${formattedContent}</p>
        </div>
        <div class="detail-tags">
            ${news.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
        <div class="detail-actions">
            <button class="action-btn secondary" onclick="closeDetail()">关闭</button>
            <button class="action-btn primary" onclick="shareNews(${id})">分享此条</button>
        </div>
    `;
    
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeDetail() {
    const modal = document.getElementById('detailModal');
    modal.classList.remove('show');
    document.body.style.overflow = '';
    state.selectedNews = null;
}

// ===== 分享功能 =====
function shareNews(id) {
    const news = state.allData.find(n => n.id === id);
    if (!news) return;
    
    const text = `【AdPulse 广告资讯】${news.title}\n\n${news.summary}\n\n来源：${news.sourceName} | 日期：${news.date}`;
    
    if (navigator.share) {
        navigator.share({ title: news.title, text: text, url: window.location.href });
    } else {
        navigator.clipboard.writeText(text).then(() => {
            showToast('已复制到剪贴板！');
        }).catch(() => {
            fallbackCopy(text);
        });
    }
}

function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); showToast('已复制到剪贴板！'); } catch(e) {}
    document.body.removeChild(ta);
}

// ===== Toast 提示 =====
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}

// ===== 自动更新通知 =====
function showUpdateNotification() {
    setTimeout(() => {
        const notif = document.getElementById('updateNotif');
        notif.classList.add('show');
        setTimeout(() => notif.classList.remove('show'), 5000);
    }, 2000);
}

// ===== 搜索功能 =====
function handleSearch(query) {
    state.searchQuery = query.trim().toLowerCase();
    state.currentPage = 1;
    applyFilters();
}

function performSearch() {
    const input = document.getElementById('searchInput');
    handleSearch(input.value);
}

// ===== 筛选逻辑 =====
function applyFilters() {
    let result = [...state.allData];
    
    // 来源筛选
    if (state.activeSource !== 'all') {
        result = result.filter(n => n.source === state.activeSource);
    }
    
    // 分类筛选
    if (state.activeCategory !== 'all') {
        result = result.filter(n => n.category === state.activeCategory);
    }
    
    // 影响力筛选
    if (state.activeImpact !== 'all') {
        result = result.filter(n => n.impact === state.activeImpact);
    }
    
    // 搜索关键词
    if (state.searchQuery) {
        result = result.filter(n => 
            n.title.toLowerCase().includes(state.searchQuery) ||
            n.summary.toLowerCase().includes(state.searchQuery) ||
            n.tags.some(t => t.toLowerCase().includes(state.searchQuery)) ||
            n.category.toLowerCase().includes(state.searchQuery)
        );
    }
    
    // 排序
    switch (state.sortMode) {
        case 'date-asc':
            result.sort((a, b) => new Date(a.date) - new Date(b.date));
            break;
        case 'date-desc':
            result.sort((a, b) => new Date(b.date) - new Date(a.date));
            break;
        case 'impact':
            const order = { high: 0, medium: 1, normal: 2 };
            result.sort((a, b) => (order[a.impact]||99) - (order[b.impact]||99));
            break;
    }
    
    state.filteredData = result;
    renderStats();
    renderNews();
    updateActiveFilterStyles();
}

function updateActiveFilterStyles() {
    // 来源按钮
    document.querySelectorAll('#sourceFilters .filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.source === state.activeSource);
    });
    
    // 分类按钮
    document.querySelectorAll('#categoryFilters .cat-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === state.activeCategory);
    });
    
    // 影响力按钮
    document.querySelectorAll('.impact-filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.impact === state.activeImpact);
    });
    
    // 排序按钮
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.sort === state.sortMode);
    });
    
    // 视图切换
    document.querySelectorAll('.view-toggle .toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === state.viewMode);
    });
    
    // 更新搜索框值
    const input = document.getElementById('searchInput');
    if (input && input.value !== state.searchQuery && !input.matches(':focus')) {
        // Don't override while user is typing
    }
}

// ===== 绑定事件 =====
function bindEvents() {
    // 搜索
    const searchInput = document.getElementById('searchInput');
    let searchTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(performSearch, 300);
    });
    searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') performSearch();
    });
    
    // 来源筛选（事件委托）
    document.getElementById('sourceFilters').addEventListener('click', e => {
        const btn = e.target.closest('.filter-btn');
        if (!btn) return;
        state.activeSource = btn.dataset.source;
        state.currentPage = 1;
        applyFilters();
    });
    
    // 分类筛选（事件委托）
    document.getElementById('categoryFilters').addEventListener('click', e => {
        const btn = e.target.closest('.cat-btn');
        if (!btn) return;
        state.activeCategory = btn.dataset.category;
        state.currentPage = 1;
        applyFilters();
    });
    
    // 影响力筛选
    document.querySelector('.impact-filters')?.addEventListener('click', e => {
        const btn = e.target.closest('.impact-filter-btn');
        if (!btn) return;
        state.activeImpact = btn.dataset.impact;
        state.currentPage = 1;
        applyFilters();
    });
    
    // 排序
    document.querySelector('.sort-options')?.addEventListener('click', e => {
        const btn = e.target.closest('.sort-btn');
        if (!btn) return;
        state.sortMode = btn.dataset.sort;
        state.currentPage = 1;
        applyFilters();
    });
    
    // 视图切换
    document.querySelector('.view-toggle')?.addEventListener('click', e => {
        const btn = e.target.closest('.toggle-btn');
        if (!btn) return;
        state.viewMode = btn.dataset.view;
        state.currentPage = 1;
        applyFilters();
    });
    
    // 关闭模态框
    document.getElementById('detailModal').addEventListener('click', e => {
        if (e.target === e.currentTarget) closeDetail();
    });
    
    // ESC 关闭
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeDetail();
    });
    
    // 清空搜索
    document.querySelector('.clear-search')?.addEventListener('click', () => {
        searchInput.value = '';
        handleSearch('');
    });
    
    // 刷新按钮
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        const btn = document.getElementById('refreshBtn');
        btn.classList.add('spinning');
        setTimeout(() => {
            btn.classList.remove('spinning');
            showToast('数据已更新至最新状态！');
            showUpdateNotification();
        }, 1000);
    });

    // 年份快速跳转
    document.getElementById('yearFilter')?.addEventListener('change', e => {
        const year = e.target.value;
        if (year === 'all') {
            state.searchQuery = '';
        } else {
            state.searchQuery = year;
        }
        state.currentPage = 1;
        applyFilters();
    });
}
