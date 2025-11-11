# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

from pathlib import Path
import traceback
from env_guard import cli

# prepare temp dir
p = Path('tmp_check_debug')
p.mkdir(exist_ok=True)
env = p / '.env'
env.write_text('DEBUG=true\n', encoding='utf-8')
schema = p / 'rules.schema.yaml'
schema.write_text('required:\n  - DATABASE_URL\n', encoding='utf-8')

print('Calling check with env:', env, 'schema:', schema)
try:
    cli.check(env_file=str(env), schema_file=str(schema), json_out=True)
except Exception as e:
    print('Exception type:', type(e))
    traceback.print_exc()

# Now write default and call again
schema.write_text('required:\n  - DATABASE_URL\ndefaults:\n  DATABASE_URL: "sqlite:///:memory:"\n', encoding='utf-8')
print('\nCalling check after adding defaults (expect warning exit)')
try:
    cli.check(env_file=str(env), schema_file=str(schema), json_out=True)
except Exception as e:
    print('Exception type:', type(e))
    traceback.print_exc()

# Debug helper removed — placeholder kept for reference.
# Use `pytest` and the CLI test runner (typer.testing.CliRunner) for automated tests.
