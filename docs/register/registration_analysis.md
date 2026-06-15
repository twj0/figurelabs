# FigureLabs.ai 注册逻辑分析

## 数据来源
- HAR 抓包文件（3个）
- Web 搜索结果
- API 响应数据

## 当前注册方式

### 1. Google OAuth 登录（主要方式）
根据搜索结果和业界标准，网站支持 **Google Sign-in**：
- 用户点击"Sign in with Google"
- 重定向到 Google OAuth 授权页面
- 授权后回调到 figurelabs.ai
- 后端创建账户或匹配现有账户

### 2. 邮箱注册（推测）
虽然 HAR 文件未捕获注册流程，但根据用户信息结构推测存在邮箱注册：

**用户信息结构**（来自 `/app-api/plot/member/info`）：
```json
{
  "id": "2066016948436463618",
  "name": "KH4ZPXPvLa",
  "email": "KH4ZPXPvLa@duckmail.sbs",  // 临时邮箱
  "avatar": "",
  "isSubscribed": true,
  "subscriptionType": "free",
  "loginDate": 1781411800000,
  "createTime": 1781411800000,
  "isInTeam": false,
  "teamId": null,
  "hasTeam": false
}
```

**推测的注册流程**：
1. 用户访问注册页面
2. 输入邮箱 + 密码（或仅邮箱）
3. POST 请求到 `/app-api/plot/member/register` 或类似端点
4. 后端创建账户，返回 token 或设置 Cookie
5. 前端重定向到工作区

## 认证机制

### Cookie-based 认证
- HAR 文件显示所有请求都携带 Cookie
- 服务端通过 Cookie 验证会话状态
- 主要 API：
  - `GET /app-api/plot/member/checkLogin` - 检查登录状态
  - `GET /app-api/plot/member/info` - 获取用户信息

### 会话管理
- 登录后持久化会话（Cookie）
- 前端定期调用 `checkLogin` 验证状态
- 未登录时重定向到登录页

## 账户类型

### 免费账户（Free）
```json
{
  "isSubscribed": true,
  "subscriptionType": "free"
}
```
- 有限制的使用额度
- 通过 `package/points/remaining` 查询剩余点数

### 订阅账户（推测存在 Pro/Team）
- `isInTeam` / `hasTeam` 字段表明支持团队功能
- 需付费订阅（通过 `notify/checkPaid` 检查支付状态）

## 已知的认证端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/app-api/plot/member/checkLogin` | GET | 检查登录状态 |
| `/app-api/plot/member/info` | GET | 获取用户信息 |
| `/app-api/plot/notify/checkPaid` | POST | 检查付费状态 |
| `/app-api/plot/notify/checkSubscription` | POST | 检查订阅状态 |

## 未捕获的端点（推测）

基于常见模式，可能存在但未在 HAR 中出现的端点：
- `/app-api/plot/member/register` - 注册
- `/app-api/plot/member/login` - 邮箱登录
- `/app-api/plot/member/logout` - 登出
- `/app-api/plot/member/verify` - 邮箱验证
- `/app-api/plot/oauth/google/callback` - Google OAuth 回调

## 第三方集成

### 分析工具
- **Amplitude**: 用户行为分析
- **Mixpanel**: 事件追踪

这些工具在注册流程中可能收集：
- 注册来源
- 注册转化漏斗
- 用户激活事件

## 建议的下一步

### 1. 捕获完整注册流程
**操作步骤**：
1. 清除浏览器 Cookie
2. 开启开发者工具 Network 面板
3. 访问 https://chat.figurelabs.ai
4. 完成注册流程
5. 导出新的 HAR 文件

### 2. 逆向分析前端代码
查找注册相关的 JavaScript 代码：
- 搜索 `register`, `signup` 关键字
- 查找表单提交逻辑
- 分析 API 调用点

### 3. 尝试 API 端点
使用 Postman/curl 测试推测的端点：
```bash
# 检查注册端点是否存在
curl -X POST https://chat.figurelabs.ai/app-api/plot/member/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 安全观察

✅ **良好实践**：
- 全站 HTTPS
- 使用临时邮箱服务（duckmail.sbs）表明支持任意邮箱

⚠️ **需关注**：
- Cookie 认证细节不明（HttpOnly? Secure? SameSite?）
- 密码策略未知
- 速率限制未知
- CSRF 保护未知
