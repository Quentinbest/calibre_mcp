# Calibre MCP Docker 设置指南

本指南提供了有关如何使用 Docker 运行 Calibre MCP 服务器并将其配置为与 MCP 客户端（如 Claude Desktop）一起使用的详细说明。

## 前置要求

- **Docker**：确保您的机器上已安装并运行 Docker。
- **Calibre 库**：您必须拥有一个本地 Calibre 库目录。

## 1. 构建 Docker 镜像

首先，克隆仓库并构建 Docker 镜像：

```bash
git clone https://github.com/yourusername/calibre_mcp.git
cd calibre_mcp
docker build -t calibre-mcp .
```

## 2. 测试容器

在配置客户端之前，验证容器是否工作正常并能访问您的库。

将 `/path/to/your/library` 替换为您的 Calibre 库的实际路径。

```bash
docker run -i --rm \
  -v "/path/to/your/library:/library" \
  -e CALIBRE_LIBRARY_PATH="/library" \
  calibre-mcp
```

如果服务器启动且没有错误（它可能直到收到请求才输出任何内容），则说明它正在工作。您可以通过运行以下命令来验证它是否有权访问 `calibredb`：

```bash
docker run --rm calibre-mcp calibredb --version
```

## 3. 配置 Claude Desktop

要将 Docker 化的服务器与 Claude Desktop 一起使用，您需要将其配置为运行 `docker run` 命令。

编辑您的 `~/Library/Application Support/Claude/claude_desktop_config.json` 文件：

```json
{
  "mcpServers": {
    "calibre-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/absolute/path/to/your/library:/library",
        "-e",
        "CALIBRE_LIBRARY_PATH=/library",
        "calibre-mcp"
      ]
    }
  }
}
```

**重要提示：**
- **绝对路径**：确保 `/absolute/path/to/your/library` 是您主机上的完整绝对路径。
- **卷挂载**：`-v` 标志将您的主机库映射到容器内的 `/library`。
- **环境变量**：容器内的 `CALIBRE_LIBRARY_PATH` 必须与挂载点（例如 `/library`）匹配。

## 故障排除

### 权限问题
如果容器尝试访问您的库时遇到权限错误，您可能需要使用与主机用户相同的用户 ID 运行容器。

将 `--user $(id -u):$(id -g)` 添加到 docker run 命令参数中：

```json
      "args": [
        "run",
        "-i",
        "--rm",
        "--user",
        "1000:1000", 
        "-v",
        ...
```
*（如果不同，请将 `1000:1000` 替换为您的实际 UID:GID）。*

### "calibredb executable not found"
这在 Docker 镜像中不应该发生，因为它是预安装的。如果发生这种情况，请确保您使用提供的 `Dockerfile` 正确构建了镜像。
