import json
import os
import subprocess
import sys


def test_cli_parses_bundled_data_under_ascii_locale():
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
        [
            sys.executable,
            "-m",
            "mhcgnomes",
            "--format",
            "json",
            "HLA-A*02:01",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == 1
    assert rows[0]["input"] == "HLA-A*02:01"
    assert rows[0]["type"] == "Allele"
    assert rows[0]["normalized"] == "HLA-A*02:01"
    assert rows[0]["compact"] == "A0201"
    assert rows[0]["species"] == "HLA"
    assert rows[0]["gene"] == "A"
    assert rows[0]["mhc_class"] == "Ia"
    assert "species_name=Homo sapiens" in rows[0]["properties"]
