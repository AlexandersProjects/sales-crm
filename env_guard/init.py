# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# env_guard/init.py - Initialize .env from template files

from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import re


def parse_env_line(line: str) -> Tuple[Optional[str], Optional[str], bool]:
    """Parse a line from an env file.

    Returns:
        Tuple of (key, value, is_comment)
        - If line is a comment or empty: (None, None, True)
        - If line is KEY=VALUE: (key, value, False)
    """
    stripped = line.strip()

    # Empty line or comment
    if not stripped or stripped.startswith('#'):
        return (None, None, True)

    # Key-value pair
    if '=' in stripped:
        key, value = stripped.split('=', 1)
        return (key.strip(), value.strip(), False)

    # Malformed line (treat as comment)
    return (None, None, True)


def prompt_for_value(key: str, default: str) -> str:
    """Prompt user for a value with a default.

    Args:
        key: Environment variable name
        default: Default value to show in brackets

    Returns:
        User input or default if Enter was pressed
    """
    try:
        user_input = input(f"Enter value for {key} [{default}]: ")
        return user_input if user_input.strip() else default
    except (KeyboardInterrupt, EOFError):
        # Handle Ctrl+C or EOF gracefully
        print("\nOperation cancelled.")
        raise


def initialize_env(
    example_file: str,
    out_file: str,
    interactive: bool = False,
    overwrite: bool = False,
    keep_comments: bool = True,
    schema: Optional[Dict[str, Any]] = None
) -> Tuple[int, int, List[str]]:
    """Initialize .env file from example template.

    Args:
        example_file: Path to template file
        out_file: Path to output file
        interactive: Prompt user for each value
        overwrite: Allow overwriting existing file
        keep_comments: Preserve comments from template
        schema: Optional schema dict for validation

    Returns:
        Tuple of (total_vars, vars_needing_values, placeholder_keys)

    Raises:
        FileNotFoundError: If example_file doesn't exist
        FileExistsError: If out_file exists and overwrite=False
        PermissionError: If cannot write to out_file
    """
    example_path = Path(example_file)
    out_path = Path(out_file)

    # Check if example file exists
    if not example_path.exists():
        raise FileNotFoundError(f"Example file not found: {example_file}")

    # Check if output file exists
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"{out_file} already exists. Use --overwrite to replace.")

    # Read template file
    try:
        with open(example_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except PermissionError:
        raise PermissionError(f"Cannot read {example_file} (permission denied)")

    # Process lines
    output_lines = []
    total_vars = 0
    placeholder_keys = []

    # Common placeholder patterns
    placeholder_patterns = [
        r'^your-.*-here$',
        r'^<.*>$',
        r'^changeme$',
        r'^replace.*$',
        r'^example.*$',
        r'^TODO.*$',
        r'^\.\.\.$',
        r'^$',  # Empty values
    ]

    for line in lines:
        key, value, is_comment = parse_env_line(line)

        if is_comment:
            if keep_comments:
                output_lines.append(line)
            continue

        if key is None:
            # Shouldn't happen, but handle gracefully
            output_lines.append(line)
            continue

        total_vars += 1

        # Check if value is a placeholder
        is_placeholder = False
        if value:
            for pattern in placeholder_patterns:
                if re.match(pattern, value, re.IGNORECASE):
                    is_placeholder = True
                    break
        else:
            is_placeholder = True

        if is_placeholder:
            placeholder_keys.append(key)

        # Interactive mode: prompt for value
        if interactive:
            new_value = prompt_for_value(key, value or "")
            output_lines.append(f"{key}={new_value}\n")
        else:
            # Non-interactive: preserve original
            output_lines.append(line)

    # Write output file
    try:
        # Ensure parent directory exists
        if out_path.parent and not out_path.parent.exists():
            out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
    except PermissionError:
        raise PermissionError(f"Cannot write to {out_file} (permission denied)")

    return (total_vars, len(placeholder_keys), placeholder_keys)

