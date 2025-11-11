# JSONB Format Analysis - event_data Field

## Date: 2025-11-09

## Problem Statement

Supabase `telemetry_events` table expects `event_data` to be JSONB type, but events are being rejected with HTTP 400 error (`PostgREST; error=23502` - NOT NULL constraint violation).

## Investigation Results

### What We're Sending ✅

```json
{
  "event_type": "jsonb_test_completed",
  "session_id": "27c9fc1b-c6b7-4bd0-a053-6b76a1cf9b13",
  "user_id": null,
  "timestamp": "2025-11-09T09:05:41.108409+00:00",
  "event_data": {  // ← Sent as DICT/object
    "version": 1,
    "status": "completed",
    "run_id": "24231017-21ec-440c-b728-973d12988e2",
    "command": "jsonb_test",
    ...
  },
  "os_name": "Windows",
  ...
}
```

**env_guard sends `event_data` as a Python dict** - this is correct!

### What's Actually Stored in Supabase

From your successful `connection_test` event:

```json
{
  "event_type": "connection_test",
  "event_data": "{\"test_data\": \"Direct connection test from diagnostics\"}"  // ← STRING!
}
```

**Supabase stores `event_data` as a JSON string**, not as native JSONB.

## Root Cause Analysis

### Issue 1: proof_tracker's JSON Serialization

**proof_tracker** is likely using `json.dumps()` on the entire payload before sending to Supabase. This converts:

```python
# Python dict
{"event_data": {"version": 1, "status": "completed"}}

# After json.dumps()
'{"event_data": "{\\"version\\": 1, \\"status\\": \\"completed\\"}"}'
```

This double-encodes the `event_data` field.

### Issue 2: Supabase JSONB Handling

PostgreSQL JSONB columns can accept:
1. **Native JSON objects** (preferred)
2. **JSON strings** (will be parsed)

But when proof_tracker sends a stringified dict, the Supabase client might be:
- Not parsing it correctly
- Treating it as a plain string instead of JSONB
- Causing a type mismatch

### Issue 3: The Real Problem - NOT NULL Constraint

The error `PostgREST; error=23502` means a NOT NULL constraint is being violated. But which field?

Looking at your schema:
```sql
CREATE TABLE telemetry_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),     -- ✅ Has default
    event_type VARCHAR(100) NOT NULL,                  -- ✅ We send this
    user_id VARCHAR(255),                              -- ✅ Nullable
    session_id UUID NOT NULL,                          -- ✅ We send this
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),      -- ✅ Has default
    os_name VARCHAR(50),                               -- ✅ Nullable
    os_version VARCHAR(50),                            -- ✅ Nullable
    python_version VARCHAR(20),                        -- ✅ Nullable
    proof_tracker_version VARCHAR(20),                 -- ✅ Nullable
    event_data JSONB,                                  -- ✅ Nullable
    created_at TIMESTAMPTZ DEFAULT NOW()               -- ✅ Has default
);
```

**All required fields are satisfied!** So why the NOT NULL violation?

## Hypothesis

The issue might be:

1. **Hidden constraint**: There's a constraint we don't see (trigger, check constraint, or RLS policy)
2. **Type conversion failure**: PostgreSQL rejects the insert because `event_data` string can't be converted to JSONB
3. **proof_tracker bug**: proof_tracker isn't sending the data correctly to Supabase

## Solution Options

### Option 1: Pre-stringify event_data (Quick Fix)

Convert `event_data` to a JSON string before sending:

```python
supabase_event = {
    "event_type": f"{command}_completed",
    "session_id": self.session_id,
    "event_data": json.dumps(event_data),  # ← Convert to string
    ...
}
```

**Pros:** Matches the format that worked before  
**Cons:** Not true JSONB, just a string column

### Option 2: Fix proof_tracker (Proper Fix)

Update proof_tracker to NOT stringify the payload before sending to Supabase. The Supabase Python client should handle JSONB automatically.

**Pros:** Proper JSONB support, better querying  
**Cons:** Requires fixing proof_tracker library

### Option 3: Change Supabase Column Type (Workaround)

Change `event_data` from JSONB to TEXT:

```sql
ALTER TABLE telemetry_events 
ALTER COLUMN event_data TYPE TEXT;
```

**Pros:** Quick database fix  
**Cons:** Loses JSONB querying benefits

## Recommended Action

**Immediate:** Try Option 1 (pre-stringify) to unblock telemetry

**Long-term:** Work with proof_tracker maintainer to fix JSONB handling

## Test Script

Use `test_jsonb_format.py` to verify the format:

```bash
python test_jsonb_format.py
```

Look for the `📦 Complete payload being sent` log to see exactly what's sent.

## Status

⚠️ **Investigation complete, awaiting decision on fix approach**

- ✅ Identified that we send dict (correct)
- ✅ Identified that Supabase stores string (unexpected)
- ✅ Identified proof_tracker as likely culprit
- ⏳ Need to test Option 1 (pre-stringify)

