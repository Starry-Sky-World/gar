# ChatGPT 账号自动注册工具

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB.svg?logo=python&logoColor=white)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)


基于 Python + Selenium 的 ChatGPT 账号全流程自动化工具。实现了从**账号注册**、**自动绑卡开通 Plus** 到 **自动取消订阅** 的全链路自动化。

## 功能特性

### 1. 自动注册 (Automatic Registration)

- **全自动流程**：自动填写邮箱、密码，处理验证码，填写个人资料（生日等）。
- **验证码处理**：对接 Cloudflare 临时邮箱服务，自动获取并输入验证码。
- **反检测机制**：使用 `undetected-chromedriver` 模拟真实用户行为，绕过 Cloudflare 验证。
- **批量作业**：支持配置批量注册数量和间隔时间。

### 2. 自动绑卡 (Automatic Card Binding)

- **Plus 订阅**：注册完成后自动引导至 Plus 订阅页面。
- **支付填单**：自动填写信用卡信息（卡号、有效期、CVC）和账单地址。
- **状态确认**：智能检测订阅成功状态，确保权益开通。

### 3. 自动取消 (Automatic Cancellation)

- **即时止损**：订阅成功后立即执行取消操作，防止后续扣费。
- **流程闭环**：进入设置页面 -> 管理订阅 -> 取消方案 -> 确认终止。
- **权益保留**：取消后账号仍保留当前计费周期的 Plus 权益。

## 项目结构


```text
py/
├── main.py              # CLI 核心逻辑
├── server.py            # Web 服务端 (Flask)
├── browser.py           # 浏览器自动化模块 (Selenium + undetected-chromedriver)
├── email_service.py     # 临时邮箱服务接口
├── config.py            # 配置加载模块
├── utils.py             # 通用工具函数
├── static/              # 前端静态资源 (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── config.yaml          # [隐私] 你的实际配置文件 (已忽略)
├── config.example.yaml  # 配置文件模板 (提交到 Git)
├── pyproject.toml       # 项目依赖定义 (uv)
├── uv.lock              # 依赖锁定文件
└── README.md            # 说明文档
```

## 快速开始


### 1. 安装依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 进行现代化的包管理。

1. **安装 uv**（如果你还没安装）：
   ```bash
   pip install uv
   ```

2. **同步虚拟环境**：
   ```bash
   # 这会根据 pyproject.toml 自动创建虚拟环境并安装所有依赖
   uv sync
   ```

### 2. 配置

复制示例配置文件并修改：

```bash
cp config.example.yaml config.yaml
```

然后编辑 `config.yaml` 填入你的配置。

> 也可以通过环境变量覆盖配置，适用于容器/CI 环境。详见下方“环境变量配置”。

### 3. 运行

**方式一：Web 控制台（推荐）**

启动带有可视化界面的 Web 服务：

```bash
uv run server.py
```

然后在浏览器访问：[http://localhost:5000](http://localhost:5000)

**方式二：命令行模式**

仅运行后台脚本：

```bash
uv run main.py
```



## 配置说明


所有配置都在 `config.yaml` 文件中，使用 YAML 格式，结构清晰易读。

### 配置文件结构

```yaml
# 注册配置
registration:
  total_accounts: 1      # 要注册的账号数量
  min_age: 20           # 随机生日的最小年龄
  max_age: 40           # 随机生日的最大年龄

# 临时邮箱服务配置
email:
  worker_url: "https://your-worker.workers.dev"
  domain: "your-domain.com"
  prefix_length: 10
  wait_timeout: 120     # 等待验证邮件超时（秒）
  poll_interval: 3
  admin_password: "your-password"

# 浏览器配置
browser:
  max_wait_time: 600
  short_wait_time: 120
  user_agent: "..."

# 密码配置
password:
  length: 16
  charset: "abcdefghijklmnopqrstuvwxyz..."

# 重试配置
retry:
  http_max_retries: 5
  http_timeout: 30
  error_page_max_retries: 5
  button_click_max_retries: 3

# 批量注册配置
batch:
  interval_min: 5
  interval_max: 15

# 文件路径配置
files:
  accounts_file: "registered_accounts.txt"

# WebDAV 备份（可选）
webdav:
  enabled: false
  url: "https://dav.example.com/remote.php/dav/files/user"
  username: "your-user"
  password: "your-password"
  remote_dir: "oai_accounts"
  interval_minutes: 0

# 支付信息（用于 Plus 试用）
payment:
  credit_card:
    number: "your-card-number"
    expiry: "MMYY"
    expiry_month: "MM"
    expiry_year: "YYYY"
    cvc: "xxx"
```

### 必须配置

| 配置项 | 路径 | 说明 |
|--------|------|------|
| Worker 地址 | `email.worker_url` | 你部署的 cloudflare_temp_email Worker 地址 |
| 邮箱域名 | `email.domain` | 收信域名（Cloudflare Email Routing 配置的域名） |
| 管理员密码 | `email.admin_password` | cloudflare_temp_email 管理员密码 |

### 可选配置

| 配置项 | 路径 | 默认值 | 说明 |
|--------|------|--------|------|
| 注册数量 | `registration.total_accounts` | 1 | 要注册的账号数量 |
| 最小年龄 | `registration.min_age` | 20 | 随机生日的最小年龄 |
| 最大年龄 | `registration.max_age` | 40 | 随机生日的最大年龄 |
| 密码长度 | `password.length` | 16 | 密码长度 |
| 邮件超时 | `email.wait_timeout` | 120 | 等待验证邮件超时（秒） |

### 环境变量配置

除了 `config.yaml`，你也可以使用环境变量覆盖配置，方便在容器或 CI 环境中传递敏感信息。所有环境变量都需要以 `GAR_` 为前缀，例如：

```bash
export GAR_EMAIL_DOMAIN="your-domain.com"
export GAR_EMAIL_ADMIN_PASSWORD="your-admin-password"
```

常用环境变量对照表（✅ 必填）：

| 环境变量 | 必填 | 默认值 | 对应配置路径 | 变量作用 |
|----------|------|--------|--------------|----------|
| `GAR_EMAIL_WORKER_URL` | ✅ | 无 | `email.worker_url` | Cloudflare 临时邮箱 Worker 的完整访问地址 |
| `GAR_EMAIL_DOMAIN` | ✅ | 无 | `email.domain` | 临时邮箱接收域名（需要在 Cloudflare Email Routing 中配置） |
| `GAR_EMAIL_ADMIN_PASSWORD` | ✅ | 无 | `email.admin_password` | 临时邮箱 Worker 的管理员密码，用于轮询和读取邮件 |
| `GAR_WEBDAV_ENABLED` | ❌ | `false` | `webdav.enabled` | 是否启用 WebDAV 账号备份 |
| `GAR_WEBDAV_URL` | ❌ | 空 | `webdav.url` | WebDAV 服务器地址 |
| `GAR_WEBDAV_USERNAME` | ❌ | 空 | `webdav.username` | WebDAV 登录用户名 |
| `GAR_WEBDAV_PASSWORD` | ❌ | 空 | `webdav.password` | WebDAV 登录密码/应用密码 |
| `GAR_WEBDAV_REMOTE_DIR` | ❌ | `oai_accounts` | `webdav.remote_dir` | 备份文件存放的远端目录 |
| `GAR_WEBDAV_INTERVAL_MINUTES` | ❌ | `0` | `webdav.interval_minutes` | 定时备份间隔（分钟），0 表示关闭 |
| `GAR_PAYMENT_CREDIT_CARD_NUMBER` | ✅（绑卡） | 无 | `payment.credit_card.number` | 用于 Plus 订阅的信用卡卡号 |
| `GAR_PAYMENT_CREDIT_CARD_EXPIRY` | ✅（绑卡） | 无 | `payment.credit_card.expiry` | 信用卡有效期（MMYY），与 `expiry_month`/`expiry_year` 二选一 |
| `GAR_PAYMENT_CREDIT_CARD_EXPIRY_MONTH` | ✅（绑卡） | 无 | `payment.credit_card.expiry_month` | 信用卡有效期-月（MM），与 `expiry`/`expiry_year` 组合使用 |
| `GAR_PAYMENT_CREDIT_CARD_EXPIRY_YEAR` | ✅（绑卡） | 无 | `payment.credit_card.expiry_year` | 信用卡有效期-年（YYYY），与 `expiry_month` 组合使用 |
| `GAR_PAYMENT_CREDIT_CARD_CVC` | ✅（绑卡） | 无 | `payment.credit_card.cvc` | 信用卡 CVC/CVV 安全码 |
| `GAR_REGISTRATION_TOTAL_ACCOUNTS` | ❌ | `1` | `registration.total_accounts` | 需要注册的账号数量 |
| `GAR_REGISTRATION_MIN_AGE` | ❌ | `20` | `registration.min_age` | 随机生日的最小年龄（岁） |
| `GAR_REGISTRATION_MAX_AGE` | ❌ | `40` | `registration.max_age` | 随机生日的最大年龄（岁） |
| `GAR_EMAIL_PREFIX_LENGTH` | ❌ | `10` | `email.prefix_length` | 临时邮箱前缀长度 |
| `GAR_EMAIL_WAIT_TIMEOUT` | ❌ | `120` | `email.wait_timeout` | 轮询验证邮件的超时时间（秒） |
| `GAR_EMAIL_POLL_INTERVAL` | ❌ | `3` | `email.poll_interval` | 轮询验证邮件的时间间隔（秒） |
| `GAR_BROWSER_MAX_WAIT_TIME` | ❌ | `600` | `browser.max_wait_time` | 页面加载或元素等待的最长时间（秒） |
| `GAR_BROWSER_SHORT_WAIT_TIME` | ❌ | `120` | `browser.short_wait_time` | 常规短等待时间（秒） |
| `GAR_BROWSER_USER_AGENT` | ❌ | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` | `browser.user_agent` | 浏览器 User-Agent 字符串 |
| `GAR_PASSWORD_LENGTH` | ❌ | `16` | `password.length` | 自动生成密码的长度 |
| `GAR_PASSWORD_CHARSET` | ❌ | `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%` | `password.charset` | 自动生成密码的字符集 |
| `GAR_RETRY_HTTP_MAX_RETRIES` | ❌ | `5` | `retry.http_max_retries` | HTTP 请求的最大重试次数 |
| `GAR_RETRY_HTTP_TIMEOUT` | ❌ | `30` | `retry.http_timeout` | HTTP 请求超时时间（秒） |
| `GAR_RETRY_ERROR_PAGE_MAX_RETRIES` | ❌ | `5` | `retry.error_page_max_retries` | 遇到错误页时的重试次数 |
| `GAR_RETRY_BUTTON_CLICK_MAX_RETRIES` | ❌ | `3` | `retry.button_click_max_retries` | 按钮点击失败时的重试次数 |
| `GAR_BATCH_INTERVAL_MIN` | ❌ | `5` | `batch.interval_min` | 批量注册时的最短间隔（秒） |
| `GAR_BATCH_INTERVAL_MAX` | ❌ | `15` | `batch.interval_max` | 批量注册时的最长间隔（秒） |
| `GAR_FILES_ACCOUNTS_FILE` | ❌ | `registered_accounts.txt` | `files.accounts_file` | 已注册账号保存文件路径 |

### WebDAV 备份说明

- 可通过配置文件或环境变量开启 `webdav.enabled`。
- 每次任务结束会将账号文件上传到 WebDAV 的 `oai_accounts/<timestamp>_accounts.txt` 下，便于历史追溯。
- 设置 `webdav.interval_minutes` 后会按间隔自动备份，手动模式可在 Web 界面点击「立即备份」。

> 提示：表格中的默认值即 `config.py` 中的内置默认值；标记为 ✅ 的环境变量在对应功能（邮箱服务或绑卡）中必须提供，否则运行会失败。

> 其他字段也支持环境变量覆盖，命名规则请参考上述表格中的前缀和路径格式。

## 模块说明


### config.py - 配置加载模块

从 `config.yaml` 加载配置，支持：
- 自动查找配置文件（支持 `.yaml`、`.yml`、`.local.yaml` 等）
- 类型安全的配置访问（使用 dataclass）
- 向后兼容（仍可使用 `from config import TOTAL_ACCOUNTS` 方式）
- 运行时重新加载配置

**推荐用法：**
```python
from config import cfg

# 访问配置
total = cfg.registration.total_accounts
email_domain = cfg.email.domain
```

**兼容旧代码：**
```python
from config import TOTAL_ACCOUNTS, EMAIL_DOMAIN
```

### email_service.py - 邮箱服务模块
基于 [cloudflare_temp_email](https://github.com/dreamhunter2333/cloudflare_temp_email) 项目实现：
- `create_temp_email()` - 创建临时邮箱
- `fetch_emails()` - 获取邮件列表
- `get_email_detail()` - 获取邮件详情
- `wait_for_verification_email()` - 等待并提取验证码

### browser.py - 浏览器自动化模块
使用 undetected-chromedriver 绕过反爬检测：
- `create_driver()` - 创建浏览器实例
- `fill_signup_form()` - 填写注册表单
- `enter_verification_code()` - 输入验证码
- `fill_profile_info()` - 填写个人资料
- `subscribe_plus_trial()` - 开通 Plus 试用
- `cancel_subscription()` - 取消订阅

### utils.py - 工具函数模块
通用辅助函数：
- `create_http_session()` - 创建带重试的 HTTP Session
- `generate_random_password()` - 生成随机密码
- `save_to_txt()` - 保存账号到 TXT
- `update_account_status()` - 更新账号状态
- `extract_verification_code()` - 提取验证码

### main.py - 主程序
程序入口，整合所有模块：
- `register_one_account()` - 注册单个账号
- `run_batch()` - 批量注册

## 重要安全提示


1. **不要提交 `config.yaml`**：包含敏感信息（API 密钥、信用卡信息等）
2. 项目已配置 `.gitignore` 忽略 `config.yaml`
3. 请使用 `config.example.yaml` 作为模板
4. 定期检查并删除已保存的账号记录

## 注意事项


1. 需要正确配置 cloudflare_temp_email 服务
2. 确保邮箱域名的 MX 记录已正确设置
3. 注册过程中请勿操作浏览器窗口
4. 建议每次注册间隔一定时间，避免触发风控

## 输出文件


注册成功的账号会保存到 `registered_accounts.txt`，格式：

```
邮箱 | 密码 | 状态 | 注册时间
xxx@domain.com | password123 | 已取消订阅 | 2026-01-06 09:45:00
```

项目依赖现已通过 `pyproject.toml` 管理。

## 免责声明 (Disclaimer)


1. **技术研究用途**：本项目仅供 Python 自动化技术学习和研究使用，旨在验证 Selenium 和 undetected-chromedriver 的技术可行性。
2. **合规使用**：请严格遵守 OpenAI 的[使用条款](https://openai.com/policies/terms-of-use)。请勿将本工具用于任何商业用途、大规模批量注册或其他违反服务条款的行为。
3. **风险自负**：使用者需自行承担使用本工具产生的任何后果（包括但不限于账号被封禁、IP 被拉黑等）。作者不对任何因使用本工具而导致的损失负责。
4. **无担保**：本项目基于开源精神分享，不提供任何形式的保证或维护承诺。代码可能会因目标网站更新而失效。


