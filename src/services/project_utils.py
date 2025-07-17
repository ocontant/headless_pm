"""
Project utilities for filesystem operations and name sanitization.
Security-focused implementation to prevent shell injection and path traversal attacks.
"""

import re
import os
from typing import Dict, Set
from pathlib import Path

# Comprehensive list of shell special characters that must be excluded
SHELL_SPECIAL_CHARS = {
    # Shell operators and redirections
    '|', '&', ';', '(', ')', '<', '>', '!', '?', '*', '[', ']', '{', '}',
    # Path separators and traversal
    '/', '\\', '..',
    # Variable expansion and command substitution
    '$', '`', '"', "'", 
    # Whitespace and control characters
    ' ', '\t', '\n', '\r', '\0',
    # Other potentially dangerous characters
    '~', '^', '%', '=', '+', ':', '@', '#'
}

def sanitize_project_name(project_name: str) -> str:
    """
    Sanitize project name for safe filesystem usage with maximum security.
    
    Security measures:
    - Only allows alphanumeric characters, hyphens, and underscores
    - Converts to lowercase for consistency
    - Prevents all shell special characters
    - Limits length to prevent buffer overflows
    - Ensures valid filename format
    
    Args:
        project_name: The original project name
        
    Returns:
        A filesystem-safe version of the project name
        
    Raises:
        ValueError: If project name cannot be sanitized to a valid format
    """
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty")
    
    # Start with basic string
    sanitized = str(project_name).strip()
    
    # Remove all characters that are not alphanumeric, hyphen, or underscore
    # This is the most restrictive approach for maximum security
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', sanitized)
    
    # Replace multiple consecutive separators with single hyphen
    sanitized = re.sub(r'[-_]+', '-', sanitized)
    
    # Remove leading/trailing separators
    sanitized = sanitized.strip('-_')
    
    # Convert to lowercase for consistency
    sanitized = sanitized.lower()
    
    # Ensure minimum length
    if len(sanitized) < 1:
        raise ValueError(f"Project name '{project_name}' results in empty sanitized name")
    
    # Limit length to prevent issues
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip('-_')
    
    # Ensure it doesn't start with a dot or hyphen (hidden files/invalid names)
    if sanitized.startswith('.') or sanitized.startswith('-'):
        sanitized = 'proj-' + sanitized.lstrip('.-')
    
    # Final validation - must match strict pattern
    if not re.match(r'^[a-z0-9][a-z0-9\-_]*[a-z0-9]$|^[a-z0-9]$', sanitized):
        raise ValueError(f"Project name '{project_name}' cannot be safely sanitized")
    
    return sanitized

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem usage.
    
    Args:
        filename: The original filename
        
    Returns:
        A filesystem-safe version of the filename
        
    Raises:
        ValueError: If filename cannot be sanitized to a valid format
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    # Extract file extension if present
    path_obj = Path(filename)
    name_part = path_obj.stem
    extension = path_obj.suffix
    
    # Sanitize the name part (same rules as project names)
    if not name_part:
        raise ValueError("Filename must have a name part")
    
    # Remove all unsafe characters from name
    sanitized_name = re.sub(r'[^a-zA-Z0-9\-_]', '', name_part)
    sanitized_name = re.sub(r'[-_]+', '-', sanitized_name)
    sanitized_name = sanitized_name.strip('-_').lower()
    
    if not sanitized_name:
        raise ValueError(f"Filename '{filename}' results in empty sanitized name")
    
    # Sanitize extension (only allow safe characters)
    if extension:
        sanitized_ext = re.sub(r'[^a-zA-Z0-9]', '', extension.lower())
        if sanitized_ext:
            extension = '.' + sanitized_ext
        else:
            extension = ''
    
    # Limit total length
    max_name_length = 50 - len(extension)
    if len(sanitized_name) > max_name_length:
        sanitized_name = sanitized_name[:max_name_length].rstrip('-_')
    
    sanitized_filename = sanitized_name + extension
    
    # Final validation
    if not re.match(r'^[a-z0-9][a-z0-9\-_]*(\.[a-z0-9]+)?$', sanitized_filename):
        raise ValueError(f"Filename '{filename}' cannot be safely sanitized")
    
    return sanitized_filename

def validate_path_security(file_path: str, base_path: str) -> str:
    """
    Validate that a file path is secure and doesn't escape the base directory.
    
    Args:
        file_path: The file path to validate
        base_path: The base directory that must contain the file
        
    Returns:
        The validated absolute path
        
    Raises:
        ValueError: If the path is not secure
    """
    if not file_path or not base_path:
        raise ValueError("Both file_path and base_path must be provided")
    
    # Check for obvious path traversal attempts
    if '..' in file_path or file_path.startswith('/') or '\\' in file_path:
        raise ValueError("Path contains invalid traversal characters")
    
    # Check for null bytes and other control characters
    if '\0' in file_path or any(ord(c) < 32 for c in file_path):
        raise ValueError("Path contains invalid control characters")
    
    # Resolve absolute paths
    try:
        abs_base = os.path.abspath(base_path)
        abs_file = os.path.abspath(os.path.join(base_path, file_path))
        
        # Ensure the file path is within the base directory
        if not abs_file.startswith(abs_base + os.sep) and abs_file != abs_base:
            raise ValueError("Path escapes base directory")
            
        return abs_file
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid path: {e}")

def sanitize_path_component(component: str) -> str:
    """
    Sanitize a single path component (directory or filename).
    
    Args:
        component: A single path component
        
    Returns:
        Sanitized path component
        
    Raises:
        ValueError: If component cannot be sanitized
    """
    if '/' in component or '\\' in component:
        raise ValueError("Path component cannot contain path separators")
    
    # For directories, use project name sanitization
    # For files, detect if it has an extension
    if '.' in component and not component.startswith('.'):
        return sanitize_filename(component)
    else:
        return sanitize_project_name(component)

def get_project_directory_path(project_name: str) -> str:
    """
    Get the filesystem directory path for a project.
    
    Args:
        project_name: The project name
        
    Returns:
        The full directory path for the project
    """
    sanitized_name = sanitize_project_name(project_name)
    return f"./projects/{sanitized_name}"

def get_project_docs_path(project_name: str) -> str:
    """
    Get the documentation directory path for a project.
    
    Args:
        project_name: The project name
        
    Returns:
        The documentation directory path
    """
    return f"{get_project_directory_path(project_name)}/docs"

def get_project_shared_path(project_name: str) -> str:
    """
    Get the shared files directory path for a project.
    
    Args:
        project_name: The project name
        
    Returns:
        The shared files directory path
    """
    return f"{get_project_directory_path(project_name)}/shared"

def get_project_instructions_path(project_name: str) -> str:
    """
    Get the instructions directory path for a project.
    
    Args:
        project_name: The project name
        
    Returns:
        The instructions directory path
    """
    return f"{get_project_directory_path(project_name)}/instructions"

def ensure_project_directories(project_name: str) -> Dict[str, str]:
    """
    Ensure all project directories exist and return their paths.
    
    Args:
        project_name: The project name
        
    Returns:
        Dictionary with all project directory paths
    """
    paths = {
        'base': get_project_directory_path(project_name),
        'docs': get_project_docs_path(project_name),
        'shared': get_project_shared_path(project_name),
        'instructions': get_project_instructions_path(project_name)
    }
    
    # Create all directories
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    
    return paths