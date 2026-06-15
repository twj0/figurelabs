#!/usr/bin/env python3
"""
深度分析 FigureLabs.ai 消息格式和参数
"""
import json
import re
from pathlib import Path
from typing import Dict, Any


def parse_multipart_form_data(text: str) -> Dict[str, Any]:
    """解析 multipart/form-data 格式"""
    fields = {}

    # 提取 boundary
    boundary_match = re.search(r'------[a-z0-9]+', text)
    if not boundary_match:
        return fields

    boundary = boundary_match.group(0)
    parts = text.split(boundary)

    for part in parts:
        if 'Content-Disposition' not in part:
            continue

        # 提取字段名
        name_match = re.search(r'name="([^"]+)"', part)
        if not name_match:
            continue

        field_name = name_match.group(1)

        # 提取值 (在两个换行符之后)
        lines = part.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '' and i + 1 < len(lines):
                value = lines[i + 1].strip()
                if value and value != boundary.strip('-'):
                    fields[field_name] = value
                break

    return fields


def analyze_message_formats(har_path: Path):
    """分析消息格式"""
    with open(har_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n{'='*80}")
    print(f"分析文件: {har_path.name}")
    print(f"{'='*80}\n")

    message_samples = []

    for entry in data.get('log', {}).get('entries', []):
        req = entry['request']
        resp = entry['response']

        # 只看消息发送请求
        if '/plot/chat/message' not in req['url'] or req['method'] != 'POST':
            continue

        # 解析请求
        post_data = req.get('postData', {})
        mime_type = post_data.get('mimeType', '')
        text = post_data.get('text', '')

        sample = {
            'url': req['url'],
            'method': req['method'],
            'mime_type': mime_type,
            'headers': {h['name']: h['value'] for h in req['headers']},
            'status': resp['status'],
        }

        if 'multipart/form-data' in mime_type:
            sample['format'] = 'multipart/form-data'
            sample['fields'] = parse_multipart_form_data(text)
        elif 'application/json' in mime_type:
            sample['format'] = 'application/json'
            try:
                sample['fields'] = json.loads(text)
            except:
                sample['fields'] = {}
        else:
            sample['format'] = 'unknown'
            sample['raw'] = text[:200]

        # 解析响应 (SSE 流)
        resp_text = resp.get('content', {}).get('text', '')
        if resp_text:
            sample['response'] = resp_text[:500]

            # 尝试提取 messageId
            message_id_match = re.search(r'"messageId":"(\d+)"', resp_text)
            if message_id_match:
                sample['message_id'] = message_id_match.group(1)

        message_samples.append(sample)

    return message_samples


def extract_all_fields(samples):
    """提取所有字段"""
    all_fields = set()
    field_values = {}

    for sample in samples:
        if 'fields' in sample:
            for key, value in sample['fields'].items():
                all_fields.add(key)
                if key not in field_values:
                    field_values[key] = set()
                if isinstance(value, str) and len(value) < 100:
                    field_values[key].add(value)

    return all_fields, field_values


if __name__ == '__main__':
    har_dir = Path(__file__).parent.parent / '01HttpArchive'
    har_files = list(har_dir.glob('chat.*.har'))

    all_samples = []

    for har_file in har_files:
        samples = analyze_message_formats(har_file)
        all_samples.extend(samples)

    print(f"\n{'='*80}")
    print(f"消息格式汇总")
    print(f"{'='*80}\n")

    print(f"总共发现 {len(all_samples)} 个消息发送请求\n")

    # 分析格式
    formats = {}
    for sample in all_samples:
        fmt = sample.get('format', 'unknown')
        if fmt not in formats:
            formats[fmt] = []
        formats[fmt].append(sample)

    for fmt, samples in formats.items():
        print(f"【{fmt}】 {len(samples)} 个样本\n")

        # 提取字段
        all_fields, field_values = extract_all_fields(samples)

        print(f"  必需字段:")
        for field in sorted(all_fields):
            values = field_values.get(field, set())
            if values and len(values) < 10:
                print(f"    - {field}: {', '.join(sorted(values))}")
            else:
                print(f"    - {field}: <用户输入>")

        # 显示一个完整样本
        if samples:
            sample = samples[0]
            print(f"\n  样本:")
            print(f"    URL: {sample['url']}")
            print(f"    Format: {sample['format']}")
            if 'fields' in sample:
                print(f"    Fields:")
                for key, value in sample['fields'].items():
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + '...'
                    print(f"      {key}: {value}")
            if 'message_id' in sample:
                print(f"    Message ID: {sample['message_id']}")

        print()
