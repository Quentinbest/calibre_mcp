# Calibre MCP 服务器

[English](README.md) | [中文](README_zh.md)

一个 Model Context Protocol (MCP) 服务器，为您的本地 [Calibre](https://calibre-ebook.com/) 库提供接口。这允许 AI 代理（如 Claude 或 Cursor）搜索、检索详情、添加和转换 Calibre 库中的书籍。

## 功能

- **搜索书籍**：按标题、作者或其他元数据查询您的库。
- **获取详情**：检索特定书籍的完整元数据，包括可用格式和文件路径。
- **添加书籍**：从本地文件系统向您的库添加新书文件。
- **转换书籍**：使用 Calibre 的 `ebook-convert` 工具在格式之间转换书籍（例如，EPUB 转 MOBI）。
- **库管理**：删除书籍、导出书籍到特定目录。
- **元数据管理**：更新书籍详情、管理标签、设置封面。
- **内容与发现**：读取书籍内容、获取封面路径、列出分类、检查库健康状况。

## 前置要求

- **Python 3.10+**
- **Calibre**：`calibredb` 和 `ebook-convert` 命令行工具必须已安装并在您的系统 PATH 中可访问。
  - 在 macOS 上，这些通常位于 `/Applications/calibre.app/Contents/MacOS/`，或者链接到 `/usr/local/bin` 或 `/opt/homebrew/bin`。
  - 通过在终端运行 `calibredb --version` 来验证安装。

## 安装

1. **克隆或复制仓库**：
   确保您拥有 `calibre_mcp` 目录和 `requirements.txt`。

2. **安装依赖**：
   建议使用虚拟环境。
   ```bash
   pip install -r requirements.txt
   ```

## 配置

如果您的 Calibre 库不在默认位置，服务器需要库的路径。

- **环境变量**：`CALIBRE_LIBRARY_PATH`
  - 示例：`/Users/username/Calibre Library`

## 使用

您可以直接运行服务器进行测试，但它设计为由 MCP 客户端运行。

### 手动运行（用于测试）
```bash
# 可选：设置库路径
export CALIBRE_LIBRARY_PATH="/path/to/your/library"

# 运行服务器
python3 server.py
```

### 使用 Docker 运行

1. **构建镜像**：
   ```bash
   docker build -t calibre-mcp .
   ```

2. **运行容器**：
   您需要将 Calibre 库挂载到容器中。
   ```bash
   docker run -i --rm \
     -v "/path/to/your/library:/library" \
     -e CALIBRE_LIBRARY_PATH="/library" \
     calibre-mcp
   ```

   或者使用 Docker Compose：
   ```bash
   export CALIBRE_LIBRARY_PATH="/path/to/your/library"
   docker-compose up --build
   ```

   *注意：当与 Claude Desktop 等 MCP 客户端一起使用时，您需要配置客户端以运行 `docker run` 命令。有关详细配置说明，请参阅 [Docker 设置指南](docs/docker_setup_zh.md)。*


## 客户端配置

### Claude Desktop

将以下内容添加到您的 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "calibre": {
      "command": "/path/to/python3",
      "args": [
        "/absolute/path/to/calibre_mcp/server.py"
      ],
      "env": {
        "CALIBRE_LIBRARY_PATH": "/absolute/path/to/Calibre Library"
      }
    }
  }
}
```
*注意：将 `/path/to/python3` 替换为您的实际 Python 可执行文件路径（运行 `which python3` 查找）。*

### Cursor

1. 转到 **Cursor Settings** > **Features** > **MCP**。
2. 点击 **Add New MCP Server**。
3. **Name**: Calibre
4. **Type**: stdio
5. **Command**: `/path/to/python3` (例如 `/usr/bin/python3` 或您的 venv 路径)
6. **Arguments**: `/absolute/path/to/calibre_mcp/server.py`
7. **Environment Variables**:
   - Key: `CALIBRE_LIBRARY_PATH`
   - Value: `/absolute/path/to/Calibre Library`

## 工具参考

| 工具 | 描述 | 参数 | 返回 |
|------|-------------|-----------|---------|
| `search_books` | 在库中搜索书籍。 | `query` (string): 搜索查询 (例如 `title:Python`) | 书籍列表 (`id`, `title`, `authors`) |
| `get_book_details` | 获取特定书籍的详细元数据。 | `book_id` (int): Calibre 书籍 ID | 包含完整元数据的字典 |
| `add_book` | 向库添加新文件。 | `file_path` (string): 文件的绝对路径 | 包含新书籍 ID 的成功消息 |
| `convert_book` | 将书籍转换为不同格式。 | `book_id` (int), `output_format` (string) | 成功消息 |
| `delete_book` | 从库中永久删除书籍。 | `book_id` (int) | 状态消息 |
| `export_book` | 将书籍导出到特定目录。 | `book_id` (int), `output_dir` (string) | 状态消息 |
| `update_book` | 更新书籍元数据。 | `book_id` (int), `title` (str, 可选), `authors` (str, 可选) | 状态消息 |
| `manage_tags` | 添加或移除书籍标签。 | `book_id` (int), `add_tags` (list), `remove_tags` (list) | 状态消息 |
| `set_cover` | 设置书籍封面图片。 | `book_id` (int), `cover_path` (string) | 状态消息 |
| `get_cover_path` | 获取书籍封面的本地路径。 | `book_id` (int) | 封面图片的绝对路径 |
| `read_book_content` | 读取书籍的文本内容。 | `book_id` (int) | 文本内容（如果过大则截断） |
| `list_categories` | 列出可用分类。 | `category_type` (string): 例如 `tags`, `authors` | 分类名称列表 |
| `check_library` | 对库数据库运行一致性检查。 | 无 | 检查报告 |
| `get_library_stats` | 获取关于库的统计信息。 | 无 | 统计字典 |

## 故障排除

- **`calibredb executable not found`**：确保包含 `calibredb` 的目录在您的系统 PATH 中，或者您正在使用正确的环境变量启动 MCP 客户端。
- **`Book not found`**：使用 `search_books` 验证书籍 ID。
- **转换失败**：确保已安装 `ebook-convert`。某些转换（例如受 DRM 保护的文件）可能会失败。
