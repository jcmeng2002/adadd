#!/usr/bin/env python3
"""ADADD V6 Build Script - 生成自包含HTML页面（数据全部内联）

修复版：正确处理JS字符串转义，确保语法100%合法
"""
import json, os, sys, re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, 'data', 'news_data.json')
TPL_FILE = os.path.join(BASE, 'v6_template.html')
OUT_FILE = os.path.join(BASE, 'index.html')

def main():
    # 1) Load data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    print(f'Loaded {len(raw_data)} items')

    # 2) Extract unique years
    years = sorted(set((d.get('date') or '')[:4] for d in raw_data if d.get('date')))

    # 3) Generate year <option> HTML
    year_opts = '<option value="">全部年份</option>'
    for y in years:
        year_opts += f'<option value="{y}">{y}年</option>'

    # 4) Read template
    with open(TPL_FILE, 'r', encoding='utf-8') as f:
        tpl = f.read()

    # 5) CRITICAL: Safely embed JSON as JavaScript literal
    # Use json.dumps() which correctly escapes all special chars including </script>
    js_data_str = json.dumps(raw_data, ensure_ascii=False, separators=(',', ':'))

    # Additional safety: prevent any </script> sequence in data breaking the HTML tag
    js_data_str = js_data_str.replace('</', '<\\/')  # escape closing tags within script

    # Verify: parse back to confirm it's valid
    verify = json.loads(js_data_str.replace('<\\/', '</'))
    assert len(verify) == len(raw_data), "Data verification failed!"

    # 6) Replace placeholders
    html = tpl.replace('{{ITEM_COUNT}}', str(len(raw_data)))
    html = html.replace('{{YEAR_OPTIONS}}', year_opts)
    html = html.replace('{{JS_DATA}}', js_data_str)

    # 7) Write output
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f'Generated index.html ({size_kb:.0f} KB)')
    
    # Stats summary
    sources = set(d['source'] for d in raw_data)
    categories = set(d['category'] for d in raw_data)
    print(f'Sources:{len(sources)} Cats:{len(categories)} Years:{years}')

if __name__ == '__main__':
    main()
