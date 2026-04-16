#!/usr/bin/env python3
"""
ADADD Build V8 - FINAL VERSION
Strategy: 
1. Data embedded as <script type="application/json"> → zero escaping issues
2. All JS innerHTML uses template literals (backticks) → zero quote nesting
3. No onclick inline attributes → all events via delegation with data-* attrs
4. Python uses raw strings (r''') for JS code → no f-string conflicts
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, 'data', 'news_data.json')
OUT_PATH = os.path.join(BASE, 'index.html')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    raw = f.read().strip()
    data_list = json.loads(raw if raw.startswith('[') else raw)

print(f"Loaded {len(data_list)} items")
years = sorted(set(item['date'][:4] for item in data_list), reverse=True)
print(f"Years: {years}")

data_json = json.dumps(data_list, ensure_ascii=False)
data_safe = data_json.replace('</script', '<\\/script').replace('</', '<\\/')

css = r"""@font-face{font-family:"Tencent Sans";src:url("fonts/TencentSans-W7-subset.woff2") format("woff2"),url("fonts/TencentSans-W7.otf") format("opentype");font-weight:700;font-style:normal;font-display:swap}
:root{--p:#0052D9;--pl:#E8F0FE;--pd:#1a3c6e;--ph:#2670F0;--a:#00A870;--w:#ED7B2D;--d:#E02020;--t1:#1a1a1a;--t2:#666666;--t3:#999999;--bc:#e5e5e5;--bg:#f5f7fa;--wh:#ffffff;--ss:0 1px 3px rgba(0,0,0,.06);--sm:0 4px 12px rgba(0,0,0,.08);--sl:0 8px 30px rgba(0,0,0,.12);--r1:6px;--r2:10px;--r3:16px;--ff:"Tencent Sans","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{font-family:var(--ff);background:var(--bg);color:var(--t1);line-height:1.6;min-height:100vh}a{color:var(--p);text-decoration:none}button{cursor:pointer;font-family:inherit;border:none;background:none}input,select{font-family:inherit}
.navbar{position:sticky;top:0;z-index:100;background:var(--wh);border-bottom:1px solid var(--bc);box-shadow:var(--ss)}
.nav-inner{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:20px;padding:12px 24px}.logo{display:flex;align-items:center;gap:10px}
.logo-icon-wrap{position:relative;width:32px;height:32px;flex-shrink:0;display:flex;align-items:center;justify-content:center}
.logo-ring{position:absolute;inset:0;border:2px solid transparent;border-top-color:#0052D9;border-right-color:#00A3FF;border-radius:50%;animation:spin 6s linear infinite}
.logo-ring-inner{position:absolute;inset:4px;border:1.5px solid transparent;border-bottom-color:rgba(0,163,255,.5);border-left-color:rgba(0,82,217,.3);border-radius:50%;animation:spin 4s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.logo-center{font-family:"Tencent Sans",sans-serif;font-size:12px;font-weight:800;color:#1a1a1a;z-index:2;line-height:1}
.logo-center .lp{font-weight:300;color:#0052D9}
.logo-text{font-size:22px;font-weight:900;color:#0052D9;letter-spacing:2px;font-family:"Tencent Sans",sans-serif;position:relative}
.logo-text::after{content:'';position:absolute;bottom:-3px;left:0;width:100%;height:2px;background:linear-gradient(90deg,#0052D9,#00A3FF,transparent);border-radius:1px}
.logo-sub{font-size:11px;color:var(--t3);padding-left:8px;border-left:1px solid var(--bc)}.nav-center{flex:1;max-width:480px}
.search-bar{display:flex;align-items:center;background:var(--bg);border-radius:20px;padding:8px 16px;gap:8px;transition:all .25s;border:1.5px solid transparent}.search-bar:focus-within{background:var(--wh);border-color:var(--p);box-shadow:0 0 0 3px rgba(0,82,217,.08)}.search-bar input{flex:1;border:none;outline:none;background:transparent;font-size:14px;color:var(--t1)}.clear-search{width:18px;height:18px;border-radius:50%;display:none;align-items:center;justify-content:center;font-size:14px;color:var(--t3);background:#ddd}.nav-right{display:flex;align-items:center;gap:10px}.year-select{padding:6px 12px;border-radius:var(--r1);border:1px solid var(--bc);font-size:13px;color:var(--t2);background:var(--wh);cursor:pointer}
.fbar{max-width:1400px;margin:0 auto;padding:20px 24px 0}.frow{display:flex;align-items:center;gap:24px;margin-bottom:14px;flex-wrap:wrap}.flab{font-size:13px;font-weight:500;color:var(--t2);white-space:nowrap;flex-shrink:0}.btns{display:flex;flex-wrap:wrap;gap:6px}.fbtn{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;font-size:13px;color:var(--t2);background:var(--wh);border:1px solid var(--bc);transition:all .2s;white-space:nowrap;cursor:pointer}.fbtn:hover{border-color:var(--p);color:var(--p)}.fbtn.active{background:var(--p);color:white;border-color:var(--p);box-shadow:0 2px 8px rgba(0,82,217,.25)}.cbtn{padding:4px 12px;border-radius:16px;font-size:12px;color:var(--t2);background:var(--wh);border:1px solid var(--bc);transition:all .2s;white-space:nowrap;cursor:pointer}.cbtn:hover{border-color:var(--ph);color:var(--ph)}.cbtn.active{background:linear-gradient(135deg,var(--p),#2670F0);color:white;border-color:transparent}.inline-group{display:flex;align-items:center;gap:8px}.inline-group label{font-size:13px;font-weight:500;color:var(--t2);white-space:nowrap}.btn-group{display:flex;gap:4px}.bg-btn{padding:4px 12px;border-radius:14px;font-size:12px;color:var(--t2);background:var(--wh);border:1px solid var(--bc);transition:all .2s;cursor:pointer}.bg-btn:hover{border-color:var(--ph)}.bg-btn.active{background:var(--pl);color:var(--p);border-color:var(--p);font-weight:600}
.stats{max-width:1400px;margin:0 auto;padding:0 24px;display:flex;align-items:center;background:linear-gradient(135deg,#fff,#f0f5ff);border-radius:var(--r2);padding:18px 28px;margin-bottom:20px;border:1px solid rgba(0,82,217,.08);box-shadow:var(--ss)}.st-item{text-align:center;flex:1}.st-num{font-size:26px;font-weight:900;color:var(--p);line-height:1.2;letter-spacing:-.5px}.st-lbl{font-size:12px;color:var(--t3);margin-top:2px}.st-div{width:1px;height:40px;background:var(--bc);margin:0 16px}
.news-section{max-width:1400px;margin:0 auto;padding:0 24px 60px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:20px}
.card{background:var(--wh);border-radius:var(--r2);padding:24px;border:1px solid var(--bc);cursor:pointer;transition:all .3s;display:flex;flex-direction:column;position:relative;overflow:hidden}.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--p),var(--ph));opacity:0;transition:opacity .3s}.card:hover{transform:translateY(-3px);box-shadow:var(--sl);border-color:transparent}.card:hover::before{opacity:1}
.chdr{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}.src-tag{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:500;padding:3px 10px;border-radius:12px;white-space:nowrap}.date-text{font-size:12px;color:var(--t3);flex:1}.imp-badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;white-space:nowrap}
.ctitle{font-size:17px;font-weight:700;line-height:1.45;color:var(--t1);margin-bottom:10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .2s}.card:hover .ctitle{color:var(--p)}.csum{font-size:14px;line-height:1.65;color:var(--t2);margin-bottom:14px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.ctags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}.tag{font-size:11px;padding:3px 10px;border-radius:12px;background:var(--bg);color:var(--t2);border:1px solid var(--bc);white-space:nowrap}.cftr{display:flex;justify-content:space-between;align-items:center;padding-top:14px;border-top:1px solid #f0f0f0}.cat-tag{font-size:12px;color:var(--p);background:var(--pl);padding:3px 10px;border-radius:10px;font-weight:500}.visit-link{font-size:13px;color:var(--a)!important;font-weight:500;opacity:0;transition:opacity .2s}.card:hover .visit-link{opacity:1}
.tl-group{margin-bottom:24px}.tl-summary-bar{background:var(--wh);border-radius:var(--r2);padding:14px 20px;margin-bottom:20px;border:1px solid var(--bc);font-size:14px;color:var(--t2)}.tl-year{font-size:18px;font-weight:900;color:var(--p);margin-bottom:12px;padding-left:16px;border-left:4px solid var(--p);letter-spacing:1px;cursor:pointer;user-select:none;display:flex;align-items:center;gap:6px;transition:border-color .2s}.tl-y-toggle{font-size:11px;color:var(--t3);transition:transform .2s;width:16px;text-align:center}.tl-year:hover{color:var(--ph)}.tl-items{display:flex;flex-direction:column;gap:10px;transition:max-height .35s ease,opacity .25s ease;overflow:hidden}.tl-items.collapsed{max-height:0!important;opacity:0;margin:0;padding:0}.tl-item{display:flex;gap:16px;background:var(--wh);border-radius:var(--r2);padding:20px 24px;border:1px solid var(--bc);cursor:pointer;transition:all .25s}.tl-item:hover{transform:translateX(4px);box-shadow:var(--sm);border-color:var(--ph)}.tl-dot{width:12px;height:12px;border-radius:50%;margin-top:6px;flex-shrink:0;box-shadow:0 0 0 3px rgba(0,82,217,.15)}.tl-cnt{flex:1;min-width:0}.tl-meta{display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:12px;color:var(--t3)}.tl-item h4{font-size:16px;font-weight:700;line-height:1.4;color:var(--t1);margin-bottom:6px;transition:color .2s}.tl-item:hover h4{color:var(--p)}.tl-item>p{font-size:14px;color:var(--t2);line-height:1.55;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 20px;text-align:center}
.pagination{display:flex;justify-content:center;margin-top:32px}.pgn-inn{display:flex;align-items:center;gap:4px}.pg-btn{min-width:38px;height:38px;border-radius:var(--r1);font-size:13px;font-weight:500;color:var(--t2);background:var(--wh);border:1px solid var(--bc);display:flex;align-items:center;justify-content:center;padding:0 12px;transition:all .2s;cursor:pointer}.pg-btn:not(:disabled):hover{border-color:var(--p);color:var(--p)}.pg-btn.active{background:var(--p);color:white;border-color:var(--p);box-shadow:0 2px 8px rgba(0,82,217,.25)}.pg-btn:disabled{opacity:.35;cursor:not-allowed}    '.pg-dots{color:var(--t3);padding:0 6px;font-size:13px}.pg-jump-wrap{display:inline-flex;align-items:center;gap:6px;margin-left:10px;padding-left:14px;border-left:1px solid var(--bc)}.pg-jump-wrap select{height:38px;padding:0 28px 0 12px;border-radius:var(--r1);border:1px solid var(--bc);font-size:13px;font-weight:500;color:var(--t2);background:var(--wh) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%230052D9' fill='none' stroke-width='1.5'/%3E%3C/svg%3E") no-repeat right 10px center;background-size:10px;-webkit-appearance:none;-moz-appearance:none;appearance:none;cursor:pointer;transition:border-color .2s,box-shadow .2s;outline:none}.pg-jump-wrap select:hover,.pg-jump-wrap select:focus{border-color:var(--p);box-shadow:0 0 0 3px rgba(0,82,217,.15)}.pg-jump-btn{padding:5px 14px;font-size:13px;color:#fff;background:#0052D9;border:none;border-radius:6px;cursor:pointer;transition:all .2s;white-space:nowrap}.pg-jump-btn:hover{background:#0046ba;transform:translateY(-1px)}.pg-jump-btn:active{transform:scale(.97)}'
.modal-overlay{position:fixed;inset:0;z-index:-9999!important;background:rgba(0,0,0,.45);backdrop-filter:blur(4px);display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;height:0!important;overflow:hidden!important}.modal-overlay.show{display:flex!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;z-index:1000!important;height:auto!important;overflow-y:auto!important;align-items:flex-start;justify-content:center;padding:40px 20px}.modal-dialog{background:var(--wh);border-radius:var(--r3);max-width:720px;width:100%;position:relative;box-shadow:0 20px 60px rgba(0,0,0,.2);animation:slideUp .3s ease;margin:auto}@keyframes slideUp{from{transform:translateY(30px);opacity:0}to{transform:translateY(0);opacity:1}}.modal-close{position:absolute;top:16px;right:16px;z-index:5;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--t3);background:var(--bg);transition:all .2s;cursor:pointer}.modal-close:hover{background:var(--d);color:white}.modal-body{padding:36px 36px 28px}.dtl-title{font-size:24px;font-weight:900;line-height:1.35;color:var(--t1);margin-bottom:12px;font-family:"Tencent Sans",sans-serif}.dtl-sum{font-size:16px;color:var(--t2);line-height:1.6}.dtl-body{margin-top:20px;font-size:15px;line-height:1.85;color:var(--t1);white-space:pre-line}.dtl-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px;padding-top:16px;border-top:1px solid var(--bc)}.dtl-actions{display:flex;gap:12px;justify-content:flex-end;margin-top:24px}.act-btn{padding:10px 24px;border-radius:var(--r1);font-size:14px;font-weight:600;transition:all .2s;cursor:pointer;text-align:center;text-decoration:none;display:inline-block}.act-btn.primary{background:var(--p);color:white}.act-btn.primary:hover{background:var(--ph);box-shadow:0 4px 12px rgba(0,82,217,.3)}.act-btn.visit{background:var(--a)!important;color:white!important}.act-btn.visit:hover{background:#00915e!important}
.footer{background:var(--t1);color:rgba(255,255,255,.6);padding:24px;text-align:center;font-size:13px;margin-top:auto}.footer strong{color:white}
@media(max-width:1024px){.grid{grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}.nav-inner{flex-wrap:wrap;gap:12px;padding:10px 20px}.nav-center{order:3;max-width:100%;flex-basis:100%}.search-bar{width:100%}}
@media(max-width:768px){.grid{grid-template-columns:1fr}.stats{flex-direction:column;gap:12px;padding:16px}.st-div{display:none}.cftr{flex-direction:column;align-items:flex-start;gap:8px}.visit-link{opacity:1!important}.frow{gap:12px}}"""

# JS - ALL innerHTML uses backtick template literals. Raw string avoids Python issues.
js = r'''(function(){"use strict";
var rawData=document.getElementById("appData").textContent;
var ALL_DATA=JSON.parse(rawData);
console.log("ADADD loaded:",ALL_DATA.length,"items");
var SOURCES={weibo:{name:"微博",icon:"📱",color:"#E6162D"},zhihu:{name:"知乎",icon:"💡",color:"#0084FF"},wechat:{name:"微信公众号",icon:"📨",color:"#07C160"},github:{name:"GitHub",icon:"🐙",color:"#24292E"},"tech-media":{name:"技术社区",icon:"⚙️",color:"#ED7B2D"},"industry-media":{name:"行业媒体",icon:"📰",color:"#0052D9"},"36kr":{name:"36氪",icon:"🚀",color:"#0066CC"}};
var IMPACTS={high:{label:"🔴 高",color:"#E02020"},medium:{label:"🟠 中",color:"#ED7B2D"},low:{label:"🟢 低",color:"#00A870"}};
var PAGE_SIZE=12;
var state={source:"",category:"",impact:"",sort:"latest",view:"cards",page:1,search:""};
var $=function(id){return document.getElementById(id)};
var filterBar=$("filterBar"),statsBar=$("statsBar"),newsSection=$("newsSection");
var searchInput=$("searchInput"),clearSearch=$("clearSearch"),yearSelect=$("yearSelect");
/* Modal: dynamically created on first use, not in static HTML */
var modalOverlay=null,modalClose=null,modalBody=null;
function ensureModal(){
  if(modalOverlay)return;
  var ov=document.createElement("div");
  ov.className="modal-overlay";ov.id="modalOverlay";
  ov.innerHTML='<div class="modal-dialog"><button class="modal-close" id="modalClose" style="position:absolute;top:16px;right:16px;z-index:5;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;color:#999;background:#f5f7fa;cursor:pointer;border:none;transition:all .2s">×</button><div class="modal-body" id="modalBody"></div></div>';
  document.body.appendChild(ov);
  modalOverlay=ov;modalClose=$("modalClose");modalBody=$("modalBody");
  modalClose.addEventListener("click",function(){modalOverlay.style.display="none";modalOverlay.classList.remove("show")});
  ov.addEventListener("click",function(e){if(e.target===ov){ov.style.display="none";ov.classList.remove("show")}});
  document.addEventListener("keydown",function(e){if(e.key==="Escape"){ov.style.display="none";ov.classList.remove("show")}});
}

function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}
var SOURCE_SEARCH_TPL={"zhihu":"https://www.zhihu.com/search?type=content&q=","36kr":"https://36kr.com/search/articles?q=","weibo":"https://s.weibo.com/weibo?q=","github":"https://github.com/search?q=","wechat":"https://weixin.sogou.com/weixin?type=2&query=","tech-media":"https://www.google.com/search?q=site:juejin.cn+","industry-media":"https://www.google.com/search?q=site:madisonboom.com+OR+site:meihua.info+OR+site:adquan.com+"};
function getSearchQuery(item){var kw=item.category||"";if(item.tags&&item.tags.length>0)kw+=" "+item.tags[0];var t=item.title.replace(/\d{4}年.*?[白皮书|指南|观察|复盘|报告|洞察]/g,"").replace(/[：:].*/g,"");kw=t.trim()||kw;return kw}
function getNewsUrl(item){if(item.url&&item.url.length>0&&(!item.url.includes("search?"))&&(!item.url.includes("/search/")))return item.url;var src=item.source||"",tpl=SOURCE_SEARCH_TPL[src],q=getSearchQuery(item);if(tpl)return tpl+encodeURIComponent(q);return "https://www.google.com/search?q="+encodeURIComponent(q)+" 广告 营销 2026"}
function openRealSearch(q){window.open("https://www.google.com/search?q="+encodeURIComponent(q+" 广告 营销 AI 程序化 2026")+"&hl=zh-CN","_blank")}

function getFilteredData(){
  return ALL_DATA.filter(function(x){
    if(state.source&&x.source!==state.source)return false;
    if(state.category&&x.category!==state.category)return false;
    if(state.impact&&x.impact!==state.impact)return false;
    if(yearSelect.value&&x.date.substring(0,4)!==yearSelect.value)return false;
    if(state.search){
      var q=state.search.toLowerCase();
      if(x.title.toLowerCase().indexOf(q)<0&&x.summary.toLowerCase().indexOf(q)<0&&!x.tags.some(function(t){return t.toLowerCase().indexOf(q)>=0}))return false;
    }
    return true;
  }).sort(function(a,b){
    if(state.sort==="latest")return b.date.localeCompare(a.date);
    if(state.sort==="oldest")return a.date.localeCompare(b.date);
    return({high:3,medium:2,low:1}[b.impact]||0)-({high:3,medium:2,low:1}[a.impact]||0);
  });
}

/* ===== RENDER FILTERS (template literals only) ===== */
function renderFilters(){
  var srcKeys=Object.keys(SOURCES);
  var sc={};ALL_DATA.forEach(function(x){sc[x.source]=(sc[x.source]||0)+1});
  var sb=`<button class="fbtn${state.source===''?' active':''}" data-a="src" data-v="">全部</button>`;
  srcKeys.forEach(function(k){
    var s=SOURCES[k];sb+=`<button class="fbtn${state.source===k?' active':''}" data-a="src" data-v="${k}">${s.icon}${s.name}<span style="font-size:11px;background:rgba(0,0,0,0.06);padding:1px 7px;border-radius:10px;margin-left:4px">${sc[k]||0}</span></button>`;
  });

  var cats=[],cc={};ALL_DATA.forEach(function(x){if(cats.indexOf(x.category)<0)cats.push(x.category);cc[x.category]=(cc[x.category]||0)+1});cats.sort();
  var cb=`<button class="cbtn${state.category===''?' active':''}" data-a="cat" data-v="">全部</button>`;
  cats.forEach(function(c){cb+=`<button class="cbtn${state.category===c?' active':''}" data-a="cat" data-v="${esc(c)}">${esc(c)} <span style="font-size:10px;color:#999">${cc[c]||0}</span></button>`});

  var ia=state.impact===""?" active":"",ih=state.impact==="high"?" active":"",im=state.impact==="medium"?" active":"",il=state.impact==="low"?" active":"";
  var sl=state.sort==="latest"?" active":"",so=state.sort==="oldest"?" active":"",si=state.sort==="impact"?" active":"";
  var vc=state.view==="cards"?" active":"",vt=state.view==="timeline"?" active":"";

  filterBar.innerHTML=`<div class="frow"><div class="flab">📂 来源：</div><div class="btns">${sb}</div></div>`+
    `<div class="frow"><div class="flab">🏷 分类：</div><div class="btns">${cb}</div></div>`+
    `<div class="frow">
      <div class="inline-group"><label>⚡ 影响力：</label><div class="btn-group">
        <button class="bg-btn${ia}" data-a="imp" data-v="">全部</button>
        <button class="bg-btn${ih}" data-a="imp" data-v="high">🔴 高</button>
        <button class="bg-btn${im}" data-a="imp" data-v="medium">🟠 中</button>
        <button class="bg-btn${il}" data-a="imp" data-v="low">🟢 低</button>
      </div></div>
      <div class="inline-group"><label>🔄 排序：</label><div class="btn-group">
        <button class="bg-btn${sl}" data-a="sort" data-v="latest">最新优先</button>
        <button class="bg-btn${so}" data-a="sort" data-v="oldest">最早优先</button>
        <button class="bg-btn${si}" data-a="sort" data-v="impact">高影响力</button>
      </div></div>
      <div class="inline-group"><label>👁 展示形式：</label><div class="btn-group">
        <button class="bg-btn${vc}" data-a="view" data-v="cards">卡片</button>
        <button class="bg-btn${vt}" data-a="view" data-v="timeline">时间轴</button>
      </div></div></div>`;
}

function renderStats(){
  var d=getFilteredData(),yrs={},srcs={};
  ALL_DATA.forEach(function(x){yrs[x.date.substring(0,4)]=1;srcs[x.source]=1});
  statsBar.innerHTML=`<div class="st-item"><div class="st-num">${ALL_DATA.length}</div><div class="st-lbl">总资讯数</div></div><div class="st-div"></div><div class="st-item"><div class="st-num">${d.length}</div><div class="st-lbl">当前筛选</div></div><div class="st-div"></div><div class="st-item"><div class="st-num">${Object.keys(yrs).length}</div><div class="st-lbl">覆盖年份</div></div><div class="st-div"></div><div class="st-item"><div class="st-num">${Object.keys(srcs).length}</div><div class="st-lbl">数据来源</div></div>`;
}

function renderNews(){
  var d=getFilteredData();
  if(d.length===0){newsSection.innerHTML=`<div class="empty-state"><p style="font-size:48px">🔍</p><p style="font-size:16px;color:var(--t2)">没有找到相关资讯</p><p style="font-size:13px;color:var(--t3)">调整筛选条件或点击「全网搜」按钮搜索互联网</p></div>`;return;}
    var total=Math.ceil(d.length/PAGE_SIZE);if(state.page>total)state.page=total;if(state.page<1)state.page=1;
  var start=(state.page-1)*PAGE_SIZE,pg=d.slice(start,start+PAGE_SIZE);
  var pageOptions="";for(var pi=1;pi<=total;pi++){pageOptions+=`<option value="${pi}"${pi===state.page?" selected":""}>第${pi}页</option>`;}

  if(state.view==="timeline"){
    var grps={};d.forEach(function(x){var y=x.date.substring(0,4);if(!grps[y])grps[y]=[];grps[y].push(x)});
    var h='<div class="tl-summary-bar">共 <b>'+d.length+'</b> 条 · <b>'+Object.keys(grps).length+'</b> 个年份</div>';
    Object.keys(grps).sort().reverse().forEach(function(y){
      var items=grps[y];
      h+=`<div class="tl-group"><div class="tl-year" data-tl-y="${y}"><span class="tl-y-toggle">▶</span><span>${y}年</span><span style="font-size:13px;font-weight:400;color:var(--t3);margin-left:8px">${items.length}条</span></div><div class="tl-items" id="tl-items-${y}">`;
      items.forEach(function(it){
        var sr=SOURCES[it.source]||{name:it.source,icon:"📌",color:"#999"},ip=IMPACTS[it.impact]||{label:it.impact,color:"#999"};
        h+=`<div class="tl-item" data-url="${it.url}"><div class="tl-dot" style="background:${sr.color}"></div><div class="tl-cnt"><div class="tl-meta"><span class="src-tag" style="background:${sr.color}20;color:${sr.color}">${sr.icon}${sr.name}</span><span>${it.date}</span><span class="imp-badge" style="background:${ip.color}20;color:${ip.color}">${ip.label}</span></div><h4>${esc(it.title)}</h4><p>${esc(it.summary)}</p><div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">${it.tags.map(function(t){return`<span class="tag">${esc(t)}</span>`}).join('')}<a href="${it.url}" target="_blank" style="color:#00A870;font-size:13px;font-weight:500;margin-left:auto">访问原文 ↗</a></div></div></div>`;
      });h+="</div></div>";
    });
    newsSection.innerHTML=h;
    /* bind toggle events */
    newsSection.querySelectorAll(".tl-year").forEach(function(el){
      el.addEventListener("click",function(){
        var y=this.dataset.tlY;
        var items=document.getElementById("tl-items-"+y);
        var tg=this.querySelector(".tl-y-toggle");
        if(items.classList.contains("collapsed")){
          items.classList.remove("collapsed");tg.textContent="▶";this.style.borderLeftColor="var(--p)";
        }else{
          items.classList.add("collapsed");tg.textContent="▼";this.style.borderLeftColor="var(--bc)";
        }
      });
    });
  }else{
    var ch="";pg.forEach(function(it){
      var sr=SOURCES[it.source]||{name:it.source,icon:"📌",color:"#999"},ip=IMPACTS[it.impact]||{label:it.impact,color:"#999"};
      ch+=`<div class="card" data-id="${it.id}" data-url="${it.url}"><div class="chdr"><span class="src-tag" style="background:${sr.color}20;color:${sr.color}">${sr.icon}${sr.name}</span><span class="date-text">${it.date}</span><span class="imp-badge" style="background:${ip.color}20;color:${ip.color}">${ip.label}</span></div><h3 class="ctitle">${esc(it.title)}</h3><p class="csum">${esc(it.summary)}</p><div class="ctags">${it.tags.map(function(t){return`<span class="tag">${esc(t)}</span>`}).join('')}</div><div class="cftr"><span class="cat-tag">${esc(it.category)}</span><a class="visit-link" href="${it.url}" target="_blank">访问原文 ↗</a></div></div>`;
    });
    var nh=`<div class="grid">${ch}</div>`;
    if(total>1){nh+=`<div class="pagination"><div class="pgn-inn">`;nh+=`<button class="pg-btn" data-p="${state.page-1}"${state.page<=1?" disabled":""}>‹</button>`;
      var sp=Math.max(1,state.page-2),ep=Math.min(total,state.page+2);
      for(var i=sp;i<=ep;i++){nh+=`<button class="pg-btn${i===state.page?" active":""}" data-p="${i}">${i}</button>`}
      if(ep<total){if(ep<total-1)nh+=`<span class="pg-dots">...</span>`;nh+=`<button class="pg-btn" data-p="${total}">${total}</button>`}
      nh+=`<button class="pg-btn" data-p="${state.page+1}"${state.page>=total?" disabled":""}>›</button>`;
      nh+=`<div class="pg-jump-wrap"><select id="pageJumpSelect">${pageOptions}</select><button class="pg-jump-btn" data-a="jump">跳转</button></div>`;
      nh+="</div></div>";}
    newsSection.innerHTML=nh;
  }
}

/* ===== EVENTS ===== */
filterBar.addEventListener("click",function(e){
  var btn=e.target.closest("[data-a]");
  if(!btn)return;
  var a=btn.dataset.a,v=btn.dataset.v;
  if(a==="src")state.source=v;else if(a==="cat")state.category=v;
  else if(a==="imp")state.impact=v;else if(a==="sort")state.sort=v;
  else if(a==="view")state.view=v;
  else if(a==="jump"){var sel=document.getElementById("pageJumpSelect");if(sel){var jp=parseInt(sel.value);if(!isNaN(jp)&&jp>=1&&jp<=total){state.page=jp;renderNews();return;}}}
  state.page=1;renderAll();
});

newsSection.addEventListener("click",function(e){
  var bp=e.target.closest("[data-p]");
  if(bp){state.page=parseInt(bp.dataset.p);renderNews();return;}
  if(e.target.closest(".visit-link"))return;
  var ut=e.target.closest("[data-url]");
  if(ut){window.open(ut.dataset.url,"_blank");return;}
  var cld=e.target.closest(".card");
  if(cld&&!e.target.closest(".visit-link]")&&!e.target.closest("[data-url]")){
    var item=ALL_DATA.find(function(x){return x.id===parseInt(cld.dataset.id)});
    if(item)openModal(item);
  }
});

newsSection.addEventListener("change",function(e){
  if(e.target.id==="pageJumpSelect"){var val=parseInt(e.target.value);if(val&&val>0){state.page=val;renderNews();}}
});
searchInput.addEventListener("input",function(){state.search=this.value.trim();clearSearch.style.display=state.search?"flex":"none";state.page=1;renderAll()});
clearSearch.addEventListener("click",function(){searchInput.value="";state.search="";clearSearch.style.display="none";state.page=1;renderAll()});
yearSelect.addEventListener("change",function(){state.page=1;renderAll()});
document.getElementById("globalSearchBtn").addEventListener("click",function(){var q=searchInput.value.trim();if(q)openRealSearch(q)});
searchInput.addEventListener("keydown",function(e){
  if(e.key==="Enter"){var q=e.target.value.trim();if(!q)return;if(getFilteredData().length===0)openRealSearch(q);else{state.search=q;state.page=1;renderAll()}}
});
/* ===== MODAL (template literal) ===== */
function openModal(item){
  ensureModal();
  var sr=SOURCES[item.source]||{name:item.source,icon:"📌",color:"#999"};
  var ip=IMPACTS[item.impact]||{label:item.impact,color:"#999"};
  var origTitle = item.original_title ? `<div style="font-size:13px;color:var(--t3);margin-bottom:6px;padding:8px 12px;background:var(--bg);border-radius:var(--r1);border-left:3px solid var(--p)"><span style="font-weight:600;color:var(--p)">📄 原文标题：</span>${esc(item.original_title)}</div>` : "";
  modalBody.innerHTML=`
    <div style="margin-bottom:24px">
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
        <span class="src-tag" style="background:${sr.color}20;color:${sr.color};font-size:13px;padding:4px 12px">${sr.icon}${sr.name}</span>
        <span class="imp-badge" style="background:${ip.color}20;color:${ip.color};font-size:12px;padding:3px 10px">${ip.label}</span>
        <span class="cat-tag" style="font-size:13px;padding:4px 12px">${esc(item.category)}</span>
      </div>
      <div style="font-size:13px;color:var(--t3);margin-bottom:10px">${item.date}</div>
      ${origTitle}
      <h2 class="dtl-title">${esc(item.title)}</h2>
      <p class="dtl-sum">${esc(item.summary)}</p>
    </div>
    <div class="dtl-body">${esc(item.body)}</div>
    <div class="dtl-tags">${item.tags.map(function(t){return`<span class="tag">${esc(t)}</span>`}).join('')}</div>
    <div class="dtl-actions">
      <a href="${item.url}" target="_blank" class="act-btn visit">访问原文 ↗</a>
      <button class="act-btn primary" onclick="navigator.clipboard.writeText(location.href)">复制链接</button>
    </div>`;
  modalOverlay.style.display="flex";
}

function fillYearSelect(){var ys={};ALL_DATA.forEach(function(x){ys[x.date.substring(0,4)]=1});Object.keys(ys).sort().reverse().forEach(function(y){var o=document.createElement("option");o.value=y;o.text=y+"年";yearSelect.add(o)})}

function renderAll(){renderFilters();renderStats();renderNews()}
fillYearSelect();
renderAll();
console.log("ADADD initialized ✓");
})();
'''

html_parts = [
    '<!DOCTYPE html>', '<html lang="zh-CN">', '<head>',
    '<meta charset="UTF-8">', '<meta name="viewport" content="width=device-width,initial-scale=1.0">',
    '<title>ADADD · 广告行业资讯聚合平台</title>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">',
    '<style>'+css+'</style>', '</head>', '<body>',
    '<header class="navbar"><div class="nav-inner">',
    '<div class="logo"><div class="logo-icon-wrap"><div class="logo-ring"></div><div class="logo-ring-inner"></div><div class="logo-center">AD<span class="lp">+</span></div></div><span class="logo-text">ADADD</span><span class="logo-sub">AD+ 广告行业资讯聚合</span></div>',
    '<div class="nav-center"><div class="search-bar" id="searchBar">',
    '🔍 <input type="text" id="searchInput" placeholder="搜索广告行业资讯、技术、趋势... (Enter本地 / 无结果自动全网搜)" autocomplete="off">',
    '<button class="clear-search" id="clearSearch">×</button>',
    '<button id="globalSearchBtn" style="padding:4px 12px;border-radius:14px;font-size:11px;color:#00A870;background:#EDFAF3;border:1px solid #00A870;cursor:pointer;white-space:nowrap;font-weight:500;">全网搜 🔍</button>',
    '</div></div>',
    '<div class="nav-right"><select class="year-select" id="yearSelect"><option value="">全部年份</option></select></div>',
    '</div></header>',
    '<div class="fbar" id="filterBar"></div>',
    '<div class="stats" id="statsBar"></div>',
    '<section class="news-section" id="newsSection"></section>',
    '<footer class="footer"><strong>AD+</strong> (Ad Add) · 广告行业资讯聚合平台 · Developed with ❤️ by nelsonmeng</footer>',
    '<script type="application/json" id="appData">'+data_safe+'</script>',
    '<script>'+js+'</script>',
    '</body>', '</html>'
]

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_parts))

size = os.path.getsize(OUT_PATH)
print(f'✅ Generated {OUT_PATH} ({size:,} bytes)')
print(f'   Items: {len(data_list)}, Years: {years}')
