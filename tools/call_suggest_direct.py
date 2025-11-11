# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

from pathlib import Path
from env_guard.cli import suggest

p = Path('tmp_suggest_demo')
p.mkdir(exist_ok=True)
env = p / '.env'
env.write_text('', encoding='utf-8')
schema = p / 'rules.schema.yaml'
schema.write_text('required:\n  - SECRET_KEY\ndefaults:\n  SECRET_KEY: "topsecret"\nsecrets:\n  - SECRET_KEY\n', encoding='utf-8')
out = p / '.env.suggested'

print('Calling suggest directly with', env, schema, out)
# call the function directly
suggest(env_file=str(env), schema_file=str(schema), out_file=str(out), show_secrets=False, safe_mode=True)
print('Done. out exists?', out.exists())
if out.exists():
    print(out.read_text(encoding='utf-8'))

# Placeholder: removed heavy debug helper. Use tests/CliRunner.
