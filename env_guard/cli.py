# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# main entry point (command-line interface)

import typer
from typer import Context
from importlib.metadata import version, PackageNotFoundError
from rich.console import Console
from rich.table import Table
from rich.text import Text
from env_guard.validator import EnvValidator, ValidationResult
from env_guard.schema_loader import load_schema
from env_guard.init import initialize_env
from env_guard import telemetry
from pathlib import Path
import subprocess
import re
import sys
import logging
from typing import List, Optional, Tuple, Dict
import time

app = typer.Typer()
console = Console()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def version_callback(value: bool):
    """Print version and exit."""
    if value:
        try:
            v = version("env_guard")
            typer.echo(f"env-guard version {v}")
        except PackageNotFoundError:
            typer.echo("env-guard version unknown (not installed)")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True
    )
):
    """env-guard: Environment variable validation tool"""
    # If no subcommand was provided, run 'check' by default
    if ctx.invoked_subcommand is None:
        ctx.invoke(ctx.command.commands["check"]) # ← Calls check() with its default parameters
        # env_file = ".env",  # Default from check()
        # schema_file = ".env.schema",  # Default from check()
        # show_all = False,  # Default from check()
        # strict = False,  # Default from check()
        # show_values = False  # Default from check()
    pass

@app.command()
def check(
    env_file: Optional[str] = typer.Option(None, "--env-file", help="Path to env file (default: .env)"),
    schema_file: str = typer.Option("rules.schema.yaml", "--schema-file", "--schema", help="Path to schema file"),
    json_out: bool = typer.Option(False, "--json", help="Output results as JSON"),
    yaml_out: bool = typer.Option(False, "--yaml", help="Output results as YAML"),
    show_secrets: bool = typer.Option(False, help="Show secret values in output (unsafe)"),
    safe_mode: bool = typer.Option(True, help="Safe mode: avoid exposing secrets and sensitive suggestions"),
    strict: bool = typer.Option(False, help="Strict mode: unknown env vars are errors"),
    show_ok: bool = typer.Option(False, help="Show OK entries in table output"),
    highlight: bool = typer.Option(True, help="Highlight full rows by status: green=ok, yellow=warning, red=error"),
    fix: bool = typer.Option(False, help="Automatically apply simple fixes (defaults, boolean normalization)"),
    dry_run: bool = typer.Option(True, help="When used with --fix: preview fixes without writing"),
    backup: bool = typer.Option(True, help="When used with --fix: create a backup of the original env file as .bak"),
    profile: str = typer.Option(None, help="Profile name for multi-env files (.env.<profile>)"),
    no_telemetry: bool = typer.Option(False, "--no-telemetry", help="Disable telemetry for this run")
) -> None:
    """Validate .env file against schema"""
    # Initialize telemetry tracker
    start_time = time.time()
    tracker = telemetry.create_tracker()
    if no_telemetry:
        tracker.enabled = False

    # Default to .env if no file specified
    if env_file is None:
        env_file = ".env"

    # resolve profile
    env_path = env_file
    if profile:
        p = Path(env_file)
        env_path = str(p.with_name(f"{p.stem}.{profile}{p.suffix}"))

    schema = load_schema(schema_file)
    validator = EnvValidator(env_path, schema, show_secrets=show_secrets, strict=strict, profile=profile)
    results: List[ValidationResult] = validator.run_all()

    # check git uncommitted changes for the env file
    try:
        git_cmd = ["git", "status", "--porcelain", "--", env_path]
        proc = subprocess.run(git_cmd, capture_output=True, text=True, check=False)
        git_dirty = proc.stdout.strip() != ""
    except Exception:
        git_dirty = False

    # summary counts
    counts = {"ok": 0, "warning": 0, "error": 0}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1

    # Display files being used (only for human-readable output)
    if not json_out and not yaml_out:
        console.print(f"[cyan]📄 Environment file:[/cyan] {env_path}")
        console.print(f"[cyan]📋 Schema file:[/cyan] {schema_file}")
        if profile:
            console.print(f"[cyan]🏷️  Profile:[/cyan] {profile}")
        console.print()  # blank line for spacing

    # machine output
    if json_out:
        # Use plain print to avoid ANSI color codes in JSON output
        print(validator.to_json(show_secrets=show_secrets and not safe_mode))
        # Track telemetry before exit
        runtime_ms = int((time.time() - start_time) * 1000)
        findings_by_type = telemetry.calculate_findings_by_type(results)
        findings_by_severity = telemetry.calculate_findings_by_severity(results)
        estimated_time_saved = telemetry.estimate_time_saved(
            findings_total=counts["error"] + counts["warning"],
            auto_fixes_applied=0
        )
        tracker.track_run_completed(
            command="check",
            files_scanned=1,
            findings_total=counts["error"] + counts["warning"],
            findings_by_type=findings_by_type,
            findings_by_severity=findings_by_severity,
            auto_fixes_applied=0,
            runtime_ms=runtime_ms,
            estimated_time_saved_minutes=estimated_time_saved,
            sample_rate=1.0,
        )
        raise typer.Exit(code=1 if counts["error"] else (2 if counts["warning"] else 0))
    if yaml_out:
        # Use plain print to avoid ANSI color codes in YAML output
        print(validator.to_yaml(show_secrets=show_secrets and not safe_mode))
        # Track telemetry before exit
        runtime_ms = int((time.time() - start_time) * 1000)
        findings_by_type = telemetry.calculate_findings_by_type(results)
        findings_by_severity = telemetry.calculate_findings_by_severity(results)
        estimated_time_saved = telemetry.estimate_time_saved(
            findings_total=counts["error"] + counts["warning"],
            auto_fixes_applied=0
        )
        tracker.track_run_completed(
            command="check",
            files_scanned=1,
            findings_total=counts["error"] + counts["warning"],
            findings_by_type=findings_by_type,
            findings_by_severity=findings_by_severity,
            auto_fixes_applied=0,
            runtime_ms=runtime_ms,
            estimated_time_saved_minutes=estimated_time_saved,
            sample_rate=1.0,
        )
        raise typer.Exit(code=1 if counts["error"] else (2 if counts["warning"] else 0))
    # human output
    title = Text("Env Guard Results")
    title.append(f" — {counts['error']} errors, {counts['warning']} warnings, {counts['ok']} ok")
    console.rule(title)

    if git_dirty:
        console.print("[yellow]Warning:[/yellow] The env file has uncommitted changes. Consider committing or stashing before running fixes.")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status")
    table.add_column("Key")
    table.add_column("Value")
    table.add_column("Expected")
    table.add_column("Message")
    table.add_column("Location")

    for r in results:
        if r.status == "ok" and not show_ok:
            continue
        # determine visible value: redact secrets unless explicitly allowed
        if r.secret and not show_secrets:
            val = "****"
        else:
            val = r.found if r.found is not None else "<none>"

        # format location (file:line) — if line unknown, show just file or '-'
        if r.file and r.line:
            loc = f"{r.file}:{r.line}"
        elif r.file:
            loc = f"{r.file}:?"
        else:
            loc = "-"

        # determine status text and optional full-row style
        status_plain = r.status.upper()
        expected = r.expected or "-"
        msg = r.message
        # keep suggestions separate (don't append to message). They will be rendered in the Suggestions section below.

        if highlight:
            # full-row coloring
            if r.status == "ok":
                row_style = "green"
            elif r.status == "warning":
                row_style = "yellow"
            else:
                row_style = "red"
            table.add_row(status_plain, r.key, val, expected, msg, loc, style=row_style)
        else:
            # inline coloring for status only
            if r.status == "ok":
                status_text = f"[green]{status_plain}[/green]"
            elif r.status == "warning":
                status_text = f"[yellow]{status_plain}[/yellow]"
            else:
                status_text = f"[red]{status_plain}[/red]"
            table.add_row(status_text, r.key, val, expected, msg, loc)

    console.print(table)

    # suggestions (brief)
    suggestions = [r for r in results if r.suggestion]
    if suggestions:
        console.rule("Suggestions")
        for s in suggestions:
            # don't reveal secret suggestions in safe_mode unless explicitly allowed
            if safe_mode and s.secret and not show_secrets:
                console.print(f"- {s.key}: (secret suggestion hidden in safe mode)")
            else:
                console.print(f"- {s.key}: {s.suggestion}")

    # --fix: apply simple fixes (non-destructive by default - controlled with dry_run/backup)
    fixes = []  # Initialize fixes list
    if fix:
        # Build in-memory representation of file lines
        p = Path(env_path)
        if p.exists():
            orig_lines = p.read_text(encoding='utf-8').splitlines()
        else:
            orig_lines = []

        # map existing keys to (line_idx, raw_line)
        key_to_index = {}
        for i, raw in enumerate(orig_lines):
            stripped = raw.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            k, v = raw.split('=', 1)
            key_to_index[k.strip()] = i

        fixes: List[Tuple[str, str, Optional[str], Optional[str], Optional[int]]] = []  # list of (kind, key, old, new, line)

        # 1) append defaults for missing required keys
        defaults = (schema.get('defaults', {}) or {})
        secrets = set((schema.get('secrets', []) or []))
        for r in results:
            if r.expected == 'required' and r.suggestion and r.status in ('warning', 'error'):
                key = r.key
                # only apply default if available and not secret in safe_mode
                default_val = defaults.get(key)
                if default_val is None:
                    continue
                if safe_mode and key in secrets and not show_secrets:
                    # skip applying secret defaults unless user explicitly allows
                    continue
                if key not in key_to_index:
                    fixes.append(('append_default', key, None, default_val, None))

        # 2) normalize booleans to 'true'/'false' for keys declared as bool
        for key, t in (schema.get('types', {}) or {}).items():
            tname = t if isinstance(t, str) else t.get('type')
            if tname != 'bool':
                continue
            if key in key_to_index:
                idx = key_to_index[key]
                raw = orig_lines[idx]
                parts = raw.split('=', 1)
                old_val = parts[1].strip() if len(parts) > 1 else ''
                # use validator parse_bool logic
                b = validator._parse_bool(old_val) if old_val is not None else None
                if b is not None:
                    new_val = 'true' if b else 'false'
                    if old_val.lower() not in ('true', 'false') or old_val != new_val:
                        fixes.append(('normalize_bool', key, old_val, new_val, idx))

        # 3) URL normalization: add https:// if missing scheme and value looks like a host/path
        for key, t in (schema.get('types', {}) or {}).items():
            tname = t if isinstance(t, str) else t.get('type')
            if tname != 'url':
                continue
            if key in key_to_index:
                idx = key_to_index[key]
                raw = orig_lines[idx]
                parts = raw.split('=', 1)
                old_val = parts[1].strip() if len(parts) > 1 else ''
                if old_val and not re.match(r'^https?://', old_val, flags=re.I):
                    # simple heuristic: if contains a dot or a slash, assume it's a URL without scheme
                    if '.' in old_val or '/' in old_val:
                        new_val = 'https://' + old_val.lstrip('/')
                        fixes.append(('normalize_url', key, old_val, new_val, idx))

        # 4) integer coercion/clamping for port-like or int-typed keys
        for key, t in (schema.get('types', {}) or {}).items():
            if isinstance(t, str):
                tname = t
                extras = {}
            else:
                tname = t.get('type')
                extras = t
            if tname != 'int':
                continue
            minv = extras.get('min') if isinstance(extras, dict) else None
            maxv = extras.get('max') if isinstance(extras, dict) else None
            if key in key_to_index:
                idx = key_to_index[key]
                raw = orig_lines[idx]
                parts = raw.split('=', 1)
                old_val = parts[1].strip() if len(parts) > 1 else ''
                # if it's not a plain integer, try to extract digits
                if old_val and not old_val.lstrip('-').isdigit():
                    m = re.search(r"(-?\d+)", old_val)
                    if m:
                        new_val = m.group(1)
                        fixes.append(('coerce_int', key, old_val, new_val, idx))
                        # after coercion we may still need to clamp; compute clamped value
                        try:
                            ival = int(new_val)
                            if minv is not None and ival < minv:
                                fixes.append(('clamp_int', key, new_val, str(minv), idx))
                            if maxv is not None and ival > maxv:
                                fixes.append(('clamp_int', key, new_val, str(maxv), idx))
                        except Exception:
                            pass
                else:
                    # it's digits -> check clamping
                    if old_val.lstrip('-').isdigit():
                        try:
                            ival = int(old_val)
                            if minv is not None and ival < minv:
                                fixes.append(('clamp_int', key, old_val, str(minv), idx))
                            if maxv is not None and ival > maxv:
                                fixes.append(('clamp_int', key, old_val, str(maxv), idx))
                        except Exception:
                            pass

        # Apply or preview fixes
        if not fixes:
            console.print('[green]No automatic fixes available.[/green]')
        else:
            console.rule('Planned fixes')
            for ftype, key, old, new, line in fixes:
                if ftype == 'append_default':
                    console.print(f"- Append default: {key}={new}")
                elif ftype == 'normalize_bool':
                    ln = (line + 1) if line is not None else "?"
                    console.print(f"- Normalize boolean: {key}: '{old}' -> '{new}' at line {ln}")
                elif ftype == 'normalize_url':
                    ln = (line + 1) if line is not None else "?"
                    console.print(f"- Normalize URL: {key}: '{old}' -> '{new}' at line {ln}")
                elif ftype == 'coerce_int':
                    ln = (line + 1) if line is not None else "?"
                    console.print(f"- Coerce integer: {key}: '{old}' -> '{new}' at line {ln}")
                elif ftype == 'clamp_int':
                    ln = (line + 1) if line is not None else "?"
                    console.print(f"- Clamp integer: {key}: '{old}' -> '{new}' at line {ln}")

    # Track telemetry before exit
    runtime_ms = int((time.time() - start_time) * 1000)
    findings_by_type = telemetry.calculate_findings_by_type(results)
    findings_by_severity = telemetry.calculate_findings_by_severity(results)
    auto_fixes_count = len(fixes) if fix else 0
    estimated_time_saved = telemetry.estimate_time_saved(
        findings_total=counts["error"] + counts["warning"],
        auto_fixes_applied=auto_fixes_count
    )

    tracker.track_run_completed(
        command="check",
        files_scanned=1,  # Currently only scanning one file
        findings_total=counts["error"] + counts["warning"],
        findings_by_type=findings_by_type,
        findings_by_severity=findings_by_severity,
        auto_fixes_applied=auto_fixes_count,
        runtime_ms=runtime_ms,
        estimated_time_saved_minutes=estimated_time_saved,
        sample_rate=1.0,
    )

    # Show social engagement message (only for human-readable output)
    if not json_out and not yaml_out:
        console.print()
        console.print("[cyan]❤️  Like env_guard? Tweet or DM me how it helped: @ActiveDadAlex[/cyan]")

    # Exit with appropriate code based on validation results
    raise typer.Exit(code=1 if counts["error"] else (2 if counts["warning"] else 0))


@app.command()
def suggest(
    env_file: str = typer.Option(".env", "--env-file", help="Path to env file"),
    schema_file: str = typer.Option("rules.schema.yaml", "--schema-file", help="Path to schema file"),
    out_file: str = typer.Option(".env.suggested", "--out-file", help="Output file for suggestions"),
    show_secrets: bool = typer.Option(False, help="Show secret values in suggestions"),
    safe_mode: bool = typer.Option(True, help="Safe mode: do not write secrets into suggested files unless explicitly allowed")
) -> None:
    """Suggest fixes for .env file based on schema"""
    # resolve profile (if any)
    env_path = env_file
    profile = None
    if '.' in env_file and not env_file.endswith('.env'):
        p = Path(env_file)
        env_path = str(p.with_name(f"{p.stem}.env{p.suffix}"))
        profile = p.stem.split('.')[-1]

    schema = load_schema(schema_file)
    validator = EnvValidator(env_path, schema, show_secrets=show_secrets, strict=False, profile=profile)
    results = validator.run_all()

    # Display files being used
    console.print(f"[cyan]📄 Environment file:[/cyan] {env_path}")
    console.print(f"[cyan]📋 Schema file:[/cyan] {schema_file}")
    console.print(f"[cyan]💾 Output file:[/cyan] {out_file}")
    if profile:
        console.print(f"[cyan]🏷️  Profile:[/cyan] {profile}")
    console.print()  # blank line for spacing

    # machine output (JSON)
    console.print(validator.to_json(show_secrets=show_secrets and not safe_mode))

    # collect suggestions
    suggestions: Dict[str, str] = {}
    defaults = (schema.get("defaults", {}) or {})
    for r in results:
        if not r.suggestion:
            continue
        k = r.key
        # if it's a secret and safe_mode is on and user didn't allow show_secrets,
        # write an empty placeholder (to avoid leaking) rather than skipping the key entirely
        if safe_mode and r.secret and not show_secrets:
            suggestions[k] = ""
            continue
        # otherwise prefer explicit default value from schema if present
        if k in defaults:
            val = defaults.get(k)
            suggestions[k] = str(val) if val is not None else ""
        else:
            # fallback: no default available — write empty placeholder
            suggestions[k] = ""

    # read existing env file content
    existing_lines = []
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()
    except FileNotFoundError:
        # If the env file is missing, proceed with empty content (we still write a suggestion file)
        existing_lines = []

    # ensure output directory exists
    out_path = Path(out_file)
    if out_path.parent and not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # write a copy with inserted defaults (append at end)
    with open(out_file, "w", encoding="utf-8") as out:
        out.writelines(existing_lines)
        for k, v in suggestions.items():
            if v is None:
                v = ""
            out.write(f"{k}={v}\n")

    console.print(f"Wrote suggested env to {out_file}")
    console.print()
    console.print("[cyan]❤️  Like env_guard? Tweet or DM me how it helped: @ActiveDadAlex[/cyan]")


@app.command()
def init(
    example_file: str = typer.Option("example.env", "--example-file", help="Template file to copy from"),
    out_file: str = typer.Option(".env", "--out-file", help="Output environment file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Prompt for each variable"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing file"),
    keep_comments: bool = typer.Option(True, "--keep-comments/--no-comments", help="Preserve comments"),
    schema_file: Optional[str] = typer.Option(None, "--schema-file", help="Validate after creation"),
) -> None:
    """Initialize .env from example.env template."""
    try:
        # Display files being used
        console.print(f"[cyan]📝 Template file:[/cyan] {example_file}")
        console.print(f"[cyan]💾 Output file:[/cyan] {out_file}")
        if schema_file:
            console.print(f"[cyan]📋 Schema file (for validation):[/cyan] {schema_file}")
        console.print()  # blank line for spacing

        # Initialize the file
        total_vars, needs_values, placeholder_keys = initialize_env(
            example_file=example_file,
            out_file=out_file,
            interactive=interactive,
            overwrite=overwrite,
            keep_comments=keep_comments,
            schema=None  # Schema is only used for post-creation validation
        )

        # Success message
        if needs_values > 0:
            console.print(f"[green]✅ Created {out_file} with {total_vars} variables ({needs_values} still need values)[/green]")
            if not interactive and placeholder_keys:
                console.print("\n[yellow]Variables with placeholder values:[/yellow]")
                for key in placeholder_keys:
                    console.print(f"  - {key}")
        else:
            console.print(f"[green]✅ Created {out_file} with {total_vars} variables[/green]")

        # Optional: Validate against schema
        if schema_file:
            console.print(f"\n[cyan]Validating against {schema_file}...[/cyan]")
            try:
                schema = load_schema(schema_file)
                validator = EnvValidator(out_file, schema, show_secrets=False, strict=False)
                results = validator.run_all()

                # Count errors and warnings
                errors = sum(1 for r in results if r.status == 'error')
                warnings = sum(1 for r in results if r.status == 'warning')

                if errors > 0:
                    console.print(f"[red]❌ Validation found {errors} errors and {warnings} warnings[/red]")
                    console.print("[yellow]Run 'env-guard check' for details[/yellow]")
                elif warnings > 0:
                    console.print(f"[yellow]⚠️  Validation found {warnings} warnings[/yellow]")
                    console.print("[yellow]Run 'env-guard check' for details[/yellow]")
                else:
                    console.print("[green]✅ Validation passed[/green]")

            except FileNotFoundError:
                console.print(f"[yellow]Warning: Schema file {schema_file} not found. Skipping validation.[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning: Validation failed: {e}[/yellow]")

        # Show social engagement message
        console.print()
        console.print("[cyan]❤️  Like env_guard? Tweet or DM me how it helped: @ActiveDadAlex[/cyan]")

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=2)
    except FileExistsError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=2)
    except PermissionError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=2)


# Add runnable module entry point so `python -m env_guard.cli` works
def main(argv: Optional[List[str]] = None) -> int:
    """Programmatic entry point for env-guard. Returns an exit code integer.

    Use via CLI: `env-guard` (installed entry point) or `python -m env_guard.cli`.
    This function will call Typer's app with provided argv (for tests) and return the exit code.
    """
    try:
        # Typer expects to be invoked via app() which will call sys.exit internally if Exit is raised.
        # To capture the exit code cleanly for callers we run app() and catch typer.Exit.
        if argv is None:
            app()
            return 0
        else:
            app(args=argv)
            return 0
    except typer.Exit as e:
        # typer.Exit(code=None) means normal exit with code 0
        code = e.exit_code if e.exit_code is not None else 0
        return int(code)
    except Exception:  # pragma: no cover - unexpected runtime error
        logger.exception("Fatal error in env-guard CLI")
        # 2 indicates usage/runtime errors per specification
        return 2


if __name__ == "__main__":
    sys.exit(main())
