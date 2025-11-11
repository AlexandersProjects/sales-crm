# File Display Feature - Summary

## What Was Added

The CLI now displays the files being used at the beginning of each command's output in a nice, human-readable format with icons.

## Commands Updated

### 1. `check` command
Displays before validation results:
- 📄 Environment file
- 📋 Schema file
- 🏷️ Profile (if specified)

### 2. `suggest` command
Displays before suggestions:
- 📄 Environment file
- 📋 Schema file
- 💾 Output file
- 🏷️ Profile (if specified)

### 3. `init` command
Displays before initialization:
- 📝 Template file
- 💾 Output file
- 📋 Schema file (if validation is requested)

## Example Output

When running `env-guard check --env-file .env --schema-file rules.schema.yaml`:

```
📄 Environment file: .env
📋 Schema file: rules.schema.yaml

─────────────── Env Guard Results — 0 errors, 1 warnings, 3 ok ────────────────
┌─────────┬──────────────┬────────┬──────────┬───────────────┬────────────────┐
│ Status  │ Key          │ Value  │ Expected │ Message       │ Location       │
├─────────┼──────────────┼────────┼──────────┼───────────────┼────────────────┤
│ WARNING │ DATABASE_URL │ <none> │ required │ Missing...    │ .env:?         │
│ OK      │ PORT         │ 8080   │ -        │ OK            │ .env:1         │
│ OK      │ DEBUG        │ true   │ -        │ OK            │ .env:2         │
│ OK      │ API_KEY      │ ****   │ -        │ OK            │ .env:3         │
└─────────┴──────────────┴────────┴──────────┴───────────────┴────────────────┘
```

With profile:
```
📄 Environment file: .env.production
📋 Schema file: rules.schema.yaml
🏷️  Profile: production

[rest of output...]
```

## Technical Details

- File information is displayed in **cyan color** for visibility
- Icons (📄, 📋, 💾, 📝, 🏷️) make it easy to scan visually
- Only shown for human-readable output (not for `--json` or `--yaml` flags)
- A blank line separates the file info from the main output for better readability

## Benefits

1. **Clarity**: Users immediately see which files are being processed
2. **Debugging**: Easier to identify configuration issues or wrong file paths
3. **Documentation**: Output is self-documenting for logs and screenshots
4. **User Experience**: Professional, polished feel with minimal clutter

