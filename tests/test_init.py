# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License")

import pytest
from env_guard.init import initialize_env, parse_env_line, prompt_for_value
from env_guard.cli import main


class TestInitModule:
    """Test the init module functions"""

    def test_parse_env_line_comment(self):
        """Test parsing comment lines"""
        key, value, is_comment = parse_env_line("# This is a comment")
        assert key is None
        assert value is None
        assert is_comment is True

    def test_parse_env_line_empty(self):
        """Test parsing empty lines"""
        key, value, is_comment = parse_env_line("")
        assert key is None
        assert value is None
        assert is_comment is True

    def test_parse_env_line_keyvalue(self):
        """Test parsing key=value lines"""
        key, value, is_comment = parse_env_line("DATABASE_URL=postgres://localhost/db")
        assert key == "DATABASE_URL"
        assert value == "postgres://localhost/db"
        assert is_comment is False

    def test_parse_env_line_keyvalue_with_spaces(self):
        """Test parsing key=value with spaces"""
        key, value, is_comment = parse_env_line("  PORT = 8000  ")
        assert key == "PORT"
        assert value == "8000"
        assert is_comment is False

    def test_parse_env_line_equals_in_value(self):
        """Test parsing when value contains equals sign"""
        key, value, is_comment = parse_env_line("SECRET=abc=123=xyz")
        assert key == "SECRET"
        assert value == "abc=123=xyz"
        assert is_comment is False

    def test_initialize_env_basic(self, tmp_path):
        """Test basic initialization without interaction"""
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "# Example config\n"
            "DATABASE_URL=your-database-url-here\n"
            "PORT=8000\n"
        )

        out_file = tmp_path / ".env"

        total, needs_values, placeholders = initialize_env(
            str(example_file),
            str(out_file),
            interactive=False,
            overwrite=False,
            keep_comments=True
        )

        assert total == 2
        assert needs_values == 1
        assert "DATABASE_URL" in placeholders
        assert "PORT" not in placeholders

        # Check output file exists and has correct content
        assert out_file.exists()
        content = out_file.read_text()
        assert "# Example config" in content
        assert "DATABASE_URL=your-database-url-here" in content
        assert "PORT=8000" in content

    def test_initialize_env_overwrite_protection(self, tmp_path):
        """Test that existing .env is not overwritten without flag"""
        example_file = tmp_path / "example.env"
        example_file.write_text("KEY=value\n")

        out_file = tmp_path / ".env"
        out_file.write_text("EXISTING=data\n")

        with pytest.raises(FileExistsError) as exc_info:
            initialize_env(
                str(example_file),
                str(out_file),
                interactive=False,
                overwrite=False
            )

        assert ".env already exists" in str(exc_info.value)

    def test_initialize_env_overwrite_allowed(self, tmp_path):
        """Test overwriting existing file with --overwrite"""
        example_file = tmp_path / "example.env"
        example_file.write_text("NEW_KEY=new_value\n")

        out_file = tmp_path / ".env"
        out_file.write_text("OLD_KEY=old_value\n")

        total, needs_values, placeholders = initialize_env(
            str(example_file),
            str(out_file),
            interactive=False,
            overwrite=True
        )

        assert total == 1
        content = out_file.read_text()
        assert "NEW_KEY=new_value" in content
        assert "OLD_KEY" not in content

    def test_initialize_env_missing_example(self, tmp_path):
        """Test error handling for missing example file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            initialize_env(
                str(tmp_path / "nonexistent.env"),
                str(tmp_path / ".env"),
                interactive=False
            )

        assert "not found" in str(exc_info.value).lower()

    def test_initialize_env_no_comments(self, tmp_path):
        """Test initialization without preserving comments"""
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "# This is a comment\n"
            "KEY=value\n"
            "# Another comment\n"
            "KEY2=value2\n"
        )

        out_file = tmp_path / ".env"

        initialize_env(
            str(example_file),
            str(out_file),
            interactive=False,
            keep_comments=False
        )

        content = out_file.read_text()
        assert "# This is a comment" not in content
        assert "# Another comment" not in content
        assert "KEY=value" in content
        assert "KEY2=value2" in content

    def test_initialize_env_placeholder_detection(self, tmp_path):
        """Test detection of various placeholder patterns"""
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "KEY1=your-api-key-here\n"
            "KEY2=<replace-me>\n"
            "KEY3=changeme\n"
            "KEY4=example-value\n"
            "KEY5=TODO\n"
            "KEY6=...\n"
            "KEY7=\n"
            "KEY8=actual-value\n"
        )

        out_file = tmp_path / ".env"

        total, needs_values, placeholders = initialize_env(
            str(example_file),
            str(out_file),
            interactive=False
        )

        assert total == 8
        assert needs_values == 7
        assert "KEY1" in placeholders
        assert "KEY2" in placeholders
        assert "KEY3" in placeholders
        assert "KEY4" in placeholders
        assert "KEY5" in placeholders
        assert "KEY6" in placeholders
        assert "KEY7" in placeholders
        assert "KEY8" not in placeholders


class TestInitCLI:
    """Test the init CLI command"""

    def test_init_default(self, tmp_path, monkeypatch):
        """Test basic initialization via CLI"""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Create example.env
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "# Example\n"
            "DATABASE_URL=your-url-here\n"
            "PORT=8000\n"
        )

        # Run init command
        with pytest.raises(SystemExit) as exc_info:
            main(["init"])

        assert exc_info.value.code == 0

        # Check .env was created
        env_file = tmp_path / ".env"
        assert env_file.exists()
        content = env_file.read_text()
        assert "DATABASE_URL=your-url-here" in content
        assert "PORT=8000" in content

    def test_init_custom_files(self, tmp_path, monkeypatch):
        """Test initialization with custom file paths"""
        monkeypatch.chdir(tmp_path)

        # Create custom template
        template = tmp_path / "template.env"
        template.write_text("CUSTOM_KEY=custom_value\n")

        # Run init with custom files
        with pytest.raises(SystemExit) as exc_info:
            main([
                "init",
                "--example-file", "template.env",
                "--out-file", ".env.custom"
            ])

        assert exc_info.value.code == 0

        # Check custom output was created
        out_file = tmp_path / ".env.custom"
        assert out_file.exists()
        content = out_file.read_text()
        assert "CUSTOM_KEY=custom_value" in content

    def test_init_with_validation(self, tmp_path, monkeypatch):
        """Test initialization with schema validation"""
        monkeypatch.chdir(tmp_path)

        # Create example.env
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "DATABASE_URL=postgres://localhost/db\n"
            "PORT=8000\n"
        )

        # Create schema
        schema_file = tmp_path / "rules.schema.yaml"
        schema_file.write_text(
            "required:\n"
            "  - DATABASE_URL\n"
            "  - PORT\n"
            "types:\n"
            "  PORT: int\n"
        )

        # Run init with validation
        with pytest.raises(SystemExit) as exc_info:
            main([
                "init",
                "--schema-file", "rules.schema.yaml"
            ])

        assert exc_info.value.code == 0

        # .env should exist
        env_file = tmp_path / ".env"
        assert env_file.exists()

    def test_init_missing_example_error(self, tmp_path, monkeypatch):
        """Test error when example file is missing"""
        monkeypatch.chdir(tmp_path)

        # Run init without example file
        with pytest.raises(SystemExit) as exc_info:
            main(["init"])

        assert exc_info.value.code == 2  # Error code

    def test_init_overwrite_protection_error(self, tmp_path, monkeypatch):
        """Test error when .env already exists"""
        monkeypatch.chdir(tmp_path)

        # Create example.env and .env
        example_file = tmp_path / "example.env"
        example_file.write_text("KEY=value\n")

        env_file = tmp_path / ".env"
        env_file.write_text("EXISTING=data\n")

        # Run init without --overwrite
        with pytest.raises(SystemExit) as exc_info:
            main(["init"])

        assert exc_info.value.code == 2  # Error code

        # .env should still have old content
        content = env_file.read_text()
        assert "EXISTING=data" in content

    def test_init_overwrite_flag(self, tmp_path, monkeypatch):
        """Test --overwrite flag"""
        monkeypatch.chdir(tmp_path)

        # Create example.env and .env
        example_file = tmp_path / "example.env"
        example_file.write_text("NEW_KEY=new_value\n")

        env_file = tmp_path / ".env"
        env_file.write_text("OLD_KEY=old_value\n")

        # Run init with --overwrite
        with pytest.raises(SystemExit) as exc_info:
            main(["init", "--overwrite"])

        assert exc_info.value.code == 0

        # .env should have new content
        content = env_file.read_text()
        assert "NEW_KEY=new_value" in content
        assert "OLD_KEY" not in content

    def test_init_no_comments(self, tmp_path, monkeypatch):
        """Test --no-comments flag"""
        monkeypatch.chdir(tmp_path)

        # Create example.env with comments
        example_file = tmp_path / "example.env"
        example_file.write_text(
            "# Comment\n"
            "KEY=value\n"
        )

        # Run init without comments
        with pytest.raises(SystemExit) as exc_info:
            main(["init", "--no-comments"])

        assert exc_info.value.code == 0

        # .env should not have comments
        env_file = tmp_path / ".env"
        content = env_file.read_text()
        assert "# Comment" not in content
        assert "KEY=value" in content


class TestPromptForValue:
    """Test interactive prompting (mocked)"""

    def test_prompt_with_default(self, monkeypatch):
        """Test prompt with user accepting default"""
        # Mock input to return empty string (accept default)
        monkeypatch.setattr('builtins.input', lambda _: "")

        result = prompt_for_value("API_KEY", "your-key-here")
        assert result == "your-key-here"

    def test_prompt_with_custom_value(self, monkeypatch):
        """Test prompt with user entering custom value"""
        # Mock input to return custom value
        monkeypatch.setattr('builtins.input', lambda _: "my-custom-key")

        result = prompt_for_value("API_KEY", "your-key-here")
        assert result == "my-custom-key"

    def test_prompt_keyboard_interrupt(self, monkeypatch):
        """Test handling of Ctrl+C during prompt"""
        # Mock input to raise KeyboardInterrupt
        def mock_input(_):
            raise KeyboardInterrupt()

        monkeypatch.setattr('builtins.input', mock_input)

        with pytest.raises(KeyboardInterrupt):
            prompt_for_value("API_KEY", "default")

