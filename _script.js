<script>(function(){"use strict";
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
var modalOverlay=$("modalOverlay"),modalClose=$("modalClose"),modalBody=$("modalBody");

function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}
var SOURCE_SEARCH_TPL={"zhihu":"https://www.zhihu.com/search?type=content&q=","36kr":"https://36kr.com/search/articles?q=","weibo":"https://s.weibo.com/weibo?q=","github":"https://github.com/search?q=","wechat":"https://weixin.sogou.com/weixin?type=2&query=","tech-media":"https://www.google.com/search?q=site:juejin.cn+","industry-media":"https://www.google.com/search?q=site:madisonboom.com+OR+site:meihua.info+OR+site:adquan.com+"};
function getSearchQuery(item){var kw=item.category||"";if(item.tags&&item.tags.length>0)kw+=" "+item.tags[0];var t=item.title.replace(/\d{4}年.*?[白皮书|指南|观察|复盘|报告|洞察]/g,"").replace(/[：:].*/g,"");kw=t.trim()||kw;return kw}
function getNewsUrl(item){if(item.url&&item.url.length>0&&(!item.url.includes("search?"))&&(!item.url.includes("/search/")))return item.url;var src=item.source||"",tpl=SOURCE_SEARCH_TPL[src],q=getSearchQuery(item);if(tpl)return tpl+encodeURIComponent(q);return "https://www.google.com/search?q="+encodeURIComponent(q)+" 广告 营销 2026")}
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

  var ia=state.impact===""?"":"",ih=state.impact==="high"?" active":"",im=state.impact==="medium"?" active":"",il=state.impact==="low"?" active":"";
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
        <button class="bg-btn${sl}" data-a="sort" data-val="latest">最新优先</button>
        <button class="bg-btn${so}" data-a="sort" data-val="oldest">最早优先</button>
        <button class="bg-btn${si}" data-a="sort" data-val="impact">高影响力</button>
      </div></div>
      <div class="inline-group"><label>👁 展示形式：</label><div class="btn-group">
        <button class="bg-btn${vc}" data-a="view" data-val="cards">卡片</button>
        <button class="bg-btn${vt}" data-a="view" data-val="timeline">时间轴</button>
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

  if(state.view==="timeline"){
    var grps={};pg.forEach(function(x){var y=x.date.substring(0,4);if(!grps[y])grps[y]=[];grps[y].push(x)});
    var h="";Object.keys(grps).sort().reverse().forEach(function(y){
      h+=`<div class="tl-group"><div class="tl-year">${y}年</div><div class="tl-items">`;
      grps[y].forEach(function(it){
        var sr=SOURCES[it.source]||{name:it.source,icon:"📌",color:"#999"},ip=IMPACTS[it.impact]||{label:it.impact,color:"#999"};
        h+=`<div class="tl-item" data-url="${it.url}"><div class="tl-dot" style="background:${sr.color}"></div><div class="tl-cnt"><div class="tl-meta"><span class="src-tag" style="background:${sr.color}20;color:${sr.color}">${sr.icon}${sr.name}</span><span>${it.date}</span><span class="imp-badge" style="background:${ip.color}20;color:${ip.color}">${ip.label}</span></div><h4>${esc(it.title)}</h4><p>${esc(it.summary)}</p><div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">${it.tags.map(function(t){return`<span class="tag">${esc(t)}</span>`}).join('')}<a href="${it.url}" target="_blank" style="color:#00A870;font-size:13px;font-weight:500;margin-left:auto">访问原文 ↗</a></div></div></div>`;
      });h+="</div></div>";
    });newsSection.innerHTML=h;
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
      nh+=`<button class="pg-btn" data-p="${state.page+1}"${state.page>=total?" disabled":""}>›</button>`;nh+="</div></div>";}
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

searchInput.addEventListener("input",function(){state.search=this.value.trim();clearSearch.style.display=state.search?"flex":"none";state.page=1;renderAll()});
clearSearch.addEventListener("click",function(){searchInput.value="";state.search="";clearSearch.style.display="none";state.page=1;renderAll()});
yearSelect.addEventListener("change",function(){state.page=1;renderAll()});
document.getElementById("globalSearchBtn").addEventListener("click",function(){var q=searchInput.value.trim();if(q)openRealSearch(q)});
searchInput.addEventListener("keydown",function(e){
  if(e.key==="Enter"){var q=e.target.value.trim();if(!q)return;if(getFilteredData().length===0)openRealSearch(q);else{state.search=q;state.page=1;renderAll()}}
});
modalClose.addEventListener("click",function(){modalOverlay.classList.remove("show")});
modalOverlay.addEventListener("click",function(e){if(e.target===modalOverlay)modalOverlay.classList.remove("show")});

/* ===== MODAL (template literal) ===== */
function openModal(item){
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
  modalOverlay.classList.add("show");
}

function fillYearSelect(){var ys={};ALL_DATA.forEach(function(x){ys[x.date.substring(0,4)]=1});Object.keys(ys).sort().reverse().forEach(function(y){var o=document.createElement("option");o.value=y;o.text=y+"年";yearSelect.add(o)})}

function renderAll(){renderFilters();renderStats();renderNews()}
fillYearSelect();
renderAll();
console.log("ADADD initialized ✓");
})();
</script>
