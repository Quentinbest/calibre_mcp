# Docker Setup Guide for Calibre MCP

This guide provides detailed instructions on how to run the Calibre MCP server using Docker and configure it with MCP clients like Claude Desktop.

## Prerequisites

- **Docker**: Ensure Docker is installed and running on your machine.
- **Calibre Library**: You must have a local Calibre library directory.

## 1. Build the Docker Image

First, clone the repository and build the Docker image:

```bash
git clone https://github.com/yourusername/calibre_mcp.git
cd calibre_mcp
docker build -t calibre-mcp .
```

## 2. Test the Container

Before configuring the client, verify that the container works and can access your library.

Replace `/path/to/your/library` with the actual path to your Calibre library.

```bash
docker run -i --rm \
  -v "/path/to/your/library:/library" \
  -e CALIBRE_LIBRARY_PATH="/library" \
  calibre-mcp
```

If the server starts without error (it might not output anything until it receives a request), it is working. You can verify it has access to `calibredb` by running:

```bash
docker run --rm calibre-mcp calibredb --version
```

## 3. Configure Claude Desktop

To use the Dockerized server with Claude Desktop, you need to configure it to run the `docker run` command.

Edit your `~/Library/Application Support/Claude/claude_desktop_config.json` file:

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

**Important Notes:**
- **Absolute Paths**: Ensure `/absolute/path/to/your/library` is the full absolute path on your host machine.
- **Volume Mounting**: The `-v` flag maps your host library to `/library` inside the container.
- **Environment Variable**: The `CALIBRE_LIBRARY_PATH` inside the container must match the mount point (e.g., `/library`).

## Troubleshooting

### Permission Issues
If you encounter permission errors when the container tries to access your library, you might need to run the container with the same user ID as your host user.

Add `--user $(id -u):$(id -g)` to the docker run command args:

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
*(Replace `1000:1000` with your actual UID:GID if different).*

### "calibredb executable not found"
This should not happen in the Docker image as it is pre-installed. If it does, ensure you built the image correctly using the provided `Dockerfile`.
