# Policy Agent Workspace

面向 CTF/自动化任务的 **Policy-Constrained LLM Agent**。核心链路：

`User Request -> LLM Plan -> Policy Check -> Tool Execution -> Audit Log`

## 1) 项目概览

- 前端：Next.js 14 + React + TypeScript + TailwindCSS
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 执行：Docker 隔离容器 + Workspace 文件隔离
- 模型：OpenAI（可通过环境变量切换模型名）

## 2) 快速启动

### 前置要求

- Docker / Docker Compose
- OpenAI API Key（可选，不填则后端仍可启动，但计划生成为空步骤）

### 启动

```bash
docker compose up -d --build
```

### 访问

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 常用排查

```bash
docker compose ps
docker compose logs backend --tail=200
docker compose logs frontend --tail=200
```

---

## 3) 目录结构

```text
backend/
  agent/        # LLM client + orchestrator
  api/          # REST API
  database/     # models + db connection
  policy/       # policy rules + policy engine
  tools/        # ToolGateway（工具执行入口）
  workspace/    # session 工作目录管理

frontend/
  src/app/      # Next.js App Router 页面
  src/components/
  src/hooks/
  src/lib/
```

---

## 4) 如何添加 Tools（系统内工具）

这里的 Tools 指后端代理可执行的能力（例如 `read_file`、`run_shell_safe`）。

### 4.1 添加步骤

1. 在 `backend/tools/gateway.py` 新增处理函数：
   - 命名约定：`_handle_<tool_name>(self, session_id, args)`
2. 在 `backend/policy/rules.py` 的 `ALLOWED_TOOLS` 加入工具名
3. 若涉及 shell 命令：同步更新 `ALLOWED_COMMANDS` / `FORBIDDEN_COMMANDS`
4. 在 `backend/agent/llm_client.py` 的 system prompt 里加入新工具说明
5. 重启并验证

### 4.2 示例：添加 `read_json`

在 `backend/tools/gateway.py` 增加：

```python
def _handle_read_json(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    path = args.get("path", "")
    workspace_path = self.workspace_manager.get_workspace_path(session_id)
    full_path = os.path.join(workspace_path, path.lstrip("/"))

    valid, error = self.policy_engine.validate_path(full_path, session_id)
    if not valid:
        raise ValueError(error)

    with open(full_path, "r") as f:
        return json.load(f)
```

在 `backend/policy/rules.py`:

```python
ALLOWED_TOOLS = {
    ..., "read_json"
}
```

---

## 5) 如何添加 Skills（Claude Code 本地技能）

这里的 Skills 指你在 Claude Code 中可复用的流程模板，不是后端 Tool。

### 5.1 推荐放置位置

- 项目级（推荐提交到仓库）：`.claude/skills/<skill-name>/SKILL.md`
- 用户级（仅本机）：`~/.claude/skills/<skill-name>/SKILL.md`

### 5.2 Skill 最小模板

```markdown
---
name: ctf-reverse-playbook
description: Reverse 题通用流程，含 strings/checksec/objdump 分析顺序
---

# Reverse Playbook

## When to use
- 用户要求做 reverse/pwn 静态分析时

## Steps
1. file + strings 快速识别
2. checksec + objdump 判断保护和符号
3. 输出下一步 payload/脚本
```

### 5.3 使用方式

- 在会话中通过 `use_skill("ctf-reverse-playbook")` 加载
- 或由技能匹配机制自动触发（取决于你的 Claude Code 配置）

---

## 6) 如何添加 MCP（Model Context Protocol）

MCP 用于把外部服务接入 Claude Code（例如浏览器、第三方 API、内部服务）。

### 6.1 在仓库根目录创建 `.mcp.json`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["scripts/mcp_server.py"],
      "env": {
        "API_TOKEN": "${API_TOKEN}"
      }
    }
  }
}
```

### 6.2 注意事项

- 不要把密钥硬编码进仓库，优先用环境变量
- MCP 配置变更后，重启 Claude Code 会话
- 先做只读工具，再逐步开放写操作

---

## 7) Skills / MCP / Tools 的区别

- **Tools（本项目后端）**：Agent 在你的服务里真正执行的能力
- **Skills（Claude 侧）**：工作流/策略模板，用于指导如何做事
- **MCP（Claude 侧）**：外部系统连接层，让 Claude 能调用外部工具

一句话：

- Tool = 执行能力
- Skill = 执行方法
- MCP = 执行通道

## 8) License

MIT
