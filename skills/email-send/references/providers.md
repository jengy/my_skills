# SMTP 发信配置参考

发信一律使用**授权码 / 应用专用密码**，与收信（email-receive）共用 `EMAIL_USER` / `EMAIL_PASSWORD`，可放在同一个 `.env`。

| 服务商 | SMTP_HOST | 端口 / 模式 | 授权方式 |
| ------ | --------- | ----------- | -------- |
| QQ 邮箱 | `smtp.qq.com` | `465` SSL 或 `587` STARTTLS | 设置 → 账号 → 开启 SMTP → 生成**授权码** |
| 网易 163 | `smtp.163.com` | `465` / `994` SSL | 设置 → 开启 SMTP → **客户端授权密码** |
| 网易企业邮箱 | 开通邮件中给出（如 `smtphz.qiye.163.com`） | `465` SSL 等 | 企业邮箱 IT 分配的专用密码 |
| Gmail | `smtp.gmail.com` | `465` SSL 或 `587` STARTTLS | 需开两步验证 → **应用专用密码** |
| Outlook.com / Hotmail / MSN | `smtp-mail.outlook.com` | `587` STARTTLS | **基础认证已禁用**，需两步验证 + **应用专用密码** |
| Office 365（企业） | `smtp.office365.com` | `587` STARTTLS | 登录密码或应用密码 |

## 模式选择
- `SMTP_SSL=true`（默认）→ 直连 SSL，端口通常 `465`。
- `SMTP_SSL=false` + `SMTP_STARTTLS=true` → 明连后用 STARTTLS 升级，端口通常 `587`。
- Gmail / Outlook 个人邮箱推荐用 `587` + STARTTLS。

## 常见问题
- `Basic authentication is disabled`：微软个人邮箱基础认证被禁用，改用**应用专用密码**。
- `Authentication failed` / `username and password not accepted`：授权码或密码错误；QQ/163 用授权码，Gmail/微软用应用密码。
- `5.7.1 ... blocked / rejected`：发信被服务商拦截，多为频率限制、内容被判垃圾、或收件人无效；放慢频率重试。
- 发信频率过高：QQ/163 等对每日发信量、单封收件人数有上限，超限会临时拒绝。
- 连接超时：确认 `SMTP_HOST` / `SMTP_PORT` / `SMTP_SSL` / `SMTP_STARTTLS` 是否匹配该服务商要求。

## 建议先用 --check-auth
```bash
python scripts/send_email.py --check-auth
```
若输出 `SMTP authentication verified`，说明账号与服务器配置正确，可放心发信。
