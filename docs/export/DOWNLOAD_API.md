# 图片下载 API 分析

## 1. 支持的文件格式

| 格式 | 端点 | 状态 |
|------|------|------|
| **PNG** | `GET /api/file-proxy?url=<s3>` | HAR 确认 |
| **JPG** | `GET /api/file-proxy?url=<s3>` | HAR 确认（同 PNG 代理，扩展名重命名） |
| **SVG** | `POST /app-api/plot/image/svg` | HAR 确认 |
| **PPTX** | `POST /app-api/plot/image/pptx` | 端点推断，**待 HAR 验证** |

> PPTX 端点由 SVG 规律推断（`/app-api/plot/image/<fmt>`）。验证方法：在网页 UI 点击 PPTX 导出按钮，同时抓 HAR，然后检查实际请求 URL 与 payload。

---

## 2. 核心下载流程

```
1. 发送消息
   POST /app-api/plot/chat/message (multipart/form-data)
   → SSE 返回 messageId  ← 必须保存！

2. 轮询（3s 间隔）
   GET /app-api/plot/chat/message/status?messageId=<id>
   status=0 生成中 | status=1 完成 | status=2 失败
   完成时 fileUrl[] 含 S3 预签名 PNG URL

3. 按格式下载（均需 messageId + token）
   PNG/JPG → GET /api/file-proxy?url=<s3-url>
   SVG     → POST /app-api/plot/image/svg {"imageUrl":[<url>]} → GET <svg-s3-url>
   PPTX    → POST /app-api/plot/image/pptx {"imageUrl":[<url>]} → GET <pptx-s3-url>
```

**补下载**：`message/status` 无状态，任何时候用同账号 token + messageId 均可调用，服务端每次重签 S3 URL。

---

## 3. Python API

```python
from src.export import ExportClient

client = ExportClient(access_token)

# 单格式
client.download(message_id, fmt="png", output_dir="./out", filename="fig")
client.download(message_id, fmt="svg", output_dir="./out", filename="fig")

# 多格式一次性
client.download_all(message_id, formats=["png", "svg"], output_dir="./out")
```

底层格式模块也可直接调用：

```python
from src.export import png, svg
from src.export._session import make_session

session = make_session(access_token)
png_url = "https://figurelabs-images-us-east-1.s3..."

png.download(session, png_url, "./out", "fig")
svg.download(session, png_url, "./out", "fig")
```

---

## 4. CLI

```bash
# 单格式
uv run python -m src.export <token> <message_id> -f png -o ./out

# 多格式
uv run python -m src.export <token> <message_id> -f png svg pptx -o ./out -n fig

# 生成 + 等待，再手动导出
uv run python -m src.chat <token> generate -m "..." --wait
uv run python -m src.export <token> <message_id> -f png svg
```

---

## 5. 数据来源

- `01HttpArchive/chat.figurelabs.ai_2026_06_15_20_25_21.har` — PNG 代理、SVG OCR
- `01HttpArchive/chat.figurelabs.ai_Archive [26-06-14 12-42-23].har` — SVG 转换完整流程
- 分析日期：2026-06-15
