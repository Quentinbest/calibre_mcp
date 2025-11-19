# Calibre MCP Server

[English](README.md) | [中文](README_zh.md)

A Model Context Protocol (MCP) server that provides an interface to your local [Calibre](https://calibre-ebook.com/) library. This allows AI agents (like Claude or Cursor) to search, retrieve details, add, and convert books in your Calibre library.

## Features

- **Search Books**: Query your library by title, author, or other metadata.
- **Get Details**: Retrieve full metadata for specific books, including available formats and file paths.
- **Add Books**: Add new book files to your library from the local filesystem.
- **Convert Books**: Convert books between formats (e.g., EPUB to MOBI) using Calibre's `ebook-convert` tool.

## Prerequisites

- **Python 3.10+**
- **Calibre**: The `calibredb` and `ebook-convert` command-line tools must be installed and accessible in your system PATH.
  - On macOS, these are typically found in `/Applications/calibre.app/Contents/MacOS/` or linked to `/usr/local/bin` or `/opt/homebrew/bin`.
  - Verify installation by running `calibredb --version` in your terminal.

## Installation

1. **Clone or Copy the Repository**:
   Ensure you have the `calibre_mcp` directory and `requirements.txt`.

2. **Install Dependencies**:
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The server requires the path to your Calibre library if it is not in the default location.

- **Environment Variable**: `CALIBRE_LIBRARY_PATH`
  - Example: `/Users/username/Calibre Library`

## Usage

You can run the server directly for testing, but it is designed to be run by an MCP client.

### Running Manually (for testing)
```bash
# Optional: Set library path
export CALIBRE_LIBRARY_PATH="/path/to/your/library"

# Run the server
python3 server.py
```

### Running with Docker

1. **Build the image**:
   ```bash
   docker build -t calibre-mcp .
   ```

2. **Run the container**:
   You need to mount your Calibre library into the container.
   ```bash
   docker run -i --rm \
     -v "/path/to/your/library:/library" \
     -e CALIBRE_LIBRARY_PATH="/library" \
     calibre-mcp
   ```

   Or using Docker Compose:
   ```bash
   export CALIBRE_LIBRARY_PATH="/path/to/your/library"
   docker-compose up --build
   ```

   *Note: When using with an MCP client like Claude Desktop, you will need to configure the client to run the `docker run` command. See [Docker Setup Guide](docs/docker_setup.md) for detailed configuration instructions.*


## Client Configuration

### Claude Desktop

Add the following to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

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
*Note: Replace `/path/to/python3` with your actual Python executable path (run `which python3` to find it).*

### Cursor

1. Go to **Cursor Settings** > **Features** > **MCP**.
2. Click **Add New MCP Server**.
3. **Name**: Calibre
4. **Type**: stdio
5. **Command**: `/path/to/python3` (e.g., `/usr/bin/python3` or from your venv)
6. **Arguments**: `/absolute/path/to/calibre_mcp/server.py`
7. **Environment Variables**:
   - Key: `CALIBRE_LIBRARY_PATH`
   - Value: `/absolute/path/to/Calibre Library`

## Tools Reference

### `search_books`
Search for books in the library.
- **Arguments**:
  - `query` (string): The search query. Supports Calibre search syntax (e.g., `title:Python`, `author:Asimov`).
- **Returns**: List of books with `id`, `title`, and `authors`.

### `get_book_details`
Get detailed metadata for a specific book.
- **Arguments**:
  - `book_id` (integer): The internal Calibre ID of the book.
- **Returns**: Dictionary containing full metadata (formats, tags, comments, etc.).

### `add_book`
Add a new file to the library.
- **Arguments**:
  - `file_path` (string): Absolute path to the file to add.
- **Returns**: Success message with the new Book ID.

### `convert_book`
Convert a book to a different format.
- **Arguments**:
  - `book_id` (integer): The ID of the book to convert.
  - `output_format` (string): Target format (e.g., `mobi`, `pdf`, `docx`).
- **Returns**: Success message.

### `delete_book`
Delete a book from the library permanently.
- **Arguments**:
  - `book_id` (integer): The ID of the book to delete.
- **Returns**: Status message.

### `export_book`
Export a book to a specific directory.
- **Arguments**:
  - `book_id` (integer): The ID of the book to export.
  - `output_dir` (string): The destination directory.
- **Returns**: Status message.

### `update_book`
Update book metadata (title, authors).
- **Arguments**:
  - `book_id` (integer): The ID of the book.
  - `title` (string, optional): New title.
  - `authors` (string, optional): New authors (comma-separated).
- **Returns**: Status message.

### `manage_tags`
Add or remove tags from a book.
- **Arguments**:
  - `book_id` (integer): The ID of the book.
  - `add_tags` (list of strings, optional): Tags to add.
  - `remove_tags` (list of strings, optional): Tags to remove.
- **Returns**: Status message.

### `set_cover`
Set the cover image for a book.
- **Arguments**:
  - `book_id` (integer): The ID of the book.
  - `cover_path` (string): Absolute path to the image file.
- **Returns**: Status message.

### `get_cover_path`
Get the local path to the book's cover image.
- **Arguments**:
  - `book_id` (integer): The ID of the book.
- **Returns**: Absolute path to the cover image.

### `read_book_content`
Read the text content of a book.
- **Arguments**:
  - `book_id` (integer): The ID of the book.
- **Returns**: The text content of the book (truncated if very large).

### `list_categories`
List available categories (tags, authors, series, etc.).
- **Arguments**:
  - `category_type` (string): The type of category (e.g., `tags`, `authors`, `series`, `publisher`).
- **Returns**: List of category names.

### `check_library`
Run a consistency check on the library database.
- **Returns**: The report from the check command.

### `get_library_stats`
Get statistics about the library.
- **Returns**: Dictionary with counts of books, authors, and tags.

## Troubleshooting

- **`calibredb executable not found`**: Ensure the directory containing `calibredb` is in your system PATH, or that you are launching the MCP client with the correct environment variables.
- **`Book not found`**: Verify the Book ID using `search_books`.
- **Conversion Failures**: Ensure `ebook-convert` is installed. Some conversions (e.g., DRM-protected files) may fail.
