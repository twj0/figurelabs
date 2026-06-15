#!/usr/bin/env python3
"""
提取 HAR 文件中的实际消息发送样本
"""
import json
import re
from pathlib import Path


def extract_message_samples():
    """提取消息发送样本"""
    har_dir = Path(__file__).parent.parent / '01HttpArchive'
    har_files = list(har_dir.glob('chat.*.har'))

    print("=" * 80)
    print("FigureLabs.ai 消息发送样本提取")
    print("=" * 80)

    for har_file in har_files:
        print(f"\n文件: {har_file.name}\n")

        with open(har_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for entry in data['log']['entries']:
            req = entry['request']
            resp = entry['response']

            if '/plot/chat/message' not in req['url'] or req['method'] != 'POST':
                continue

            count += 1
            print(f"[样本 {count}]")
            print(f"URL: {req['url']}")
            print(f"Method: {req['method']}")
            print(f"Status: {resp['status']}\n")

            # 提取 Content-Type
            content_type = None
            for header in req['headers']:
                if header['name'].lower() == 'content-type':
                    content_type = header['value']
                    break

            print(f"Content-Type: {content_type}\n")

            # 提取 POST body
            post_data = req.get('postData', {}).get('text', '')

            if 'multipart/form-data' in (content_type or ''):
                # 解析 multipart 字段
                print("Multipart Fields:")

                # 查找所有 name="xxx" 后面的值
                boundary = re.search(r'------[a-z0-9]+', post_data)
                if boundary:
                    boundary_str = boundary.group(0)
                    parts = post_data.split(boundary_str)

                    for part in parts:
                        name_match = re.search(r'name="([^"]+)"', part)
                        if name_match:
                            field_name = name_match.group(1)

                            # 提取值
                            lines = part.split('\r\n')
                            for i, line in enumerate(lines):
                                if line == '' and i + 1 < len(lines):
                                    value = lines[i + 1]
                                    if value and not value.startswith('------'):
                                        if len(value) > 100:
                                            value = value[:100] + '...'
                                        print(f"  {field_name}: {value}")
                                    break

            # 提取响应
            resp_text = resp.get('content', {}).get('text', '')
            if resp_text:
                print(f"\nResponse (first 300 chars):")
                print(resp_text[:300])

                # 提取 messageId
                message_id = re.search(r'"messageId":"(\d+)"', resp_text)
                if message_id:
                    print(f"\nExtracted Message ID: {message_id.group(1)}")

            print("\n" + "-" * 80 + "\n")


if __name__ == '__main__':
    extract_message_samples()
