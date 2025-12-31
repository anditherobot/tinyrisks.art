import subprocess
import os
import tempfile
import shutil
import pytest


class TestInitDbScript:
    """Tests for the init_db.py standalone script"""
    
    def test_init_db_script_exists(self):
        """Test that init_db.py script exists and is executable"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init_db.py')
        assert os.path.exists(script_path), "init_db.py script should exist"
        assert os.access(script_path, os.X_OK), "init_db.py should be executable"
    
    def test_init_db_script_runs_successfully(self):
        """Test that init_db.py executes successfully"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init_db.py')
        
        # Create a temporary directory for the test database
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy necessary files to temp dir
            temp_script = os.path.join(tmpdir, 'init_db.py')
            temp_models = os.path.join(tmpdir, 'models.py')
            
            shutil.copy(script_path, temp_script)
            shutil.copy(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models.py'),
                temp_models
            )
            
            # Run the script
            result = subprocess.run(
                ['python3', temp_script],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Script should succeed. stderr: {result.stderr}"
            assert "Database initialization complete" in result.stdout
    
    def test_init_db_script_is_idempotent(self):
        """Test that running init_db.py multiple times is safe"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init_db.py')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_script = os.path.join(tmpdir, 'init_db.py')
            temp_models = os.path.join(tmpdir, 'models.py')
            
            shutil.copy(script_path, temp_script)
            shutil.copy(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models.py'),
                temp_models
            )
            
            # Run the script twice
            result1 = subprocess.run(
                ['python3', temp_script],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            result2 = subprocess.run(
                ['python3', temp_script],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            assert result1.returncode == 0, "First run should succeed"
            assert result2.returncode == 0, "Second run should succeed"
            assert "Database initialization complete" in result2.stdout
    
    def test_init_db_script_returns_error_on_failure(self):
        """Test that init_db.py returns non-zero exit code on failure"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init_db.py')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_script = os.path.join(tmpdir, 'init_db.py')
            
            # Copy only the script, not models.py to trigger import error
            shutil.copy(script_path, temp_script)
            
            # Run the script without models.py
            result = subprocess.run(
                ['python3', temp_script],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            assert result.returncode != 0, "Script should fail when dependencies missing"
            assert "Missing dependencies" in result.stdout or "No module named" in result.stdout
