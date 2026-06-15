#!/usr/bin/env python3
"""
查找 HAR 文件中的注册相关请求
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def find_registration_apis(har_path):
    """查找注册、登录、认证相关的所有请求"""
    with open(har_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get('log', {}).get('entries', [])

    keywords = [
        'register', 'signup', 'sign-up', 'sign_up',
        'login', 'signin', 'sign-in', 'sign_in',
        'auth', 'oauth', 'token', 'verify',
        'checkLogin', 'member', 'user'
    ]

    print(f"\n{'='*80}")
    print(f"分析文件: {Path(har_path).name}")
    print(f"{'='*80}\n")

    found_requests = []

    for entry in entries:
        req = entry['request']
        resp = entry['response']
        url = req['url']
        parsed = urlparse(url)

        # 检查 URL 和路径
        url_lower = url.lower()
        if any(kw in url_lower for kw in keywords):
            found_requests.append({
                'method': req['method'],
                'url': url,
                'status': resp['status'],
                'request': req,
                'response': resp
            })

    if not found_requests:
        print("未发现注册/认证相关请求")
        return

    print(f"发现 {len(found_requests)} 个认证相关请求:\n")

    for i, item in enumerate(found_requests, 1):
        print(f"{i}. {item['method']} {item['url']}")
        print(f"   状态: {item['status']}")

        # 显示请求头（认证相关）
        auth_headers = [h for h in item['request']['headers']
                       if 'auth' in h['name'].lower() or 'token' in h['name'].lower()]
        if auth_headers:
            print("   认证请求头:")
            for h in auth_headers:
                print(f"     {h['name']}: {h['value'][:50]}...")

        # 显示请求体
        if item['request'].get('postData'):
            post_data = item['request']['postData']
            print(f"   请求体 (MIME: {post_data.get('mimeType', 'unknown')}):")
            text = post_data.get('text', '')
            if text:
                # 尝试解析 JSON
                try:
                    parsed_json = json.loads(text)
                    print(f"     {json.dumps(parsed_json, indent=6, ensure_ascii=False)}")
                except:
                    print(f"     {text[:200]}")

        # 显示响应体
        content = item['response']['content']
        if content.get('text'):
            print(f"   响应体:")
            try:
                resp_json = json.loads(content['text'])
                print(f"     {json.dumps(resp_json, indent=6, ensure_ascii=False)}")
            except:
                print(f"     {content['text'][:200]}")

        print()

def main():
    import glob
    har_files = glob.glob("01HttpArchive/*.har")

    for har_file in har_files:
        find_registration_apis(har_file)

if __name__ == '__main__':
    main()
