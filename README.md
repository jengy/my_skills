# my_skills

Codex & Claude Code 技能仓库（多技能 Monorepo）。

本仓库用于存放可复用、可共享的 [Codex skills](https://github.com/openai/skills) 与 [Claude Code 插件](https://docs.claude.com/en/docs/claude-code/plugins)。所有技能位于 `skills/` 目录下，每个技能是一个独立文件夹，包含必需的 `SKILL.md`（YAML frontmatter 声明 `name` 和 `description`）以及可选资源。

## 目录结构

```
my_skills/
├── .claude-plugin/
│   ├── marketplace.json   # Claude Code 插件 marketplace 描述
│   └── plugin.json        # email-tools 插件元数据
├── skills/
│   ├── email-receive/     # IMAP 收信技能
│   └── email-send/        # SMTP 发信技能
├── README.md
└── .gitignore
```

## 技能列表

| 技能 | 说明 |
| ---- | ---- |
| `skills/email-receive` | 通过 IMAP 收取邮件，配置从 `.env` 读取；支持正文与附件下载（模板见 `skills/email-receive/.env.example`） |
| `skills/email-send` | 通过 SMTP 发送邮件，配置从 `.env` 读取；支持 HTML 正文与附件（模板见 `skills/email-send/.env.example`） |

## 安装技能到本机（Codex）

使用 Codex 内置的 skill-installer 从本仓库安装：

```bash
# 一次安装全部技能（--path 后跟空格分隔的多个路径）
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path skills/email-receive skills/email-send

# 或只装一个
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jengy/my_skills \
  --path skills/email-receive
```

安装后会写入 `$CODEX_HOME/skills/<skill-name>`，下一个会话即可使用。仓库为私有时，需先配置 git 凭据或设置 `GITHUB_TOKEN` / `GH_TOKEN`。

## 通过 Claude Code 插件安装

本仓库同时是一个 Claude Code 插件 marketplace（`.claude-plugin/marketplace.json`），提供一个 `email-tools` 插件，内含 `email-receive` 与 `email-send` 两个 Agent Skills。

1) 添加 marketplace：

```bash
claude plugin marketplace add jengy/my_skills
```

或在交互式会话中执行 `/plugin marketplace add jengy/my_skills`。

2) 安装插件：

```bash
claude plugin install email-tools@my-skills
```

或在交互式会话中执行 `/plugin install email-tools`。

3) 也可以在项目的 `.claude/settings.json` 中配置：

```json
{
  "plugins": {
    "marketplaces": {
      "my-skills": "github:jengy/my_skills"
    },
    "enabled": {
      "email-tools": true
    }
  }
}
```

安装后 `email-receive` / `email-send` 即成为 Claude Code 的 Agent Skills，配置仍使用各技能自己的 `.env`。

## 新增技能

1. 在 `skills/` 下创建 `<skill-name>/` 文件夹。
2. 在文件夹内创建 `SKILL.md`，frontmatter 必须包含 `name`（小写连字符）和 `description`。
3. 如需要，添加 `agents/openai.yaml`（Codex UI 元数据）、`scripts/`、`references/`、`assets/`。
4. 用 skill-creator 的校验脚本检查结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

命名规范：小写字母、数字、连字符；名称用功能名（如 `email-receive`），以便技能自动发现更准确。

## 参考

- [openai/skills](https://github.com/openai/skills) — Codex 官方技能库与规范
- [Claude Code Plugins](https://docs.claude.com/en/docs/claude-code/plugins) — Claude Code 插件与 marketplace 规范
