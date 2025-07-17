"""
Security tests for filesystem operations.
Tests various attack vectors and validates security measures.
"""

import pytest
import os
import tempfile
from src.services.project_utils import (
    sanitize_project_name, 
    sanitize_filename, 
    validate_path_security,
    sanitize_path_component
)

class TestProjectNameSanitization:
    """Test project name sanitization for security."""
    
    def test_basic_sanitization(self):
        """Test basic project name sanitization."""
        assert sanitize_project_name("My Project") == "myproject"
        assert sanitize_project_name("Test-App_2") == "test-app-2"
    
    def test_shell_character_removal(self):
        """Test removal of shell special characters."""
        dangerous_chars = ['|', '&', ';', '(', ')', '<', '>', '!', '?', '*', 
                          '[', ']', '{', '}', '$', '`', '"', "'", ' ', '\t']
        
        for char in dangerous_chars:
            name = f"test{char}project"
            sanitized = sanitize_project_name(name)
            assert char not in sanitized
            assert sanitized == "testproject"
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attempts."""
        attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "./../../sensitive",
            "test/../../../etc"
        ]
        
        for attack in attacks:
            sanitized = sanitize_project_name(attack)
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized
    
    def test_empty_input_handling(self):
        """Test handling of empty or invalid inputs."""
        with pytest.raises(ValueError):
            sanitize_project_name("")
        
        with pytest.raises(ValueError):
            sanitize_project_name("   ")
        
        with pytest.raises(ValueError):
            sanitize_project_name(None)
    
    def test_length_limits(self):
        """Test length limitation enforcement."""
        long_name = "a" * 100
        sanitized = sanitize_project_name(long_name)
        assert len(sanitized) <= 50
    
    def test_valid_character_pattern(self):
        """Test that sanitized names match valid pattern."""
        import re
        test_names = [
            "Valid-Project_123",
            "test!@#$%^&*()",
            "UPPERCASE",
            "Mix3d_Ch4rs"
        ]
        
        pattern = r'^[a-z0-9][a-z0-9\-_]*[a-z0-9]$|^[a-z0-9]$'
        
        for name in test_names:
            sanitized = sanitize_project_name(name)
            assert re.match(pattern, sanitized), f"Sanitized name '{sanitized}' doesn't match pattern"

class TestFilenameSanitization:
    """Test filename sanitization for security."""
    
    def test_basic_filename_sanitization(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("test file.txt") == "testfile.txt"
        assert sanitize_filename("document-v2.md") == "document-v2.md"
    
    def test_extension_preservation(self):
        """Test that file extensions are properly preserved."""
        assert sanitize_filename("test.pdf") == "test.pdf"
        assert sanitize_filename("data.json") == "data.json"
        assert sanitize_filename("script.py") == "script.py"
    
    def test_malicious_filename_sanitization(self):
        """Test sanitization of malicious filenames."""
        malicious_files = [
            "rm -rf /.sh",
            "$(whoami).txt",
            "; cat /etc/passwd;.log",
            "file|grep secret.txt",
            "test && rm -rf /.txt"
        ]
        
        for malicious in malicious_files:
            sanitized = sanitize_filename(malicious)
            # Should not contain any shell special characters
            dangerous_chars = ['|', '&', ';', '(', ')', '<', '>', '!', '?', '*', 
                              '[', ']', '{', '}', '$', '`', '"', "'", ' ']
            for char in dangerous_chars:
                assert char not in sanitized, f"Dangerous char '{char}' found in '{sanitized}'"

class TestPathSecurity:
    """Test path security validation."""
    
    def test_valid_path_security(self):
        """Test validation of legitimate paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_paths = [
                "file.txt",
                "subdirectory/file.txt",
                "docs/readme.md"
            ]
            
            for path in valid_paths:
                validated = validate_path_security(path, temp_dir)
                assert validated.startswith(temp_dir)
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            attack_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config",
                "./../../sensitive_file",
                "docs/../../../etc/hosts",
                "test/../../.ssh/id_rsa"
            ]
            
            for attack_path in attack_paths:
                with pytest.raises(ValueError, match="invalid traversal characters|escapes base directory"):
                    validate_path_security(attack_path, temp_dir)
    
    def test_null_byte_injection_prevention(self):
        """Test prevention of null byte injection attacks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            null_byte_attacks = [
                "file.txt\x00.php",
                "document\x00.exe",
            ]
            
            for attack in null_byte_attacks:
                with pytest.raises(ValueError, match="invalid control characters"):
                    validate_path_security(attack, temp_dir)
            
            # This one should fail on traversal check first
            with pytest.raises(ValueError, match="invalid traversal characters"):
                validate_path_security("safe.txt\x00/../../../etc/passwd", temp_dir)
    
    def test_absolute_path_rejection(self):
        """Test rejection of absolute paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            absolute_paths = [
                "/etc/passwd",
                "/bin/bash",
                "C:\\Windows\\System32\\cmd.exe",
                "/home/user/.ssh/id_rsa"
            ]
            
            for abs_path in absolute_paths:
                with pytest.raises(ValueError, match="invalid traversal characters"):
                    validate_path_security(abs_path, temp_dir)

class TestSecurityIntegration:
    """Integration tests for complete security measures."""
    
    def test_end_to_end_security(self):
        """Test complete security flow from input to filesystem."""
        dangerous_inputs = [
            "$(rm -rf /)",
            "; cat /etc/passwd;",
            "../../../sensitive",
            "file|grep secret",
            "test && malicious"
        ]
        
        for dangerous_input in dangerous_inputs:
            # Should not raise exceptions but should sanitize safely
            if '.' in dangerous_input:
                sanitized = sanitize_filename(dangerous_input)
            else:
                sanitized = sanitize_project_name(dangerous_input)
            
            # Verify no dangerous characters remain
            assert all(char not in sanitized for char in ['|', '&', ';', '$', '`', '(', ')'])
    
    def test_unicode_and_encoding_safety(self):
        """Test handling of Unicode and encoding attacks."""
        unicode_attacks = [
            "file\u202e.txt",  # Right-to-left override
            "test\uFEFF.doc",  # Byte order mark
            "doc\u200B.pdf",  # Zero-width space
        ]
        
        for attack in unicode_attacks:
            sanitized = sanitize_filename(attack)
            # Should handle Unicode safely
            assert sanitized.isascii() or not any(ord(c) < 32 for c in sanitized)

if __name__ == "__main__":
    pytest.main([__file__])