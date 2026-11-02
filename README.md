# my_skills

Codex 技能仓库（Skills Repo）。

本仓库用于存放可复用、可共享的 [Codex skills](https://github.com/openai/skills)。每个技能是一个独立的文件夹，包含必需的 `SKILL.md`（YAML frontmatter 声明 `name` 和 `description`）以及可选资源。

## 技能列表

| 技能 | 说明 |
| ---- | ---- |
| `email-receive` | 通过 IMAP 收取邮件，配置从 `.env` 读取；支持正文与附件下载（模板见 `email-receive/.env.example`） |
| `email-send` | 通过 SMTP 发送邮件，配置从 `.env` 读取；支持 HTML 正文与附件（模板见 `email-send/.env.example`） |

## 安装技能到本机

使用 Codex 内置的 skill-installer 从本仓库安装：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path email-receive
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path email-send
```

或直接使用 URL 形式：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/jengy/my_skills/tree/main/email-receive
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/jengy/my_skills/tree/main/email-send
```

安装后会写入 `$CODEX_HOME/skills/<skill-name>`，下一个会话即可使用。仓库为私有时，需先配置 git 凭据或设置 `GITHUB_TOKEN` / `GH_TOKEN`。

## 新增技能

1. 在仓库根目录创建 `<skill-name>/` 文件夹。
2. 在文件夹内创建 `SKILL.md`，frontmatter 必须包含 `name`（小写连字符）和 `description`。
3. 如需要，添加 `agents/openai.yaml`（UI 元数据）、`scripts/`、`references/`、`assets/`。
4. 用 skill-creator 的校验脚本检查结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

命名规范：小写字母、数字、连字符；名称用功能名（如 `email-receive`），以便技能自动发现更准确。

## 参考

- [openai/skills](https://github.com/openai/skills) — 官方技能库与规范
