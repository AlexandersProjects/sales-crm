# 📊 Telemetry Quick Start Guide

## TL;DR

```bash
# Telemetry is OFF by default (privacy-first)
env-guard check  # ← No telemetry

# Want to help improve env-guard? Enable telemetry:
export ENV_GUARD_TELEMETRY=true
env-guard check  # ← Data collected (anonymous, local-first)

# Disable anytime:
unset ENV_GUARD_TELEMETRY
```

---

## What is Telemetry?

Telemetry helps us understand how env-guard is used so we can:
- Fix bugs faster
- Prioritize popular features
- Improve performance
- Track error rates

**Your privacy matters:** Telemetry is **opt-out by default** and **completely anonymous**.

---

## Quick Start

### ✅ Enable Telemetry (Opt-In)

```bash
# Option 1: Environment variable (recommended)
export ENV_GUARD_TELEMETRY=true

# Option 2: In your .env file
echo "ENV_GUARD_TELEMETRY=true" >> .env

# Option 3: One-time for single command
ENV_GUARD_TELEMETRY=true env-guard check
```

### ❌ Disable Telemetry (Default)

```bash
# Already disabled by default, but to be explicit:
export ENV_GUARD_TELEMETRY=false

# Or unset it:
unset ENV_GUARD_TELEMETRY
```

---

## What Data is Collected?

### ✅ Collected (Anonymous)
- Command names (check, suggest, init)
- Finding counts and types  
- Runtime metrics
- Success/failure rates
- Error types (not error messages with your data)

### ❌ NOT Collected
- ❌ File paths or names
- ❌ Variable names
- ❌ Variable values
- ❌ User names or emails
- ❌ IP addresses
- ❌ Any personally identifiable information

---

## Where is Data Stored?

### Local (Always)
When telemetry is enabled, data is saved locally at:

```
~/.env_guard_telemetry/
├── env_guard_tracking.json  # Event log
├── stats.json                # Statistics
└── session_id.txt            # Session ID
```

You can view this data anytime:
```bash
cat ~/.env_guard_telemetry/stats.json
```

### Cloud (Optional)
If you configure Supabase credentials, data is **also** sent to the cloud:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Note:** You don't need Supabase credentials. Local telemetry works without it!

---

## Check Telemetry Status

```bash
# Is telemetry enabled?
python -c "
import os
enabled = os.getenv('ENV_GUARD_TELEMETRY', 'false').lower() in ('1', 'true', 'yes', 'on', 'enabled')
print('✅ Enabled' if enabled else '❌ Disabled (default)')
"
```

---

## View Your Data

```bash
# View statistics
cat ~/.env_guard_telemetry/stats.json

# View event log
cat ~/.env_guard_telemetry/env_guard_tracking.json

# Pretty print with jq (if installed)
cat ~/.env_guard_telemetry/stats.json | jq
```

Example output:
```json
{
  "total_runs": 15,
  "total_findings": 42,
  "auto_fixes_applied": 8,
  "reliability": {
    "success_rate_percent": 93.33
  },
  "performance": {
    "average_runtime_ms": 127.5
  }
}
```

---

## Privacy & Control

### You Are In Control
- ✅ **Opt-out by default** - No data collected unless you enable it
- ✅ **Local-first** - Data always saved locally, you own it
- ✅ **Optional cloud** - Supabase is optional
- ✅ **Anonymous** - No personal information ever collected
- ✅ **Transparent** - Open source, you can read the code
- ✅ **Disable anytime** - Just unset ENV_GUARD_TELEMETRY

### How to Delete Your Data

```bash
# Delete all local telemetry data
rm -rf ~/.env_guard_telemetry/

# Telemetry will start fresh next time you enable it
```

---

## FAQ

### Q: Is telemetry required?
**A:** No! Telemetry is **disabled by default**. env-guard works perfectly without it.

### Q: What if I don't trust telemetry?
**A:** Don't enable it! The tool works 100% without telemetry.

### Q: Can I see what data is sent?
**A:** Yes! Check `~/.env_guard_telemetry/env_guard_tracking.json` to see every event.

### Q: Does telemetry slow down env-guard?
**A:** No. Telemetry is asynchronous and adds <10ms overhead.

### Q: Can I use telemetry without Supabase?
**A:** Yes! Local telemetry works without any cloud service.

### Q: How do I contribute telemetry to help improve env-guard?
**A:** Just set `ENV_GUARD_TELEMETRY=true`. That's it!

### Q: Will you sell my data?
**A:** Never. We don't collect any personal data. Everything is anonymous.

---

## Examples

### Development Workflow

```bash
# In your .env file for project
ENV_GUARD_TELEMETRY=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key

# Use env-guard normally
env-guard check
env-guard suggest
env-guard init

# View your stats
cat ~/.env_guard_telemetry/stats.json
```

### CI/CD Pipeline

```bash
# Disable telemetry in CI (default behavior)
env-guard check --no-telemetry

# Or explicit:
ENV_GUARD_TELEMETRY=false env-guard check
```

### One-Time Analysis

```bash
# Enable for single command
ENV_GUARD_TELEMETRY=true env-guard check

# Back to disabled for next command
env-guard check  # ← No telemetry
```

---

## Support

### Issues or Questions?
- GitHub Issues: https://github.com/yourusername/env_guard/issues
- Documentation: https://github.com/yourusername/env_guard/docs

### Want to Help?
- Enable telemetry: `ENV_GUARD_TELEMETRY=true`
- Report bugs: GitHub Issues
- Contribute code: Pull Requests
- Share feedback: GitHub Discussions

---

## Summary

```
┌─────────────────────────────────────────────┐
│  🔒 Privacy-First                           │
│  ✅ Opt-out by default                      │
│  ✅ Anonymous data only                     │
│  ✅ Local-first storage                     │
│  ✅ Optional cloud                          │
│  ✅ Easy to enable/disable                  │
│  ✅ Transparent and documented              │
└─────────────────────────────────────────────┘

Enable: export ENV_GUARD_TELEMETRY=true
Disable: unset ENV_GUARD_TELEMETRY
View data: cat ~/.env_guard_telemetry/stats.json
```

**Thank you for considering telemetry to help improve env-guard!** 🙏

---

**Last Updated:** 2025-11-09  
**env_guard Version:** 0.2.0

