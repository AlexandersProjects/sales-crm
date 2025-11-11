# Copyright 2025 Alexander Blaschko-Schänzer
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


import sys
import subprocess
# print which env_guard.cli file would be imported by the current interpreter
cmd = [sys.executable, '-c', 'import env_guard.cli as m; print(m.__file__); import inspect; print(inspect.getsource(m)[:400])']
print('Running:', cmd)
proc = subprocess.run(cmd, capture_output=True, text=True)
print('returncode:', proc.returncode)
print('stdout:\n', proc.stdout)
print('stderr:\n', proc.stderr)
