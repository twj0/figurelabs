#!/usr/bin/env python3
"""
HAR 文件深度分析工具
分析 HTTP Archive 文件，提取网站结构、API、性能等信息
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime

class HARAnalyzer:
    def __init__(self, har_path):
        self.har_path = Path(har_path)
        self.data = self._load_har()
        self.entries = self.data.get('log', {}).get('entries', [])

    def _load_har(self):
        with open(self.har_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def analyze(self):
        """执行完整分析"""
        print(f"\n{'='*80}")
        print(f"HAR 文件分析: {self.har_path.name}")
        print(f"{'='*80}\n")

        self._basic_info()
        self._domain_analysis()
        self._api_analysis()
        self._resource_analysis()
        self._performance_analysis()
        self._security_analysis()
        self._headers_analysis()

    def _basic_info(self):
        print("【基本信息】")
        print(f"  总请求数: {len(self.entries)}")

        if self.entries:
            start_time = min(e['startedDateTime'] for e in self.entries)
            print(f"  开始时间: {start_time}")

            durations = [e.get('time', 0) for e in self.entries]
            print(f"  总耗时: {sum(durations):.2f}ms")
        print()

    def _domain_analysis(self):
        print("【域名分析】")
        domains = defaultdict(int)
        for entry in self.entries:
            url = entry['request']['url']
            domain = urlparse(url).netloc
            domains[domain] += 1

        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        for domain, count in sorted_domains[:10]:
            print(f"  {domain}: {count} 请求")
        print()

    def _api_analysis(self):
        print("【API 分析】")
        apis = []
        for entry in self.entries:
            req = entry['request']
            url = req['url']
            parsed = urlparse(url)

            # 识别 API 请求（常见模式）
            if any(p in parsed.path for p in ['/api/', '/app-api/', '/v1/', '/v2/', '/graphql']):
                apis.append({
                    'method': req['method'],
                    'url': url,
                    'status': entry['response']['status'],
                    'time': entry.get('time', 0)
                })

        if apis:
            print(f"  发现 {len(apis)} 个 API 请求:")
            for api in apis[:15]:
                print(f"    {api['method']} {api['url'][:80]}")
                print(f"      └─ 状态: {api['status']}, 耗时: {api['time']:.2f}ms")
        else:
            print("  未发现明显的 API 请求")
        print()

    def _resource_analysis(self):
        print("【资源类型分析】")
        resources = defaultdict(lambda: {'count': 0, 'size': 0})

        for entry in self.entries:
            mime = entry['response']['content'].get('mimeType', 'unknown')
            size = entry['response']['content'].get('size', 0)

            # 简化 MIME 类型
            if 'javascript' in mime or 'ecmascript' in mime:
                category = 'JavaScript'
            elif 'css' in mime:
                category = 'CSS'
            elif 'image' in mime:
                category = 'Image'
            elif 'html' in mime:
                category = 'HTML'
            elif 'json' in mime:
                category = 'JSON'
            elif 'font' in mime:
                category = 'Font'
            else:
                category = 'Other'

            resources[category]['count'] += 1
            resources[category]['size'] += size

        for res_type, stats in sorted(resources.items(), key=lambda x: x[1]['size'], reverse=True):
            size_kb = stats['size'] / 1024
            print(f"  {res_type}: {stats['count']} 个, {size_kb:.2f} KB")
        print()

    def _performance_analysis(self):
        print("【性能分析】")
        timings = []
        for entry in self.entries:
            timings.append({
                'url': entry['request']['url'],
                'time': entry.get('time', 0),
                'blocked': entry.get('timings', {}).get('blocked', 0),
                'dns': entry.get('timings', {}).get('dns', 0),
                'connect': entry.get('timings', {}).get('connect', 0),
                'send': entry.get('timings', {}).get('send', 0),
                'wait': entry.get('timings', {}).get('wait', 0),
                'receive': entry.get('timings', {}).get('receive', 0)
            })

        if timings:
            sorted_timings = sorted(timings, key=lambda x: x['time'], reverse=True)
            print(f"  最慢的 5 个请求:")
            for t in sorted_timings[:5]:
                print(f"    {t['url'][:70]}")
                print(f"      └─ 总耗时: {t['time']:.2f}ms (DNS: {t['dns']:.2f}ms, Wait: {t['wait']:.2f}ms, Receive: {t['receive']:.2f}ms)")

            avg_time = sum(t['time'] for t in timings) / len(timings)
            print(f"\n  平均请求耗时: {avg_time:.2f}ms")
        print()

    def _security_analysis(self):
        print("【安全分析】")
        http_urls = []
        third_party_domains = set()
        main_domain = None

        for entry in self.entries:
            url = entry['request']['url']
            parsed = urlparse(url)

            if not main_domain:
                main_domain = parsed.netloc

            if parsed.scheme == 'http':
                http_urls.append(url)

            if parsed.netloc != main_domain:
                third_party_domains.add(parsed.netloc)

        if http_urls:
            print(f"  ⚠️ 发现 {len(http_urls)} 个不安全的 HTTP 请求")
        else:
            print("  ✓ 所有请求使用 HTTPS")

        if third_party_domains:
            print(f"\n  第三方域名 ({len(third_party_domains)} 个):")
            for domain in list(third_party_domains)[:10]:
                print(f"    - {domain}")
        print()

    def _headers_analysis(self):
        print("【请求头分析】")
        headers_count = defaultdict(int)
        cookies_found = False

        for entry in self.entries:
            for header in entry['request']['headers']:
                headers_count[header['name']] += 1
                if header['name'].lower() == 'cookie':
                    cookies_found = True

        print("  最常见的请求头:")
        for header, count in sorted(headers_count.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"    {header}: {count} 次")

        print(f"\n  Cookies: {'✓ 存在' if cookies_found else '✗ 未发现'}")
        print()

    def export_summary(self, output_path=None):
        """导出分析摘要到 JSON"""
        if not output_path:
            output_path = self.har_path.with_suffix('.analysis.json')

        summary = {
            'har_file': str(self.har_path),
            'analyzed_at': datetime.now().isoformat(),
            'total_requests': len(self.entries),
            'domains': {},
            'apis': [],
            'resources': {}
        }

        # 域名统计
        for entry in self.entries:
            domain = urlparse(entry['request']['url']).netloc
            summary['domains'][domain] = summary['domains'].get(domain, 0) + 1

        # API 统计
        for entry in self.entries:
            url = entry['request']['url']
            if any(p in urlparse(url).path for p in ['/api/', '/v1/', '/v2/']):
                summary['apis'].append({
                    'method': entry['request']['method'],
                    'url': url,
                    'status': entry['response']['status']
                })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"✓ 分析结果已导出到: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("用法: python har_analyzer.py <har文件路径> [--export]")
        sys.exit(1)

    har_path = sys.argv[1]
    export = '--export' in sys.argv

    analyzer = HARAnalyzer(har_path)
    analyzer.analyze()

    if export:
        analyzer.export_summary()

if __name__ == '__main__':
    main()

