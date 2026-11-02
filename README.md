# my_skills

Codex 技能仓库（Skills Repo，多技能 Monorepo）。

本仓库用于存放可复用、可共享的 [Codex skills](https://github.com/openai/skills)。所有技能位于 `skills/` 目录下，每个技能是一个独立文件夹，包含必需的 `SKILL.md`（YAML frontmatter 声明 `name` 和 `description`）以及可选资源。结构与官方 [openai/skills](https://github.com/openai/skills) 组织方式一致。

## 目录结构

```
my_skills/
├── skills/
│   ├── email-receive/   # IMAP 收信技能
│   └── email-send/      # SMTP 发信技能
├── README.md
└── .gitignore
```

## 技能列表

| 技能 | 说明 |
| ---- | ---- |
| `skills/email-receive` | 通过 IMAP 收取邮件，配置从 `.env` 读取；支持正文与附件下载（模板见 `skills/email-receive/.env.example`） |
| `skills/email-send` | 通过 SMTP 发送邮件，配置从 `.env` 读取；支持 HTML 正文与附件（模板见 `skills/email-send/.env.example`） |

## 安装技能到本机

使用 Codex 内置的 skill-installer 从本仓库安装：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path skills/email-receive
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path skills/email-send
```

或直接使用 URL 形式：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/jengy/my_skills/tree/main/skills/email-receive
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/jengy/my_skills/tree/main/skills/email-send
```

安装后会写入 `$CODEX_HOME/skills/<skill-name>`，下一个会话即可使用。仓库为私有时，需先配置 git 凭据或设置 `GITHUB_TOKEN` / `GH_TOKEN`。

## 新增技能

1. 在 `skills/` 下创建 `<skill-name>/` 文件夹。
2. 在文件夹内创建 `SKILL.md`，frontmatter 必须包含 `name`（小写连字符）和 `description`。
3. 如需要，添加 `agents/openai.yaml`（UI 元数据）、`scripts/`、`references/`、`assets/`。
4. 用 skill-creator 的校验脚本检查结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

命名规范：小写字母、数字、连字符；名称用功能名（如 `email-receive`），以便技能自动发现更准确。

## 参考

- [openai/skills](https://github.com/openai/skills) — 官方技能库与规范
