#!/usr/bin/env python3
"""
Basic tests to verify the system works in CI environments
"""

import os
import sys
import subprocess
import tempfile

def test_version_file_exists():
    """Test that version.txt exists and is readable"""
    assert os.path.exists("version.txt"), "version.txt should exist"
    
    with open("version.txt", "r") as f:
        content = f.read().strip()
        assert content, "version.txt should not be empty"
        print(f"✅ version.txt contains: {content}")

def test_get_version_script_exists():
    """Test that get_version.py exists and is executable"""
    assert os.path.exists("get_version.py"), "get_version.py should exist"
    assert os.access("get_version.py", os.X_OK), "get_version.py should be executable"
    print("✅ get_version.py exists and is executable")

def test_basic_version_generation():
    """Test basic version generation functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("1.0.0")
        temp_version_file = f.name
    
    try:
        # Set up environment
        env = os.environ.copy()
        env['GITHUB_OUTPUT'] = '/tmp/test_output'
        
        # Run the version generation
        result = subprocess.run([
            sys.executable, 'get_version.py',
            '-f', temp_version_file,
            '-r', '.'
        ], capture_output=True, text=True, env=env)
        
        assert result.returncode == 0, f"get_version.py failed: {result.stderr}"
        print("✅ Basic version generation works")
        
    finally:
        os.unlink(temp_version_file)

def test_action_yml_exists():
    """Test that action.yml exists and is valid"""
    assert os.path.exists("action.yml"), "action.yml should exist"
    
    with open("action.yml", "r") as f:
        content = f.read()
        assert "name:" in content, "action.yml should have a name field"
        assert "description:" in content, "action.yml should have a description field"
        assert "inputs:" in content, "action.yml should have inputs field"
        assert "VERSION_FILE:" in content, "action.yml should have VERSION_FILE input"
        assert "CREATE_RELEASE:" in content, "action.yml should have CREATE_RELEASE input"
        assert "IS_SNAPSHOT:" in content, "action.yml should have IS_SNAPSHOT input"
        
    print("✅ action.yml exists and has required fields")

def test_required_files_exist():
    """Test that all required files exist"""
    required_files = [
        "README.md",
        "LICENSE", 
        "requirements.txt",
        "version.sh",
        "main.py"
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"{file} should exist"
    
    print("✅ All required files exist")

if __name__ == "__main__":
    print("Running basic tests...")
    
    test_version_file_exists()
    test_get_version_script_exists()
    test_basic_version_generation()
    test_action_yml_exists()
    test_required_files_exist()
    
    print("🎉 All basic tests passed!")
