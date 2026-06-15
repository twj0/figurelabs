#!/usr/bin/env python3
"""
分析 FigureLabs.ai 对话类型和功能
从 HAR 文件中提取对话相关的 API 调用
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def analyze_chat_requests(har_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """分析 HAR 文件中的聊天相关请求"""
    with open(har_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get('log', {}).get('entries', [])

    # 按 API 类型分类
    categorized = defaultdict(list)

    keywords = {
        'session': [],
        'message': [],
        'model': [],
        'agent': [],
        'scene': [],
        'action': [],
        'status': [],
        'thinking': [],
    }

    for entry in entries:
        req = entry['request']
        resp = entry['response']
        url = req['url']

        # 只关注 chat.figurelabs.ai 的 API
        if 'chat.figurelabs.ai' not in url or '/app-api/' not in url:
            continue

        # 提取路径
        path = url.split('/app-api/')[-1].split('?')[0]

        # 分类
        for keyword, items in keywords.items():
            if keyword in path.lower():
                request_data = {}
                response_data = {}

                # 提取请求体
                if req.get('postData'):
                    post_text = req['postData'].get('text', '')
                    try:
                        request_data = json.loads(post_text)
                    except:
                        request_data = {'raw': post_text[:200]}

                # 提取响应体
                resp_content = resp.get('content', {}).get('text', '')
                if resp_content:
                    try:
                        response_data = json.loads(resp_content)
                    except:
                        response_data = {'raw': resp_content[:200]}

                categorized[keyword].append({
                    'method': req['method'],
                    'path': path,
                    'url': url,
                    'status': resp['status'],
                    'request': request_data,
                    'response': response_data,
                })
                break

    return dict(categorized)


def print_analysis(har_files: List[Path]):
    """打印分析结果"""
    print("=" * 80)
    print("FigureLabs.ai 对话类型分析")
    print("=" * 80)

    all_categories = defaultdict(list)

    for har_file in har_files:
        print(f"\n分析文件: {har_file.name}")
        categories = analyze_chat_requests(har_file)

        for category, requests in categories.items():
            all_categories[category].extend(requests)

    print("\n" + "=" * 80)
    print("汇总结果")
    print("=" * 80)

    for category, requests in sorted(all_categories.items()):
        print(f"\n【{category.upper()}】 共 {len(requests)} 个请求\n")

        # 去重显示路径
        unique_paths = {}
        for req in requests:
            path = req['path']
            if path not in unique_paths:
                unique_paths[path] = req

        for path, req in unique_paths.items():
            print(f"  {req['method']} /{path}")

            # 显示关键参数
            if req['request']:
                print(f"    请求参数:")
                for key, value in list(req['request'].items())[:5]:
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + '...'
                    print(f"      {key}: {value}")

            if req['response'] and req['response'].get('code') == 0:
                data = req['response'].get('data', {})
                if isinstance(data, dict):
                    print(f"    响应字段: {list(data.keys())[:10]}")
                elif isinstance(data, list) and data:
                    print(f"    响应列表: {len(data)} 项")
                else:
                    print(f"    响应数据: {str(data)[:100]}")

            print()


def extract_chat_features(har_files: List[Path]):
    """提取对话功能特征"""
    print("\n" + "=" * 80)
    print("对话功能特征提取")
    print("=" * 80)

    features = {
        'scenes': set(),
        'action_types': set(),
        'models': set(),
        'agents': set(),
    }

    for har_file in har_files:
        with open(har_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data.get('log', {}).get('entries', []):
            req = entry['request']

            # 提取 scene
            if 'scene=' in req['url']:
                scene = req['url'].split('scene=')[1].split('&')[0]
                features['scenes'].add(scene)

            # 提取 actionType
            post_data = req.get('postData', {}).get('text', '')
            if 'actionType' in post_data:
                try:
                    # 尝试 JSON
                    data = json.loads(post_data)
                    if 'actionType' in data:
                        features['action_types'].add(data['actionType'])
                except:
                    # 尝试 form-data
                    if 'actionType' in post_data:
                        import re
                        match = re.search(r'actionType["\s:]+([A-Z_]+)', post_data)
                        if match:
                            features['action_types'].add(match.group(1))

            # 提取响应中的信息
            resp_text = entry['response'].get('content', {}).get('text', '')
            if resp_text:
                try:
                    resp_json = json.loads(resp_text)

                    # 提取 models
                    if isinstance(resp_json.get('data'), list):
                        for item in resp_json['data']:
                            if isinstance(item, dict) and 'name' in item:
                                features['models'].add(item['name'])

                    # 提取 agents
                    if 'agent' in resp_text.lower():
                        if isinstance(resp_json.get('data'), dict):
                            agent_id = resp_json['data'].get('agentId')
                            if agent_id is not None:
                                features['agents'].add(agent_id)

                except:
                    pass

    print("\n【Scene 场景】")
    for scene in sorted(features['scenes']):
        print(f"  - {scene}")

    print("\n【Action Type 动作类型】")
    for action in sorted(features['action_types']):
        print(f"  - {action}")

    print("\n【Models 可用模型】")
    for model in sorted(features['models']):
        print(f"  - {model}")

    print("\n【Agents 代理】")
    for agent in sorted(features['agents']):
        print(f"  - Agent ID: {agent}")


if __name__ == '__main__':
    har_dir = Path(__file__).parent.parent / '01HttpArchive'
    har_files = list(har_dir.glob('chat.*.har'))

    if not har_files:
        print("未找到 chat 相关的 HAR 文件")
        sys.exit(1)

    print(f"找到 {len(har_files)} 个 HAR 文件\n")

    # 分析请求
    print_analysis(har_files)

    # 提取功能特征
    extract_chat_features(har_files)
