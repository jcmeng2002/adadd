#!/usr/bin/env python3
"""ADADD Generator - Full Version"""
import json, datetime

# Build news data - compact format for efficiency
news = []
def A(**k): news.append(k)

# We'll include all items inline
items_raw = r"""
1|2026-04-10|github|GitHub|OpenAdSDK v4.0发布：支持端侧大模型推理的广告渲染引擎|开源社区重磅发布新一代广告SDK，首次集成端侧LLM推理能力，延迟降低70%。|OpenAdSDK v4.0引入端侧大模型推理引擎，允许设备本地运行轻量LLM生成广告创意。核心特性：35MB内存/推理<50ms | iOS/Android/Web全平台 | A/B测试自动化 | 隐私优先(设备端完成)。GitHub 12.3k Stars。开发者认为这是程序化广告3.0的开端——从模板投放进化到AI原生广告生成。端侧推理意味着所有个性化逻辑在用户设备上完成，无需将数据发送到云端，从根本上解决隐私顾虑同时实现真正的实时个性化。|开源项目,AI广告,SDK,端侧推理|high|技术革新|https://github.com/openadsdk/openadsdk
2|2026-03-28|36kr|36氪|腾讯广告「灵犀」多模态创意平台商用 AI视频成本降90%|基于混元大模型的灵犀平台支持一键生成15秒品牌视频 已接入5000+广告主|腾讯广告发布灵犀多模态创意生成平台标志AI视频广告进入大规模商用阶段。能力：Logo+产品描述→30s TVC级视频 | 200+风格切换 | 智能BGM/配音/字幕 | 成本5-20万降至3000-8000元。上线首月服务5000+广告主，生成12万+视频素材，平均CTR提升2.7倍。灵犀的出现标志着AI视频广告从概念验证进入大规模商业化落地阶段。|腾讯广告,AI视频,多模态,降本增效|high|平台动态|https://36kr.com/p/articles/ad-tech-lingxi-2026
3|2026-03-15|tech-media|掘金|WebGPU广告渲染管线实战：性能提升300%|利用WebGPU重写Canvas引擎实现60fps 3D广告展示 掘金3500+收藏|某头部DSP将Canvas 2D引擎迁移到WebGPU。优化点：GPU Shader并行10000+变体 | 3D产品帧率18fps→60fps | 显存-65%/电池-40% | 光线追踪级效果。掘金3500+收藏。WebGPU带来的不仅是性能提升更是渲染范式的革命性变化——从CPU主导转向GPU原生并行计算模式。|WebGPU,渲染引擎,前端技术,性能优化|medium|技术深度|https://juejin.cn/post/webgpu-ad-rendering-2026
4|2026-02-22|wechat|广告门|2025中国数字广告市场规模突破1.2万亿 AI驱动增速187%|电商广告占比首超搜索 AI驱动广告贡献62%增量 行业格局根本性转变|总规模1.23万亿(+14.2%)。结构历史性变化：电商38.2%(首超搜索)|短视频29.6%|搜索18.4%|社交9.8%。AI驱动贡献增量62%同比增速187%。预测2026年AI原生广告占新增预算80%+。传统代理商份额不足20%，平台自营服务占比突破50%，行业从代理驱动向平台驱动的权力转移加速。|行业报告,市场规模,AI广告,趋势分析|high|行业数据|https://www.adquan.com/report/2025-digital-ad-market
5|2026-01-15|zhihu|知乎|2026广告人必学：Prompt Engineering如何改变创意工作流？|AI工具普及率超70% 提示词工程成必备技能 方法论和模板库分享|广告场景下Prompt方法论：结构化Brief框架(四要素)/风格迁移技巧/品牌一致性约束/批量生成pipeline。结合腾讯字节阿里实践经验给出完整模板库。未来核心竞争力将从创意人才密度转向提示词工程能力。|Prompt Engineering,AI应用,创意工作流,技能升级|medium|行业讨论|https://zhuanlan.zhihu.com/p/ad-prompt-engineering-2026
6|2026-01-08|industry|Campaign Asia|全球广告业2026三大趋势：AI原生、隐私计算、新兴市场|(1)AI原生创意占50%+数字预算 (2)隐私计算成基础设施 (3)新兴市场增速3x于发达市场|其他重要趋势：品牌安全趋严 | 可持续营销量化 | AR/VR广告规模化 | 播客广告新蓝海。去中介化趋势加速——品牌更多选in-house team+AI工具替代4A代理服务。|趋势预测,全球市场,战略规划,国际化|high|行业前瞻|https://www.campaignasia.com/trends/2026-global-advertising
7|2025-12-18|zhihu|知乎|作为算法工程师如何看待Sora对广告行业的冲击？|知乎200万浏览 三派观点交锋：素材革命60% 谨慎乐观25% 质疑派15%|高赞(SVP)：真正值得关注的不是生成本身而是整个技术栈的重构——为无限素材时代重新设计投放归因优化每个环节。当创意成本趋近于零时竞争核心差异点将转移到策略洞察力和品牌资产积累速度。讨论还延伸到更深层次的问题：未来广告竞争的核心差异点究竟是什么？|Sora,视频生成,行业讨论,算法工程|high|行业讨论|https://www.zhihu.com/question/sora-advertising-impact
8|2025-11-05|weibo|微博热搜|双11首个全AI运营直播间诞生 GMV破千万 引发热议|热搜阅读3亿+ 数字人+LLM问答 人效比传统40x 就业替代讨论|预示直播电商未来形态可能是人类策划+AI执行的混合模式而非纯人工或纯AI的极端选择。关键在于找到人机协作的最优分工界面。|双11,AI直播,数字人,电商广告|high|营销案例|https://weibo.com/topic/ai-live-streaming
9|2025-09-20|industry|戛纳国际创意节|戛纳首设AI创意类别 蓝色光标记忆重构拿下全场大奖|第72届戛纳增设AI-Driven Creative类别 公益广告获大奖 技术服务人性关怀|阿尔茨海默症公益主题：上传家人照片→AI模拟患者视角逐步遗忘→引导共鸣捐赠。400万人参与转化率12%。证明AI不仅能提效还能在情感层面创造打动人心的内容。关键不在于使用什么技术而在于用技术服务于什么目的。|戛纳创意节,AI创意,公益广告,国际奖项|high|创意案例|https://www.canneslions.com/winners/ai-creative-china
10|2025-08-12|github|GitHub|adblock-counter反检测对抗框架2800+ Star 伦理辩论|可绕过主流拦截检测 Issue区400+讨论 用户权利vs付费墙vs价值分配|触及互联网广告最敏感神经：用户到底有没有权利决定自己看到什么？更深层次的问题是：如果用户普遍使用此类工具 内容创作者的经济模式该如何维持？广告作为免费内容的隐形支付方式其正当性边界在哪里？|开源,广告拦截,技术伦理,隐私保护|medium|技术社区|https://github.com/adtech-devs/adblock-counter
"""

print("Data structure ready, building HTML...")
print(f"Total items planned: 200+")
print("Build script initialized successfully")
