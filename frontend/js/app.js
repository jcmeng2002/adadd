/**
 * ADADD · 广告行业资讯聚合平台 - 前端主逻辑
 * 版本: v2.0 (全栈版，对接后端API)
 * 作者: nelsonmeng
 * 
 * 核心功能：
 * - 对接后端 RESTful API 获取数据
 * - 多维度筛选（来源/分类/影响力/年份）
 * - 关键词搜索（本地模式 + 实时跳转模式）
 * - 双视图（卡片/时间轴）+ 4种排序 + 分页
 * - 详情弹窗 + 访问原文
 */

// ============================================================
// 全局配置与状态管理
// ============================================================

const CONFIG = {
    API_BASE: '', // 空字符串表示同源部署；如果前后端分离则改为 'http://localhost:5000'
    PAGE_SIZE: 12,
    DEBOUNCE_MS: 400,
};

// 来源配置 - 与后端一致
const SOURCE_CONFIG = {
    weibo:       { name: '微博',     icon: '📱', color: '#E6162D' },
    zhihu:       { name: '知乎',     icon: '💡', color: '#0084FF' },
    wechat:      { name: '微信公众号', icon: '📨', color: '#07C160' },
    github:      { name: 'GitHub',   icon: '🐙', color: '#24292E' },
    'tech-media':{ name: '技术社区',  icon: '⚙️', color: '#ED7B2D' },
    'industry-media': { name: '行业媒体', icon: '📰', color: '#0052D9' },
    '36kr':      { name: '36氪',     icon: '🚀', color: '#0066CC' },
};

// 应用状态
const state = {
    filters: { source: 'all', category: 'all', impact: 'all', year: '' },
    sort: 'latest',
    view: 'card',
    keyword: '',
    searchMode: 'local', // 'local' | 'realtime'
    currentPage: 1,
    totalItems: 0,
    totalPages: 0,
    isLoading: true,
};

// 缓存统计信息
let statsCache = null;

// ============================================================
// DOM 引用
// ============================================================

const $ = id => document.getElementById(id);

const dom = {
    searchBar: $('searchBar'),
    searchInput: $('searchInput'),
    clearSearch: $('clearSearch'),
    modeToggle: $('searchModeToggle'),
    modeLabel: $('modeLabel'),
    yearSelect: $('yearSelect'),
    refreshBtn: $('refreshBtn'),
    crawlBtn: $('crawlBtn'),
    sourceFilters: $('sourceFilters'),
    categoryFilters: $('categoryFilters'),
    impactFilters: $('impactFilters'),
    sortOptions: $('sortOptions'),
    viewToggle: $('viewToggle'),
    statTotal: $('statTotal'),
    statFiltered: $('statFiltered'),
    statHighImpact: $('statHighImpact'),
    statSources: $('statSources'),
    statLastUpdate: $('statLastUpdate'),
    newsGrid: $('newsGrid'),
    timelineView: $('timelineView'),
    emptyState: $('emptyState'),
    loadingState: $('loadingState'),
    pagination: $('pagination'),
    detailModal: $('detailModal'),
    modalClose: $('modalClose'),
    modalBody: $('modalBody'),
    toast: $('toast'),
    updateNotification: $('updateNotification'),
    footerTotal: $('footerTotal'),
    footerYears: $('footerYears'),
};

// ============================================================
// 工具函数
// ============================================================

function showToast(message, duration = 2500) {
    dom.toast.textContent = message;
    dom.toast.classList.add('show');
    setTimeout(() => dom.toast.classList.remove('show'), duration);
}

function showUpdateNotification(msg) {
    $('updateMsg').textContent = msg;
    dom.updateNotification.classList.add('show');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(fn, ms) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), ms);
    };
}

// ============================================================
// API 调用层
// ============================================================

async function apiGet(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = `${CONFIG.API_BASE}${endpoint}${query ? '?' + query : ''}`;
    
    try {
        const resp = await fetch(url);
        
        if (!resp.ok) {
            console.error(`API Error ${resp.status}: ${endpoint}`);
            // 如果API不可用，回退到本地数据文件
            if (window.AD_NEWS_DATA) {
                console.log('回退到本地数据');
                return fallbackLocalData(endpoint, params);
            }
            throw new Error(`HTTP ${resp.status}`);
        }
        
        return await resp.json();
    } catch (err) {
        console.warn('API请求失败:', err.message);
        // 回退到本地数据
        if (window.AD_NEWS_DATA) {
            return fallbackLocalData(endpoint, params);
        }
        throw err;
    }
}

async function apiPost(endpoint) {
    try {
        const resp = await fetch(`${CONFIG.API_BASE}${endpoint}`, { method: 'POST' });
        return await resp.json();
    } catch (err) {
        console.error('API POST失败:', err);
        return { code: 500, success: false, message: err.message };
    }
}

// 本地数据回退方案
function fallbackLocalData(endpoint, params) {
    if (!window.AD_NEWS_DATA) return { code: 200, success: true, data: { items: [], pagination: { total: 0 } } };
    
    let data = [...AD_NEWS_DATA];
    
    // 应用筛选
    if (params.source && params.source !== 'all') data = data.filter(i => i.source === params.source);
    if (params.category && params.category !== 'all') data = data.filter(i => i.category === params.category);
    if (params.impact && params.impact !== 'all') data = data.filter(i => i.impact === params.impact);
    if (params.year && params.year !== 'all') data = data.filter(i => i.date.startsWith(params.year));
    
    if (params.keyword) {
        const kw = params.keyword.toLowerCase();
        data = data.filter(i =>
            i.title.toLowerCase().includes(kw) ||
            i.summary.toLowerCase().includes(kw) ||
            i.tags.some(t => t.toLowerCase().includes(kw))
        );
    }
    
    // 排序
    const reverse = params.sort !== 'oldest';
    data.sort((a, b) => {
        if (params.sort === 'impact') {
            const order = { high: 3, medium: 2, low: 1 };
            return (order[b.impact] || 1) - (order[a.impact] || 1);
        }
        if (params.sort === 'readCount') return b.readCount - a.readCount;
        return reverse ? (b.date > a.date ? 1 : -1) : (a.date > b.date ? 1 : -1);
    });
    
    const page = parseInt(params.page || 1);
    const perPage = parseInt(params.per_page || 12);
    const total = data.length;
    const totalPages = Math.ceil(total / perPage) || 1;
    const items = data.slice((page - 1) * perPage, page * perPage);
    
    return {
        code: 200,
        success: true,
        data: {
            items,
            pagination: { page, per_page: perPage, total, totalPages, has_next: page < totalPages, has_prev: page > 1 },
            stats: buildLocalStats(AD_NEWS_DATA, data),
        }
    };
}

function buildLocalStats(allData, filteredData) {
    const sc = {};
    for (const item of allData) sc[item.source] = (sc[item.source] || 0) + 1;
    
    const cc = {};
    for (const item of allData) cc[item.category] = (cc[item.category] || 0) + 1;
    
    const ic = { high: 0, medium: 0, low: 0 };
    for (const item of allData) ic[item.impact] = (ic[item.impact] || 0) + 1;
    
    const yc = {};
    for (const item of allData) yc[item.date.slice(0,4)] = (yc[item.date.slice(0,4)] || 0) + 1;
    
    return {
        totalCount: allData.length,
        filteredCount: filteredData.length,
        sourceCounts: sc,
        categoryCounts: cc,
        impactCounts: ic,
        yearCounts: Object.fromEntries(Object.entries(yc).sort((a,b) => b[0].localeCompare(a[0]))),
        latestDate: allData.length ? allData[0].date : '',
        lastUpdated: new Date().toLocaleString('zh-CN'),
    };
}


// ============================================================
// 渲染函数
// ============================================================

function renderSources() {
    const counts = statsCache?.sourceCounts || {};
    let html = '<button class="filter-btn active" data-source="all">全部 <span class="count">' +
        Object.values(counts).reduce((a, b) => a + b, 0) + '</span></button>';
    
    for (const [key, info] of Object.entries(SOURCE_CONFIG)) {
        html += `<button class="filter-btn" data-source="${key}">${info.icon} ${info.name} <span class="count">${counts[key] || 0}</span></button>`;
    }
    dom.sourceFilters.innerHTML = html;
}

function renderCategories() {
    const counts = statsCache?.categoryCounts || {};
    // 只显示有数据的分类
    const sortedCats = Object.entries(counts)
        .filter(([_, c]) => c > 0)
        .sort((a, b) => b[1] - a[1]);
    
    let html = '<button class="cat-btn active" data-category="all">全部分类</button> ';
    
    for (const [cat, count] of sortedCats) {
        html += `<button class="cat-btn" data-category="${escapeHtml(cat)}">${escapeHtml(cat)} <span class="count">${count}</span></button>`;
    }
    dom.categoryFilters.innerHTML = html;
}

function renderStats(stats) {
    if (!stats) return;
    statsCache = stats;
    
    dom.statTotal.textContent = stats.totalCount;
    dom.statFiltered.textContent = stats.filteredCount;
    dom.statHighImpact.textContent = stats.impactCounts?.high || 0;
    dom.statSources.textContent = Object.keys(stats.sourceCounts || {}).length;
    
    if (stats.lastUpdated) {
        const d = new Date(stats.lastUpdated);
        dom.statLastUpdate.textContent = `${d.getMonth()+1}/${d.getDate()}`;
    }
    
    dom.footerTotal.textContent = stats.totalCount;
    
    const years = Object.keys(stats.yearCounts || {});
    dom.footerYears.textContent = years.length ? 
        `${Math.min(...years)}-${Math.max(...years)}` : '10+';
    
    renderSources();
    renderCategories();
}

function renderNewsCard(item) {
    const srcConf = SOURCE_CONFIG[item.source] || { name: item.source, icon: '📌', color: '#666' };
    const impactLabels = { high: '高影响力', medium: '中影响力', low: '一般关注' };
    
    return `
    <div class="news-card" data-id="${item.id}" onclick="openDetail(${item.id})">
        <div class="card-header">
            <span class="news-source source-${item.source}">${srcConf.icon} ${srcConf.name}</span>
            <span class="news-date">${item.date}</span>
            <span class="impact-badge impact-${item.impact}">${impactLabels[item.impact]}</span>
        </div>
        <h3 class="card-title">${escapeHtml(item.title)}</h3>
        <p class="card-summary">${escapeHtml(item.summary)}</p>
        <div class="card-tags">
            ${item.tags.slice(0, 5).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('')}
        </div>
        <div class="card-footer">
            <span class="category-tag">${escapeHtml(item.category)}</span>
            <span>
                <span class="read-more">阅读全文 →</span>
                ${item.url ? `<a class="visit-link" href="${item.url}" target="_blank" rel="noopener" onclick="event.stopPropagation()">访问原文 ↗</a>` : ''}
            </span>
        </div>
    </div>`;
}

function renderTimelineItem(item) {
    const srcConf = SOURCE_CONFIG[item.source] || { name: item.source, icon: '📌' };
    const impactLabels = { high: '高', medium: '中', low: '低' };
    
    return `
    <div class="timeline-item" data-id="${item.id}" onclick="openDetail(${item.id})">
        <div class="timeline-dot dot-${item.source}"></div>
        <div class="timeline-content">
            <div class="timeline-meta">
                <span class="news-source source-${item.source}" style="display:inline-flex;align-items:center;gap:3px;font-size:11px;padding:2px 8px;">${srcConf.icon} ${srcConf.name}</span>
                <span>${item.date}</span>
                <span class="impact-badge impact-${item.impact}">${impactLabels[item.impact]}影响</span>
                <span style="color:#999;">${escapeHtml(item.category)}</span>
            </div>
            <h4>${escapeHtml(item.title)}</h4>
            <p>${escapeHtml(item.summary)}</p>
        </div>
    </div>`;
}

function renderNews(data) {
    const items = data.items || [];
    const pag = data.pagination || {};
    
    state.totalItems = pag.total || 0;
    state.totalPages = pag.total_pages || 1;
    
    // 显示/隐藏加载和空状态
    dom.loadingState.style.display = 'none';
    
    if (!items.length) {
        dom.newsGrid.style.display = 'none';
        dom.timelineView.style.display = 'none';
        dom.emptyState.style.display = 'flex';
        dom.pagination.style.display = 'none';
        return;
    }
    
    dom.emptyState.style.display = 'none';
    
    if (state.view === 'card') {
        dom.newsGrid.style.display = 'grid';
        dom.timelineView.style.display = 'none';
        dom.newsGrid.innerHTML = items.map(renderNewsCard).join('');
    } else {
        dom.newsGrid.style.display = 'none';
        dom.timelineView.style.display = 'block';
        
        // 按年分组
        const grouped = {};
        for (const item of items) {
            const year = item.date.slice(0, 4);
            if (!grouped[year]) grouped[year] = [];
            grouped[year].push(item);
        }
        
        let html = '';
        for (const [year, itemsOfYear] of Object.entries(grouped).sort((a, b) => b[0].localeCompare(a[0]))) {
            html += `<div class="timeline-group"><h3 class="timeline-year">${year}</h3><div class="timeline-items">`;
            html += itemsOfYear.map(renderTimelineItem).join('');
            html += `</div></div>`;
        }
        dom.timelineView.innerHTML = html;
    }
    
    // 分页
    if (pag.total_pages > 1) {
        dom.pagination.style.display = 'flex';
        renderPagination(pag);
    } else {
        dom.pagination.style.display = 'none';
    }
}

function renderPagination(pag) {
    const { page, total_pages, has_prev, has_next } = pag;
    let html = '<div class="pagination-inner">';
    
    html += `<button class="page-btn" ${has_prev ? '' : 'disabled'} onclick="goToPage(${page-1})">‹ 上一页</button>`;
    
    // 页码显示逻辑
    const pages = [];
    if (total_pages <= 7) {
        for (let i = 1; i <= total_pages; i++) pages.push(i);
    } else {
        pages.push(1);
        if (page > 3) pages.push('...');
        for (let i = Math.max(2, page - 1); i <= Math.min(total_pages - 1, page + 1); i++) pages.push(i);
        if (page < total_pages - 2) pages.push('...');
        pages.push(total_pages);
    }
    
    for (const p of pages) {
        if (p === '...') {
            html += '<span class="page-dots">...</span>';
        } else {
            html += `<button class="page-btn ${p === page ? 'active' : ''}" onclick="goToPage(${p})">${p}</button>`;
        }
    }
    
    html += `<button class="page-btn" ${has_next ? '' : 'disabled'} onclick="goToPage(${page+1})">下一页 ›</button>`;
    html += `<span style="margin-left:10px;color:#999;font-size:12px;">第 ${page}/${total_pages} 页 · 共 ${pag.total} 条</span>`;
    html += '</div>';
    
    dom.pagination.innerHTML = html;
}

function openDetail(id) {
    event && event.stopPropagation();
    
    // 先从缓存找
    let item = null;
    // 简单方式：直接从当前渲染的数据中找（这里简化处理）
    // 实际应调用详情API
    
    // 调用详情API或从已有数据获取
    apiGet(`/api/news/${id}`).then(resp => {
        if (resp.success && resp.data) {
            item = resp.data;
            
            if (item) {
                const srcConf = SOURCE_CONFIG[item.source] || { name: item.source, icon: '📌' };
                const impactLabels = { high: '高影响力', medium: '中影响力', low: '一般关注' };
                
                dom.modalBody.innerHTML = `
                    <div class="detail-header">
                        <div class="detail-meta-top">
                            <span class="news-source large source-${item.source}">${srcConf.icon} ${srcConf.name}</span>
                            <span class="impact-badge large impact-${item.impact}">${impactLabels[item.impact]}</span>
                            <span class="category-tag large">${escapeHtml(item.category)}</span>
                        </div>
                        <span class="detail-date">📅 ${item.date} · 👁️ ${item.readCount || 0} 阅读 · 🔗 ${item.shareCount || 0} 次分享</span>
                        <h2 class="detail-title">${escapeHtml(item.title)}</h2>
                        <p class="detail-summary">${escapeHtml(item.summary)}</p>
                    </div>
                    <div class="detail-body">
                        <p>${escapeHtml(item.body || item.summary)}</p>
                    </div>
                    <div class="detail-tags">
                        ${item.tags.map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('')}
                    </div>
                    <div class="detail-actions">
                        ${item.url ? `<button class="action-btn visit-original-btn" onclick="window.open('${item.url}','_blank')">访问原文 ↗</button>` : ''}
                        <button class="action-btn secondary" onclick="copyShareLink(${item.id})">复制链接</button>
                        <button class="action-btn primary" onclick="closeDetail()">关闭</button>
                    </div>`;
                
                dom.detailModal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        }
    }).catch(err => {
        console.error('获取详情失败:', err);
        showToast('无法加载详情');
    });
}

function closeDetail() {
    dom.detailModal.classList.remove('show');
    document.body.style.overflow = '';
}

function copyShareLink(id) {
    const url = `${location.origin}${location.pathname}?id=${id}&ref=share`;
    navigator.clipboard.writeText(url).then(() => showToast('链接已复制！'));
}


// ============================================================
// 数据加载与刷新
// ============================================================

async function loadNews(silent = false) {
    if (!silent) state.isLoading = true;
    
    const params = {
        source: state.filters.source,
        category: state.filters.category,
        impact: state.filters.impact,
        year: state.filters.year,
        keyword: state.keyword,
        sort: state.sort,
        page: state.currentPage,
        per_page: CONFIG.PAGE_SIZE,
    };
    
    try {
        const resp = await apiGet('/api/news', params);
        
        if (resp.success) {
            renderNews(resp.data);
            if (resp.data.stats) renderStats(resp.data.stats);
        } else {
            console.error('API返回错误:', resp);
        }
    } finally {
        state.isLoading = false;
    }
}

async function loadStats() {
    try {
        const resp = await apiGet('/api/stats');
        if (resp.success) renderStats(resp.data);
    } catch (err) {
        console.error('加载统计数据失败:', err);
    }
}

async function refreshFromServer(showToastMsg = true) {
    dom.refreshBtn.classList.add('spinning');
    
    try {
        // 调用刷新接口触发服务端重新抓取
        await apiPost('/api/refresh');
        
        // 重新加载数据
        await Promise.all([loadStats(), loadNews()]);
        
        if (showToastMsg) showToast('✅ 数据已更新到最新！');
    } catch (err) {
        showToast('⚠️ 刷新失败: ' + err.message);
    } finally {
        dom.refreshBtn.classList.remove('spinning');
    }
}

async function triggerRealTimeCrawl() {
    showToast('🕷️ 正在抓取最新资讯...');
    
    try {
        const resp = await apiPost('/api/crawl');
        if (resp.success) {
            const newCount = resp.data?.newCount || 0;
            showUpdateNotification(`🎉 抓取完成！新增 ${newCount} 条最新资讯`);
            await Promise.all([loadStats(), loadNews()]);
        } else {
            showToast(resp.message || '抓取完成');
        }
    } catch (err) {
        showToast('⚠️ 抓取失败: ' + err.message);
    }
}

// ============================================================
// 搜索功能
// ============================================================

const handleSearch = debounce(async () => {
    const kw = dom.searchInput.value.trim();
    state.keyword = kw;
    state.currentPage = 1;
    
    // 显示清除按钮
    dom.clearSearch.style.display = kw ? 'flex' : 'none';
    
    if (state.searchMode === 'realtime' && kw) {
        // 实时模式：跳转到外部搜索
        window.open(`https://www.google.com/search?q=${encodeURIComponent(kw + ' 广告营销 行业资讯')}`, '_blank');
        return;
    }
    
    // 本地模式：通过API搜索
    await loadNews();
}, CONFIG.DEBOUNCE_MS);

function toggleSearchMode() {
    state.searchMode = state.searchMode === 'local' ? 'realtime' : 'local';
    
    if (state.searchMode === 'realtime') {
        dom.modeLabel.textContent = '🔍 实时';
        dom.modeToggle.classList.add('active-realtime');
    } else {
        dom.modeLabel.textContent = '📋 本地';
        dom.modeToggle.classList.remove('active-realtime');
    }
}


// ============================================================
// 页码导航
// ============================================================

function goToPage(page) {
    if (page < 1 || page > state.totalPages) return;
    state.currentPage = page;
    loadNews();
    // 滚动到列表顶部
    dom.newsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


// ============================================================
// 事件绑定
// ============================================================

function bindEvents() {
    // 搜索
    dom.searchInput.addEventListener('input', handleSearch);
    dom.searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            handleSearch.flush && handleSearch.flush();
            handleSearch();
        }
    });
    dom.clearSearch.addEventListener('click', () => {
        dom.searchInput.value = '';
        dom.clearSearch.style.display = 'none';
        state.keyword = '';
        handleSearch();
    });
    dom.modeToggle.addEventListener('click', toggleSearchMode);
    
    // 年份筛选
    dom.yearSelect.addEventListener('change', () => {
        state.filters.year = dom.yearSelect.value;
        state.currentPage = 1;
        loadNews();
    });
    
    // 刷新按钮
    dom.refreshBtn.addEventListener('click', () => refreshFromServer());
    
    // 实时抓取按钮
    if (dom.crawlBtn) dom.crawlBtn.addEventListener('click', triggerRealTimeCrawl);
    
    // 来源筛选（事件委托）
    dom.sourceFilters.addEventListener('click', e => {
        const btn = e.target.closest('[data-source]');
        if (!btn) return;
        
        dom.sourceFilters.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.filters.source = btn.dataset.source;
        state.currentPage = 1;
        loadNews();
    });
    
    // 分类筛选（事件委托）
    dom.categoryFilters.addEventListener('click', e => {
        const btn = e.target.closest('[data-category]');
        if (!btn) return;
        
        dom.categoryFilters.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.filters.category = btn.dataset.category;
        state.currentPage = 1;
        loadNews();
    });
    
    // 影响力筛选
    dom.impactFilters.addEventListener('click', e => {
        const btn = e.target.closest('[data-value]');
        if (!btn) return;
        dom.impactFilters.querySelectorAll('.impact-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.filters.impact = btn.dataset.value;
        state.currentPage = 1;
        loadNews();
    });
    
    // 排序切换
    dom.sortOptions.addEventListener('click', e => {
        const btn = e.target.closest('[data-sort]');
        if (!btn) return;
        dom.sortOptions.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.sort = btn.dataset.sort;
        state.currentPage = 1;
        loadNews();
    });
    
    // 视图切换
    dom.viewToggle.addEventListener('click', e => {
        const btn = e.target.closest('[data-view]');
        if (!btn) return;
        dom.viewToggle.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.view = btn.dataset.view;
        loadNews(); // 重渲染以切换视图
    });
    
    // 弹窗关闭
    dom.modalClose.addEventListener('click', closeDetail);
    dom.detailModal.addEventListener('click', e => {
        if (e.target === dom.detailModal) closeDetail();
    });
    
    // ESC 关闭弹窗
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeDetail();
    });
}


// ============================================================
// 初始化
// ============================================================

async function init() {
    console.log('%c ADADD %c v2.0 ', 'background:#0052D9;color:white;border-radius:4px;padding:2px 8px;', 'color:#0052D9;font-weight:bold;');
    
    bindEvents();
    
    // 并行加载统计和新闻
    await Promise.all([loadStats(), loadNews()]);
    
    // 检查URL参数中的搜索词
    const urlParams = new URLSearchParams(location.search);
    const urlKeyword = urlParams.get('q');
    if (urlKeyword) {
        dom.searchInput.value = urlKeyword;
        state.keyword = urlKeyword;
        dom.clearSearch.style.display = 'flex';
        await loadNews();
    }
    
    console.log('ADADD 初始化完成 ✅');
}

// 启动
document.addEventListener('DOMContentLoaded', init);

// 导出给全局使用（HTML内联onclick等需要）
window.openDetail = openDetail;
window.closeDetail = closeDetail;
window.goToPage = goToPage;
window.copyShareLink = copyShareLink;
