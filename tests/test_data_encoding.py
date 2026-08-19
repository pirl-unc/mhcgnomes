import os
import subprocess
import sys


def test_package_import_succeeds_under_ascii_locale():
    env = os.environ.copy()
    env.update(
        {
            "LANG": "C",
            "LC_ALL": "C",
            "PYTHONCOERCECLOCALE": "0",
            "PYTHONUTF8": "0",
        }
    )

    result = subprocess.run(
        [sys.executable, "-c", "import mhcgnomes"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr
