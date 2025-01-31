import asyncio
import os
import sys
sys.path.append('/Users/jacob/claude_home/OllamaAssist/src')
from mcp_client import mcp

# Use a path inside our allowed directory
TEST_DIR = "/Users/jacob/claude_home/OllamaAssist/tmp_test"
TEST_FILE = os.path.join(TEST_DIR, "test.txt")
TEST_CONTENT = "Hello, this is a test file"

async def setup_test_files():
    """Create test directory and file"""
    try:
        os.makedirs(TEST_DIR, exist_ok=True)
        with open(TEST_FILE, 'w') as f:
            f.write(TEST_CONTENT)
    except Exception as e:
        print(f"Setup error: {e}")

async def cleanup_test_files():
    """Clean up test files"""
    try:
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        if os.path.exists(TEST_DIR):
            os.rmdir(TEST_DIR)
    except Exception as e:
        print(f"Cleanup error: {e}")

async def test_direct_mcp():
    """Test direct MCP filesystem operations"""
    print("\nTesting direct MCP calls:")
    result = await mcp(server='filesystem', tool='read_file', arguments={'path': TEST_FILE})
    print(f"Direct read result: {result}")
    return "Test direct MCP passed!" if TEST_CONTENT in str(result) else "Direct MCP test failed!"

async def test_tools_layer():
    """Test our tools.py layer"""
    print("\nTesting tools.py layer:")
    from tools import filesystem
    result = await filesystem("read", TEST_FILE)
    print(f"Tools layer read result: {result}")
    return "Test tools layer passed!" if TEST_CONTENT in str(result) else "Tools layer test failed!"

async def main():
    """Run all tests"""
    print("\nStarting tests...")
    
    # First check if filesystem server is available
    available_servers = await mcp(tool='list_available_servers')
    print(f"\nAvailable servers: {available_servers}")
    if '"filesystem"' not in str(available_servers):
        print("Error: Filesystem server not available!")
        return

    await setup_test_files()
    
    try:
        # Test both direct MCP and our tools layer
        result1 = await test_direct_mcp()
        result2 = await test_tools_layer()
        
        print(f"\nResults:\n{result1}\n{result2}")

    except Exception as e:
        print(f"Error during tests: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cleanup_test_files()

if __name__ == "__main__":
    asyncio.run(main())