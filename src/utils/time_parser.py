"""
Time parsing utilities for time tracking functionality.
Supports shortcut formats like 1m, 1h, 1d, 1w, 1M for minutes, hours, days, weeks, months.
"""

import re
from typing import Union


def parse_time_to_minutes(time_input: Union[str, int, float]) -> int:
    """
    Parse time input to minutes.
    
    Supports:
    - Direct numbers (treated as minutes): 30, 45, 120
    - Shortcut formats: 1m, 2h, 1d, 1w, 1M
    - Negative values for time removal: -30, -1h
    
    Args:
        time_input: Time as string with shortcuts or numeric value
        
    Returns:
        Time in minutes (can be negative)
        
    Raises:
        ValueError: If the input format is invalid
    """
    if isinstance(time_input, (int, float)):
        return int(time_input)
    
    if not isinstance(time_input, str):
        raise ValueError("Time input must be a string or number")
    
    time_input = time_input.strip()
    if not time_input:
        raise ValueError("Time input cannot be empty")
    
    # Match pattern: optional minus, number, optional unit
    pattern = r'^(-?)(\d+(?:\.\d+)?)(m|h|d|w|M)?$'
    match = re.match(pattern, time_input, re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Invalid time format: '{time_input}'. Use formats like: 30, 1h, 2d, 1w, 1M")
    
    sign = -1 if match.group(1) == '-' else 1
    value = float(match.group(2))
    unit = match.group(3) if match.group(3) else 'm'
    
    # Convert to minutes based on unit
    multipliers = {
        'm': 1,          # minutes
        'h': 60,         # hours to minutes
        'd': 1440,       # days to minutes (24 * 60)
        'w': 10080,      # weeks to minutes (7 * 24 * 60)
        'M': 43200,      # months to minutes (30 * 24 * 60, approximate)
    }
    
    if unit not in multipliers:
        raise ValueError(f"Invalid time unit: '{unit}'. Supported units: m, h, d, w, M")
    
    minutes = int(value * multipliers[unit] * sign)
    return minutes


def format_minutes_to_human(minutes: int) -> str:
    """
    Format minutes into human-readable format.
    
    Args:
        minutes: Time in minutes (can be negative)
        
    Returns:
        Human-readable time string
    """
    if minutes == 0:
        return "0m"
    
    sign = "-" if minutes < 0 else ""
    abs_minutes = abs(minutes)
    
    # Convert to largest appropriate unit
    if abs_minutes >= 43200:  # 1 month or more
        months = abs_minutes // 43200
        remainder = abs_minutes % 43200
        if remainder == 0:
            return f"{sign}{months}M"
        else:
            days = remainder // 1440
            if days > 0:
                return f"{sign}{months}M {days}d"
            else:
                hours = remainder // 60
                if hours > 0:
                    return f"{sign}{months}M {hours}h"
                else:
                    return f"{sign}{months}M {remainder}m"
    
    elif abs_minutes >= 10080:  # 1 week or more
        weeks = abs_minutes // 10080
        remainder = abs_minutes % 10080
        if remainder == 0:
            return f"{sign}{weeks}w"
        else:
            days = remainder // 1440
            if days > 0:
                return f"{sign}{weeks}w {days}d"
            else:
                hours = remainder // 60
                if hours > 0:
                    return f"{sign}{weeks}w {hours}h"
                else:
                    return f"{sign}{weeks}w {remainder}m"
    
    elif abs_minutes >= 1440:  # 1 day or more
        days = abs_minutes // 1440
        remainder = abs_minutes % 1440
        if remainder == 0:
            return f"{sign}{days}d"
        else:
            hours = remainder // 60
            if hours > 0:
                return f"{sign}{days}d {hours}h"
            else:
                return f"{sign}{days}d {remainder}m"
    
    elif abs_minutes >= 60:  # 1 hour or more
        hours = abs_minutes // 60
        remainder = abs_minutes % 60
        if remainder == 0:
            return f"{sign}{hours}h"
        else:
            return f"{sign}{hours}h {remainder}m"
    
    else:  # Less than 1 hour
        return f"{sign}{abs_minutes}m"


def validate_time_entry(minutes: int, description: str = None) -> tuple[bool, str]:
    """
    Validate a time entry.
    
    Args:
        minutes: Time in minutes
        description: Optional description
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Reasonable limits: no more than 1 year (525,600 minutes) or less than -1 year
    max_minutes = 525600  # 1 year
    min_minutes = -525600  # -1 year
    
    if minutes > max_minutes:
        return False, f"Time entry too large. Maximum: {format_minutes_to_human(max_minutes)}"
    
    if minutes < min_minutes:
        return False, f"Time removal too large. Minimum: {format_minutes_to_human(min_minutes)}"
    
    if minutes == 0:
        return False, "Time entry cannot be zero"
    
    if description and len(description) > 500:
        return False, "Description cannot exceed 500 characters"
    
    return True, ""