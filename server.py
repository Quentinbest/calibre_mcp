import os
import subprocess
import json
import shutil
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Calibre MCP Server")

# Configuration
CALIBRE_LIBRARY_PATH = os.environ.get("CALIBRE_LIBRARY_PATH")

def get_calibredb_cmd() -> List[str]:
    """Returns the base command for calibredb, including library path if set."""
    cmd = ["calibredb"]
    if CALIBRE_LIBRARY_PATH:
        cmd.extend(["--with-library", CALIBRE_LIBRARY_PATH])
    return cmd

def run_calibredb(args: List[str]) -> str:
    """Runs a calibredb command and returns the stdout."""
    cmd = get_calibredb_cmd() + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"calibredb command failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("calibredb executable not found. Please ensure Calibre is installed and in your PATH.")

def _search_books(query: str) -> List[Dict[str, Any]]:
    # Use 'list' command with --search and JSON output
    # Fields: id, title, authors
    args = [
        "list",
        "--search", query,
        "--for-machine",  # JSON output
        "--fields", "id,title,authors"
    ]
    
    try:
        output = run_calibredb(args)
        books = json.loads(output)
        return books
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse calibredb output.")
    except RuntimeError as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_books(query: str) -> List[Dict[str, Any]]:
    """
    Search for books in the Calibre library.
    
    Args:
        query: The search query (e.g., title, author).
        
    Returns:
        A list of books matching the query.
    """
    return _search_books(query)

def _get_book_details(book_id: int) -> Dict[str, Any]:
    # calibredb list --search "id:123" --for-machine
    args = [
        "list",
        "--search", f"id:{book_id}",
        "--for-machine"
    ]
    
    try:
        output = run_calibredb(args)
        books = json.loads(output)
        if not books:
            return {"error": f"Book with ID {book_id} not found."}
        return books[0]
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_book_details(book_id: int) -> Dict[str, Any]:
    """
    Get metadata for a specific book.
    
    Args:
        book_id: The ID of the book.
        
    Returns:
        Metadata for the book.
    """
    return _get_book_details(book_id)

def _add_book(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    args = ["add", file_path]
    
    try:
        output = run_calibredb(args)
        # Output typically: "Added book ids: 123"
        return output.strip()
    except RuntimeError as e:
        return f"Error adding book: {str(e)}"

@mcp.tool()
def add_book(file_path: str) -> str:
    """
    Add a new book file to the library.
    
    Args:
        file_path: The absolute path to the book file.
        
    Returns:
        Success message with the new Book ID.
    """
    return _add_book(file_path)

def _convert_book(book_id: int, output_format: str) -> str:
    # 1. Find the book and its source file
    details = _get_book_details(book_id)
    if "error" in details:
        return details["error"]
    
    formats = details.get("formats", [])
    if not formats:
        return "Error: No source formats found for this book."
    
    # Pick the first available format as source
    # formats is a list of absolute paths in the library
    source_file = formats[0]
    
    # Create a temporary output path
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as tmp:
        output_file = tmp.name
        
    try:
        # 2. Run ebook-convert
        convert_cmd = ["ebook-convert", source_file, output_file]
        subprocess.run(convert_cmd, check=True, capture_output=True)
        
        # 3. Add the new format to the book
        # calibredb add_format id file
        add_fmt_args = ["add_format", str(book_id), output_file]
        run_calibredb(add_fmt_args)
        
        return f"Successfully converted book {book_id} to {output_format}."
        
    except subprocess.CalledProcessError as e:
        return f"Error converting book: {e.stderr if e.stderr else str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Cleanup temp file
        if os.path.exists(output_file):
            os.remove(output_file)

@mcp.tool()
def convert_book(book_id: int, output_format: str) -> str:
    """
    Convert a book to a new format.
    
    Args:
        book_id: The ID of the book to convert.
        output_format: The desired output format (e.g., 'mobi', 'epub').
        
    Returns:
        Status message.
    """
    return _convert_book(book_id, output_format)

if __name__ == "__main__":
    mcp.run()
