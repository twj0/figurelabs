# FigureLabs.ai 注册流程完整分析

## 数据来源
HAR 文件：`api.figurelabs.ai_2026_06_15_17_13_12.har`

---

## 注册流程（邮箱验证码方式）

### 步骤 1: 发送验证码
**端点**: `POST https://api.figurelabs.ai/app-api/plot/member/mail`

**请求**:
```http
POST /app-api/plot/member/mail HTTP/1.1
Host: api.figurelabs.ai
Content-Type: application/x-www-form-urlencoded

email=fDX4sMefvp%40duckmail.sbs
```

**请求参数**:
```
email: fDX4sMefvp@duckmail.sbs
```

**响应**:
```json
{
  "code": 0,
  "data": "2066448639105761281",
  "msg": ""
}
```

**说明**:
- 返回的 `data` 是 `codeId`（验证码ID）
- 服务端发送验证码到邮箱
- `codeId` 用于后续登录验证

---

### 步骤 2: 登录/注册
**端点**: `POST https://api.figurelabs.ai/app-api/plot/member/login`

**预检请求** (OPTIONS):
```http
OPTIONS /app-api/plot/member/login HTTP/1.1
Host: api.figurelabs.ai
```
CORS 预检，浏览器自动发起。

**实际请求**:
```http
POST /app-api/plot/member/login HTTP/1.1
Host: api.figurelabs.ai
Content-Type: application/json

{
  "email": "fDX4sMefvp@duckmail.sbs",
  "password": "525267",
  "codeId": "2066448639105761281",
  "deviceId": "5d62cb73-745e-4aba-92de-04e0895f3bf6",
  "deviceType": "desktop",
  "os": "Windows",
  "browser": "Firefox",
  "referringDomain": "$direct"
}
```

**请求参数详解**:
```typescript
interface LoginRequest {
  email: string;              // 用户邮箱
  password: string;           // 验证码（6位数字）
  codeId: string;             // 步骤1返回的验证码ID
  deviceId: string;           // 设备唯一标识（UUID）
  deviceType: string;         // 设备类型：desktop/mobile/tablet
  os: string;                 // 操作系统：Windows/macOS/Linux/iOS/Android
  browser: string;            // 浏览器：Firefox/Chrome/Safari/Edge
  referringDomain: string;    // 来源域名，$direct 表示直接访问
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "accessToken": "9a654ad89fa347f88de6c92aef05f3f3",
    "refreshToken": "a9422556799b48acbf75cf6886062425",
    "userId": "2066448730118025217",
    "avatar": null,
    "surname": null,
    "name": null,
    "email": null,
    "userType": 3,
    "expiresTime": 1781773945024,
    "isNewUser": true,
    "isInTeam": false,
    "teamId": null,
    "teamName": null,
    "isTeamAdmin": null
  },
  "msg": ""
}
```

**响应参数详解**:
```typescript
interface LoginResponse {
  accessToken: string;        // 访问令牌（用于后续 API 调用）
  refreshToken: string;       // 刷新令牌（用于延长会话）
  userId: string;             // 用户ID（雪花ID）
  avatar: string | null;      // 头像URL
  surname: string | null;     // 姓氏
  name: string | null;        // 名字
  email: string | null;       // 邮箱（未返回，隐私保护）
  userType: number;           // 用户类型：3=普通用户
  expiresTime: number;        // Token过期时间（Unix时间戳毫秒）
  isNewUser: boolean;         // 是否新用户（true=注册，false=登录）
  isInTeam: boolean;          // 是否在团队中
  teamId: string | null;      // 团队ID
  teamName: string | null;    // 团队名称
  isTeamAdmin: boolean | null;// 是否团队管理员
}
```

---

## 关键发现

### 1. 无密码注册设计
- **无需传统密码**：用户只需邮箱即可注册
- **验证码即密码**：6位数字验证码（`525267`）作为一次性密码
- **流程简化**：发送验证码 → 输入验证码 → 完成注册/登录

### 2. 注册与登录合并
- **同一端点**：`/member/login` 同时处理注册和登录
- **自动区分**：后端根据邮箱是否存在自动判断
- **响应标识**：`isNewUser: true` 表示新注册，`false` 表示已存在用户登录

### 3. Token 认证机制
- **双Token设计**：
  - `accessToken`: 短期访问令牌（API调用）
  - `refreshToken`: 长期刷新令牌（续期）
- **过期时间**：`expiresTime: 1781773945024` (约2026-06-15 17:19:05)
- **使用方式**：在 HTTP Header 中携带 `Authorization: Bearer <accessToken>`

### 4. 设备指纹追踪
收集设备信息用于：
- 安全审计（异常登录检测）
- 用户行为分析
- 多设备管理

**设备信息字段**：
```json
{
  "deviceId": "5d62cb73-745e-4aba-92de-04e0895f3bf6",  // 浏览器生成的UUID
  "deviceType": "desktop",
  "os": "Windows",
  "browser": "Firefox",
  "referringDomain": "$direct"  // 来源追踪（营销分析）
}
```

### 5. 用户类型系统
```
userType: 3  // 普通用户
```
推测可能的类型：
- `1`: 管理员
- `2`: 付费用户/Pro
- `3`: 免费用户
- `4`: 团队成员

---

## 完整注册流程图

```
用户输入邮箱
    ↓
[POST] /member/mail
    ↓
服务端发送验证码到邮箱
    ↓
用户打开邮箱，获取验证码
    ↓
用户输入验证码
    ↓
[POST] /member/login
    ↓
后端验证 codeId + password
    ↓
    ├─ 邮箱不存在 → 创建新用户 (isNewUser: true)
    └─ 邮箱已存在 → 直接登录 (isNewUser: false)
    ↓
返回 accessToken + refreshToken
    ↓
前端存储 Token（localStorage/Cookie）
    ↓
跳转到工作区 (chat.figurelabs.ai)
```

---

## API 端点总结

| 端点 | 方法 | 用途 | 请求类型 |
|------|------|------|----------|
| `/app-api/plot/member/mail` | POST | 发送邮箱验证码 | `application/x-www-form-urlencoded` |
| `/app-api/plot/member/login` | POST | 注册/登录 | `application/json` |
| `/app-api/plot/member/checkLogin` | GET | 检查登录状态 | - |
| `/app-api/plot/member/info` | GET | 获取用户信息 | - |

---

## 安全分析

### ✅ 优点
1. **无密码设计**：降低用户记忆负担，提高转化率
2. **双Token机制**：accessToken 短期 + refreshToken 长期，平衡安全与体验
3. **邮箱验证**：确保邮箱真实性
4. **设备追踪**：支持异常登录检测

### ⚠️ 潜在风险
1. **验证码安全**：
   - 6位纯数字，理论上可暴力破解（1,000,000 种可能）
   - 需要速率限制防止暴力攻击
   
2. **邮箱劫持**：
   - 使用临时邮箱（duckmail.sbs）可能导致账户被他人接管
   - 临时邮箱服务通常公开可访问
   
3. **Token泄露**：
   - accessToken 如果存储在 localStorage，易受XSS攻击
   - 建议使用 HttpOnly Cookie

4. **CORS安全**：
   - OPTIONS 预检请求需要正确配置 CORS 头
   
5. **中间人攻击**：
   - 虽然使用 HTTPS，但需确保证书有效性

### 🔒 建议的改进
1. 验证码增加字母（如 6位字母数字混合）
2. 实施严格的速率限制（如每邮箱每小时最多3次）
3. Token 存储使用 HttpOnly + Secure Cookie
4. 添加设备信任机制（常用设备无需重复验证）
5. 支持 2FA（二次认证）

---

## 前端实现参考

### JavaScript 注册示例
```javascript
// 步骤1: 发送验证码
async function sendVerificationCode(email) {
  const response = await fetch('https://api.figurelabs.ai/app-api/plot/member/mail', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({ email })
  });
  
  const result = await response.json();
  return result.data; // codeId
}

// 步骤2: 登录/注册
async function loginWithCode(email, code, codeId) {
  const deviceId = getOrCreateDeviceId(); // 从 localStorage 获取或生成
  
  const response = await fetch('https://api.figurelabs.ai/app-api/plot/member/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password: code,
      codeId,
      deviceId,
      deviceType: getDeviceType(),
      os: getOS(),
      browser: getBrowser(),
      referringDomain: document.referrer || '$direct'
    })
  });
  
  const result = await response.json();
  
  if (result.code === 0) {
    // 存储 Token
    localStorage.setItem('accessToken', result.data.accessToken);
    localStorage.setItem('refreshToken', result.data.refreshToken);
    
    // 跳转
    window.location.href = 'https://chat.figurelabs.ai';
  }
  
  return result;
}

// 辅助函数
function getOrCreateDeviceId() {
  let deviceId = localStorage.getItem('deviceId');
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem('deviceId', deviceId);
  }
  return deviceId;
}

function getDeviceType() {
  const ua = navigator.userAgent;
  if (/mobile|android|iphone|ipad|phone/i.test(ua)) {
    return 'mobile';
  } else if (/tablet|ipad/i.test(ua)) {
    return 'tablet';
  }
  return 'desktop';
}

function getOS() {
  const ua = navigator.userAgent;
  if (ua.includes('Win')) return 'Windows';
  if (ua.includes('Mac')) return 'macOS';
  if (ua.includes('Linux')) return 'Linux';
  if (ua.includes('iPhone') || ua.includes('iPad')) return 'iOS';
  if (ua.includes('Android')) return 'Android';
  return 'Unknown';
}

function getBrowser() {
  const ua = navigator.userAgent;
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Chrome') && !ua.includes('Edge')) return 'Chrome';
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari';
  if (ua.includes('Edge')) return 'Edge';
  return 'Unknown';
}
```

### Python 自动化示例
```python
import requests
import uuid

class FigureLabsAuth:
    BASE_URL = "https://api.figurelabs.ai"
    
    def __init__(self):
        self.session = requests.Session()
        self.device_id = str(uuid.uuid4())
    
    def send_verification_code(self, email):
        """发送验证码"""
        url = f"{self.BASE_URL}/app-api/plot/member/mail"
        data = {"email": email}
        
        response = self.session.post(url, data=data)
        result = response.json()
        
        if result["code"] == 0:
            return result["data"]  # codeId
        else:
            raise Exception(f"发送验证码失败: {result['msg']}")
    
    def login(self, email, code, code_id):
        """登录/注册"""
        url = f"{self.BASE_URL}/app-api/plot/member/login"
        
        payload = {
            "email": email,
            "password": code,
            "codeId": code_id,
            "deviceId": self.device_id,
            "deviceType": "desktop",
            "os": "Windows",
            "browser": "Python",
            "referringDomain": "$direct"
        }
        
        response = self.session.post(url, json=payload)
        result = response.json()
        
        if result["code"] == 0:
            data = result["data"]
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            self.user_id = data["userId"]
            return data
        else:
            raise Exception(f"登录失败: {result['msg']}")
    
    def register_and_login(self, email):
        """完整流程：发送验证码 → 等待用户输入 → 登录"""
        # 步骤1: 发送验证码
        code_id = self.send_verification_code(email)
        print(f"验证码已发送到 {email}")
        print(f"Code ID: {code_id}")
        
        # 步骤2: 等待用户输入验证码
        code = input("请输入验证码: ").strip()
        
        # 步骤3: 登录
        result = self.login(email, code, code_id)
        
        if result["isNewUser"]:
            print("✓ 注册成功！")
        else:
            print("✓ 登录成功！")
        
        print(f"User ID: {result['userId']}")
        print(f"Access Token: {result['accessToken']}")
        
        return result

# 使用示例
if __name__ == "__main__":
    auth = FigureLabsAuth()
    
    email = "test@example.com"
    result = auth.register_and_login(email)
```

---

## 测试用例

### 正常流程
1. ✅ 新邮箱注册成功
2. ✅ 已有邮箱登录成功
3. ✅ Token 有效期内可正常访问

### 异常情况
1. ⚠️ 无效邮箱格式
2. ⚠️ 验证码错误
3. ⚠️ 验证码过期（通常5-10分钟）
4. ⚠️ codeId 不匹配
5. ⚠️ Token 过期（需刷新）

---

## 总结

FigureLabs.ai 采用了**现代化的无密码认证方案**：
- ✅ 用户体验极佳（无需设置密码）
- ✅ 注册转化率高
- ✅ 支持邮箱验证码一键登录
- ⚠️ 需注意临时邮箱的安全风险
- ⚠️ 验证码强度有待提高
