# Web安全与渗透题解合集

这是一个 CTF / 靶场复盘仓库，主要收录 Web、安全研究和内网渗透相关题目的环境文件、利用脚本、截图与题解笔记。每个编号目录基本对应一题，方便按题目单独查看、复现和回顾思路。

## 目录总览

| 目录 | 题目 | 主要内容 |
| --- | --- | --- |
| `1. EzPing/` | EzPing | Flask 命令拼接、WAF 绕过、`UTF-7` 注入 |
| `2. EzDomain-flag01/` | EzDomain-flag01 | Minecraft + Log4Shell 入口、反弹 Shell 链路 |
| `3. EzDomain-flag02/` | EzDomain-flag02 | 域内提权、Kerberoast、DCSync、Pass-the-Ticket |
| `4. 博丽神社的御神签/` | 博丽神社的御神签 | JWT / Supabase、tar 符号链接、模板注入 |
| `5. Ezff/` | Ezff | Java 反序列化、Fury、OGNL、字符 oracle |
| `6. EzOmniProbe/` | EzOmniProbe | Session 竞争、Node.js vm 逃逸、setuid 提权 |

## 每题内容

### 1. EzPing
题目围绕一个 Flask 接口展开，核心是绕过黑名单 WAF，在受限输入下构造命令执行。

### 2. EzDomain-flag01
以 Minecraft 服务为入口，结合 Log4Shell 触发远程加载，完成初步拿 shell。

### 3. EzDomain-flag02
围绕 Windows 域环境展开，包含权限枚举、凭据提取、Kerberoast、DCSync 和票据传递等步骤。

### 4. 博丽神社的御神签
题解涉及前后端接口、JWT 角色、tar 包符号链接绕过，以及模板注入读取敏感文件。

### 5. Ezff
主要分析 Java 程序和序列化链，利用 Fury 反序列化与 OGNL 组合构造利用链。

### 6. EzOmniProbe
题解展示了会话竞争、沙箱逃逸和本地提权的完整链路，最终通过 setuid 程序拿到高权限结果。

## 仓库里放了什么

- 每题的题解 Markdown
- 利用脚本和辅助脚本
- 题目截图和过程截图
- 需要本地复现时用到的 Dockerfile、样例数据和工具文件

## 复现提醒

- 一些目录包含大字典、二进制工具和第三方工具包，体积较大，按需打开即可。
- 目录中的可执行文件和样例 payload 仅用于靶场复现，请在隔离环境中使用。
- 如果你只想看思路，直接打开对应目录下的题解 `.md` 文件就行。

## 推荐阅读顺序

1. 先看对应题目的题解 Markdown
2. 再看利用脚本和截图
3. 最后再看 Dockerfile、辅助工具和本地复现文件

---

最后更新：2026-05-25
