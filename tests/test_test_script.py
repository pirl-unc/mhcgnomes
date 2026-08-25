# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
from pathlib import Path


def test_test_sh_uses_python_module_for_pytest(tmp_path):
    marker = tmp_path / "python-pytest-called"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    fake_python = fake_bin / "python"
    fake_python.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then exit 1; fi\n'
        'if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then\n'
        '  touch "$MHCGENOMES_TEST_MARKER"\n'
        "  exit 0\n"
        "fi\n"
        "exit 2\n"
    )
    fake_python.chmod(0o755)

    fake_pytest = fake_bin / "pytest"
    fake_pytest.write_text("#!/bin/sh\nexit 97\n")
    fake_pytest.chmod(0o755)

    repo_dir = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join((str(fake_bin), env["PATH"]))
    env["MHCGENOMES_TEST_MARKER"] = str(marker)
    result = subprocess.run(
        ["bash", "test.sh", "--collect-only"],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert marker.exists()
