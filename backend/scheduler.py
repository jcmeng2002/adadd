#!/usr/bin/env python3
"""
ADADD 定时任务调度器
- 定时抓取新数据
- 数据更新与合并
- 健康检查
"""

import os
import sys
import time
import json
import logging
import signal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('adadd.scheduler')

# 全局运行标志
running = True


def signal_handler(sig, frame):
    global running
    logger.info("🛑 收到停止信号，正在优雅关闭...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def load_existing_data():
    """加载已有数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def merge_data(existing, new_items):
    """合并新旧数据，基于标题去重"""
    existing_titles = set(item.get('title', '') for item in existing)
    
    added = 0
    for item in new_items:
        title = item.get('title', '')
        if title not in existing_titles:
            # 新数据插入到最前面（最新）
            existing.insert(0, item)
            existing_titles.add(title)
            added += 1
    
    # 重新分配ID和排序
    existing.sort(key=lambda x: x.get('date', ''), reverse=True)
    for i, item in enumerate(existing):
        item['id'] = i + 1
    
    logger.info(f"   合并完成: 新增 {added} 条，总计 {len(existing)} 条")
    return existing


def save_data(data):
    """保存数据到文件"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 数据已保存: {DATA_FILE} ({len(data)}条)")


def run_crawl():
    """执行一次抓取任务"""
    try:
        from crawler import ADCrawler
        
        crawler = ADCrawler()
        new_data = crawler.run_all()
        
        # 与现有数据合并
        existing = load_existing_data()
        merged = merge_data(existing, new_data)
        
        save_data(merged)
        
        return len(new_data), len(merged)
    
    except Exception as e:
        logger.error(f"❌ 抓取失败: {e}")
        return 0, 0


def run_generate():
    """执行一次数据生成（补充历史数据）"""
    try:
        from generate_data import generate_news_data
        
        logger.info("📝 执行数据生成...")
        new_data = generate_news_data(220)
        
        existing = load_existing_data()
        merged = merge_data(existing, new_data)
        
        save_data(merged)
        
        return len(new_data), len(merged)
    
    except Exception as e:
        logger.error(f"❌ 生成失败: {e}")
        return 0, 0


def health_check():
    """健康检查：验证数据和API状态"""
    try:
        data_file_exists = os.path.exists(DATA_FILE)
        data_size = os.path.getsize(DATA_FILE) if data_file_exists else 0
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'dataFile': DATA_FILE,
            'dataExists': data_file_exists,
            'dataSizeKB': round(data_size / 1024, 1),
            'recordCount': len(data),
            'dateRange': {
                'earliest': min(d.get('date','') for d in data) if data else '',
                'latest': max(d.get('date','') for d in data) if data else ''
            } if data else {},
        }
        
        logger.info(f"✅ Health check passed: {len(data)} records")
        return status
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}


def main():
    """主调度循环"""
    global running
    
    import argparse
    parser = argparse.ArgumentParser(description='ADADD Scheduler')
    parser.add_argument('--mode', choices=['daemon', 'once', 'generate'], default='daemon',
                        help='运行模式: daemon=持续循环 once=执行一次 generate=仅生成数据')
    parser.add_argument('--interval', type=int, default=CRAWL_INTERVAL_HOURS * 3600,
                        help='抓取间隔秒数 (默认6小时)')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("  ADADD 定时任务调度器 v2.0")
    print("=" * 60)
    print(f"  模式: {args.mode}")
    print(f"  数据文件: {DATA_FILE}")
    if args.mode == 'daemon':
        print(f"  抓取间隔: {args.interval // 3600}小时{(args.interval % 3600) // 60}分钟")
    print("=" * 60 + "\n")
    
    if args.mode == 'generate':
        # 仅生成数据模式
        added, total = run_generate()
        print(f"\n✅ 完成！生成/新增 {added} 条，总计 {total} 条")
        health_check()
        return
    
    elif args.mode == 'once':
        # 单次执行模式
        added, total = run_crawl()
        print(f"\n✅ 完成！抓取新增 {added} 条，总计 {total} 条")
        health_check()
        return
    
    else:
        # 守护进程模式
        logger.info("🔄 启动守护进程模式...")
        
        cycle_count = 0
        while running:
            cycle_count += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"📅 第 {cycle_count} 轮调度 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info('='*50)
            
            try:
                # 1. 健康检查
                health = health_check()
                if health.get('status') != 'healthy':
                    logger.warning("⚠️ 健康检查未通过，尝试重新生成数据...")
                    run_generate()
                
                # 2. 执行抓取
                added, total = run_crawl()
                logger.info(f"📊 本轮结果: 新增{added}条 | 总计{total}条")
                
                # 3. 等待下一轮
                logger.info(f"😴 等待 {args.interval}s 后进行下一轮...")
                
                # 分段sleep以支持快速退出
                sleep_chunk = 60
                elapsed = 0
                while running and elapsed < args.interval:
                    time.sleep(min(sleep_chunk, args.interval - elapsed))
                    elapsed += sleep_chunk
                
            except Exception as e:
                logger.error(f"❌ 调度异常: {e}")
                logger.error("等待5分钟后重试...")
                time.sleep(300)
        
        logger.info("👋 调度器已停止")


if __name__ == '__main__':
    main()
