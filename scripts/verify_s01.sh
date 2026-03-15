#!/bin/bash
# Verification script for S01: End-to-end test of MCP server
# 
# This script:
# 1. Starts the MCP server in stdio mode
# 2. Sends initialize and tools/list requests
# 3. Verifies mist_list_orgs appears in the tool list
# 4. Cleans up the server process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

PYTHON_BIN="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== S01 Verification Script ==="
echo ""

# Check if fastmcp CLI is available
if command -v fastmcp &> /dev/null; then
    echo "Found fastmcp CLI, using it for verification..."
    
    # Start server in background and list tools using fastmcp
    $PYTHON_BIN -m mist_mcp.server --transport stdio &
    SERVER_PID=$!
    
    sleep 3
    
    # Use fastmcp list to get tools
    if fastmcp list --command "$PYTHON_BIN -m mist_mcp.server" --json 2>/dev/null | grep -q "mist_list_orgs"; then
        echo -e "${GREEN}✓ SUCCESS: mist_list_orgs tool found${NC}"
        kill $SERVER_PID 2>/dev/null || true
        exit 0
    fi
    
    # If fastmcp didn't work, try alternative method
    kill $SERVER_PID 2>/dev/null || true
fi

# Fallback: Use Python script for verification
echo "Using Python fallback for verification..."

# Create a temporary Python verification script
VERIFY_SCRIPT=$(mktemp)

cat > "$VERIFY_SCRIPT" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""Simple verification that the server starts and responds to tools/list."""

import json
import subprocess
import sys
import time
from pathlib import Path

def main():
    project_dir = Path(__file__).parent
    
    # Start server process
    proc = subprocess.Popen(
        [sys.executable, "-m", "mist_mcp.server", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_dir,
    )
    
    try:
        # Wait for server to start
        time.sleep(2)
        
        # Send initialize request
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "verify", "version": "1.0.0"}
            }
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()
        
        # Send initialized notification
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "initialized"}) + "\n")
        proc.stdin.flush()
        
        time.sleep(1)
        
        # Send tools/list request
        tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        proc.stdin.write(json.dumps(tools_req) + "\n")
        proc.stdin.flush()
        
        # Read response
        time.sleep(2)
        
        # Read all available output
        output = ""
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            output += line
            # Try to find JSON-RPC response
            if '"method":"tools/list"' in line or (line.strip().startswith('{') and '"result"' in line):
                break
        
        # Check for mist_list_orgs in output
        if "mist_list_orgs" in output:
            print("SUCCESS: mist_list_orgs tool found in server response")
            return 0
        else:
            print(f"FAILED: mist_list_orgs not found in response:")
            print(output[:500])
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

if __name__ == "__main__":
    sys.exit(main())
PYTHON_SCRIPT

# Run the verification script
if python3 "$VERIFY_SCRIPT"; then
    echo ""
    echo -e "${GREEN}=== VERIFICATION PASSED ===${NC}"
    rm -f "$VERIFY_SCRIPT"
    exit 0
else
    echo ""
    echo -e "${RED}=== VERIFICATION FAILED ===${NC}"
    rm -f "$VERIFY_SCRIPT"
    exit 1
fi
