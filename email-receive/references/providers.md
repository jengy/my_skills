# 邮箱服务商配置参考

以下为常用邮箱的 IMAP 参数与授权方式。密码字段一律使用**授权码 / 应用专用密码**而不使用登录密码。

| 服务商 | IMAP_HOST | 端口 / SSL | 授权方式 |
| ------ | --------- | ---------- | -------- |
| QQ 邮箱 | `imap.qq.com` | `993` + `IMAP_SSL=true` | 设置 → 账号 → 开启 IMAP/SMTP 服务 → 生成**授权码** |
| 网易 163 | `imap.163.com` | `993` + SSL | 设置 → POP3/SMTP/IMAP → 开启 IMAP → 设置**客户端授权密码** |
| 网易企业邮箱 | 开通邮件中给出（如 `smtphz.qiye.163.com`） | `993` + SSL | 企业邮箱管理后台分配的专用密码 / 授权码 |
| Gmail | `imap.gmail.com` | `993` + SSL | 需开启「两步验证」，然后 Google 账户 → 安全 → **应用专用密码** |
| Outlook / Office 365（企业版） | `outlook.office365.com` | `993` + SSL | 可使用登录密码；开启 MFA 后需使用应用密码 |
| Outlook.com / Hotmail / MSN（个人） | `imap-mail.outlook.com` | `993` + SSL | **基础认证已禁用**：登录密码一律不可用，必须开启两步验证后使用**应用专用密码** |
| 企业邮箱 / 自建 | 由 IT 提供 | 视服务器而定（常见 `143` + `IMAP_SSL=false` 走 STARTTLS） | 按企业规定 |

## QQ 邮箱授权码
1. 登录 QQ 邮箱 → 设置 → 账号。
2. 找到「IMAP/SMTP 服务」→ 开启（需短信验证）。
3. 生成一段 16 位**授权码**，填入 `EMAIL_PASSWORD`。

## Gmail 应用专用密码
1. 确认已开启「两步验证」。
2. Google 账户 → 安全 → 搜索「应用专用密码」→ 新建。
3. 生成 16 位密码，填入 `EMAIL_PASSWORD`。

## 微软个人邮箱（Outlook.com / Hotmail / MSN）注意
微软已对个人邮箱**禁用 IMAP 基础认证**，使用普通登录密码连接会返回
`Basic authentication is disabled`。处理方法：
1. 在 account.microsoft.com 开启「两步验证」。
2. 在「安全」页生成一个**应用专用密码**（App Password），共 16 位、不含空格。
3. 将应用密码填入 `EMAIL_PASSWORD`。主机用 `imap-mail.outlook.com`。

## 常见问题
- `Basic authentication is disabled`：微软个人邮箱基础认证被禁用，请改用**应用专用密码**（见上）。
- `LOGIN failed` / `Authentication failed`：授权码或密码错误，或该账户未开启 IMAP / 未开启两步验证。
- `Cannot select folder`：`IMAP_MAILBOX` 写错了，可先运行 `python scripts/fetch_emails.py --list-folders` 查看可用文件夹。
- 连接超时：确认 `IMAP_HOST`、`IMAP_PORT`（993 SSL / 143 非 SSL）和 `IMAP_SSL` 是否匹配该服务商要求。
- 明文传输风险：非 SSL（`IMAP_SSL=false`）会明文传输凭据，仅在可信内网使用。
