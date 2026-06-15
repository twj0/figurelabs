# FigureLabs.ai 对话类型分析报告

## 1. 概述

通过分析 HAR 文件，识别出 FigureLabs.ai 的对话系统架构和功能特征。

---

## 2. 核心 API 端点

### 2.1 会话管理

| 端点 | 方法 | 功能 | 返回 |
|------|------|------|------|
| `/app-api/plot/chat/session/create` | POST | 创建新会话 | `sessionId` (字符串) |
| `/app-api/plot/chat/session/history` | POST | 获取历史会话列表 | `{list, total}` |

**创建会话参数**:
```json
{
  "title": "A pristine, high-density academic...",
  "agentId": 0
}
```

### 2.2 消息发送

| 端点 | 方法 | 功能 | 返回 |
|------|------|------|------|
| `/app-api/plot/chat/message` | POST | 发送消息 | SSE 流 (包含 `messageId`) |

**消息格式**: `multipart/form-data`

**必需字段**:
- `actionType`: `NORMAL_CHAT` (动作类型)
- `sessionId`: 会话 ID
- `scene`: `normal_chat` (场景类型)
- `text`: 用户输入的文本内容

**可选字段**:
- `modelId`: 模型 ID (数字)
- `ratio`: 图像比例 (如 `16:9`)
- `style`: 风格参数
- `title`: 标题 (首次消息可能需要)
- `firstMessage`: 是否首次消息 (布尔值)

### 2.3 状态查询

| 端点 | 方法 | 功能 |
|------|------|------|
| `/app-api/plot/chat/message/status?messageId=xxx` | GET | 查询消息生成状态 |
| `/app-api/plot/chat/message/thinking/status?messageId=xxx` | GET | 查询思考状态 (多步骤) |

**状态响应字段**:
```json
{
  "id": "...",
  "userId": "...",
  "sessionId": "...",
  "type": 0,
  "status": 0,
  "text": "生成的内容",
  "messageType": 0,
  "fileUrl": "...",
  "fileType": "...",
  "createTime": 123456789
}
```

**思考状态响应字段**:
```json
{
  "id": "...",
  "messageId": "...",
  "status": 0,
  "currentStep": 1,
  "totalSteps": 5,
  "stepName": "分析需求",
  "stepDesc": "正在理解用户意图...",
  "createTime": 123456789
}
```

### 2.4 模型管理

| 端点 | 方法 | 功能 |
|------|------|------|
| `/app-api/plot/chat/model/list?scene=iiterature` | GET | 获取可用模型列表 |

**响应结构**:
```json
{
  "code": 0,
  "data": {
    "models": [...],
    "availableModelIds": [7, 12]
  }
}
```

---

## 3. 对话场景分类

### 3.1 Scene 场景

从 HAR 文件中识别到的场景类型:

- **`iiterature`** (文献/学术场景)
- **`normal_chat`** (普通对话场景)

### 3.2 Action Type 动作类型

- **`NORMAL_CHAT`**: 普通对话

*注: 可能存在其他动作类型，如 `REGENERATE`, `EDIT`, `CONTINUE` 等，但当前 HAR 文件未捕获*

---

## 4. 模型分类

### 4.1 学科领域模型

FigureLabs.ai 按学科领域对模型进行分类:

| 类别 | 说明 |
|------|------|
| **Biology** | 生物学 |
| **Chemistry** | 化学 |
| **CS** | 计算机科学 |
| **Geosciences** | 地球科学 |
| **Medicine** | 医学 |
| **Physics** | 物理学 |
| **Protocols** | 协议/方法 |
| **STEM Education** | STEM 教育 |
| **General** | 通用模型 |
| **Favorites** | 收藏夹 |

### 4.2 可用模型

免费账户可访问的模型 ID:
- **Model ID 7**: Nano Banana Pro (Google) - 30s 生成
- **Model ID 12**: GPT Image 2 (OpenAI) - 90s 生成

---

## 5. 消息发送完整示例

### 5.1 最简消息 (使用默认参数)

```python
import requests

files = {
    'actionType': (None, 'NORMAL_CHAT'),
    'sessionId': (None, '2066463076126683137'),
    'scene': (None, 'normal_chat'),
    'text': (None, 'Generate a simple flowchart diagram.')
}

response = requests.post(
    'https://chat.figurelabs.ai/app-api/plot/chat/message',
    headers={'Authorization': 'Bearer <token>'},
    files=files
)
```

### 5.2 完整消息 (指定模型和样式)

```python
files = {
    'actionType': (None, 'NORMAL_CHAT'),
    'sessionId': (None, '2066018095083679746'),
    'scene': (None, 'normal_chat'),
    'text': (None, 'A pristine, high-density academic...'),
    'modelId': (None, '12'),           # GPT Image 2
    'ratio': (None, '16:9'),           # 图像比例
    'style': (None, 'academic'),       # 风格
    'title': (None, 'IEEE 33-bus'),    # 标题
    'firstMessage': (None, 'true')     # 首次消息
}
```

---

## 6. SSE 响应流格式

消息发送后，服务端返回 SSE (Server-Sent Events) 流:

```
data:{"eventType":"INIT","sessionId":"...","messageId":"2066018148024184833","messageType":0,"status":0,...}

data:{"eventType":"PROGRESS","currentStep":1,"totalSteps":5,"stepName":"分析需求",...}

data:{"eventType":"PROGRESS","currentStep":2,"totalSteps":5,"stepName":"生成图像",...}

data:{"eventType":"COMPLETED","text":"生成完成","fileUrl":"https://...",...}
```

### 事件类型

- **`INIT`**: 初始化，返回 `messageId`
- **`PROGRESS`**: 进度更新
- **`COMPLETED`**: 生成完成
- **`ERROR`**: 错误

---

## 7. 对话工作流

```
1. 创建会话
   POST /app-api/plot/chat/session/create
   → 返回 sessionId

2. 发送消息
   POST /app-api/plot/chat/message (multipart/form-data)
   → 返回 SSE 流，包含 messageId

3. 等待生成 (可选)
   轮询 GET /app-api/plot/chat/message/status?messageId=xxx
   或
   监听 SSE 流直到收到 COMPLETED 事件

4. 继续对话
   复用 sessionId，发送新消息
```

---

## 8. 实现建议

### 8.1 扩展对话类型

基于当前实现 (`src/chat/client.py`)，可以扩展以下功能:

```python
# 1. 指定模型
def send_message_with_model(
    self, 
    session_id: str, 
    message: str, 
    model_id: int = 12,
    ratio: str = "16:9"
):
    files = {
        'actionType': (None, 'NORMAL_CHAT'),
        'sessionId': (None, session_id),
        'scene': (None, 'normal_chat'),
        'text': (None, message),
        'modelId': (None, str(model_id)),
        'ratio': (None, ratio),
    }
    # ...

# 2. 监听思考状态
def get_thinking_status(self, message_id: str):
    url = f"{self.BASE_URL}/app-api/plot/chat/message/thinking/status"
    params = {"messageId": message_id}
    response = self.session.get(url, params=params)
    return response.json()

# 3. 获取会话历史
def get_session_history(self, page: int = 1, size: int = 20):
    url = f"{self.BASE_URL}/app-api/plot/chat/session/history"
    payload = {"page": page, "size": size}
    response = self.session.post(url, json=payload)
    return response.json()
```

### 8.2 新增 chat 子模块

建议按功能创建子模块:

```
src/chat/
├── __init__.py
├── __main__.py
├── client.py           # 主客户端
├── session.py          # 会话管理
├── message.py          # 消息发送/查询
├── model.py            # 模型列表/选择
└── stream.py           # SSE 流处理
```

---

## 9. 未覆盖的功能

由于 HAR 文件有限，以下功能尚未分析:

- 文件上传 (图片/PDF 输入)
- 消息编辑/重新生成
- 会话分享
- 导出功能
- 高级搜索
- 项目管理

建议通过 Web 界面抓包或查阅官方文档进一步分析。

---

## 10. 测试覆盖

当前已实现的测试:

- ✅ `test/chat/test_quick_chat.py` - 消息发送验证
- ✅ `test/chat/test_full_chat.py` - 完整对话流程

可新增的测试:

- ⏳ 多轮对话测试
- ⏳ 模型切换测试
- ⏳ 思考状态监听测试
- ⏳ 历史会话查询测试

---

**生成时间**: 2026-06-15  
**数据来源**: HAR 抓包文件分析  
**测试账户**: User ID `2066456792086212609`
