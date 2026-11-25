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

"""Readable argparse help and table styling with optional terminal color."""

import argparse
import os
import re
import shutil
import sys

OPTION_PATTERN = re.compile(r"(?<![\w-])(--[a-zA-Z][\w-]*|-[a-zA-Z])\b")


def color_enabled(stream):
    """Return whether ``stream`` supports optional terminal styling."""
    return bool(
        getattr(stream, "isatty", lambda: False)()
        and not os.environ.get("NO_COLOR")
        and os.environ.get("TERM") != "dumb"
    )


def style_help(text, stream):
    """Style headings, flags, and ``usage:`` only on color-capable terminals."""
    if not color_enabled(stream):
        return text

    lines = []
    for line in text.splitlines(keepends=True):
        if line.rstrip().endswith(":") and not line[0].isspace():
            lines.append("\033[1;36m" + line.rstrip("\n") + "\033[0m\n")
        else:
            line = OPTION_PATTERN.sub(lambda match: "\033[36m" + match[0] + "\033[0m", line)
            if line.startswith("usage:"):
                line = line.replace("usage:", "\033[1musage:\033[0m", 1)
            lines.append(line)
    return "".join(lines)


def style_table_header(text, stream):
    """Style the first line of an aligned table in bold cyan on color terminals."""
    if not text or not color_enabled(stream):
        return text
    lines = text.splitlines(keepends=True)
    trailing_newline = "\n" if lines[0].endswith("\n") else ""
    lines[0] = "\033[1;36m" + lines[0].rstrip("\n") + "\033[0m" + trailing_newline
    return "".join(lines)


def style_status(text, stream, *, dim=False, warning=False):
    """Optionally style a status value as dim (absent) or yellow (warning) on TTYs."""
    if not text or not color_enabled(stream):
        return text
    if warning:
        return f"\033[33m{text}\033[0m"
    if dim:
        return f"\033[2m{text}\033[0m"
    return text


class HelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Limit reading width and separate options without adding table borders."""

    def __init__(self, prog):
        width = max(40, min(100, shutil.get_terminal_size().columns - 2))
        super().__init__(prog, max_help_position=32, width=width)

    def _split_lines(self, text, width):
        """Strip RST backticks before wrapping option help text."""
        return super()._split_lines(text.replace("``", ""), width)

    def _format_action(self, action):
        """Add a blank line after each formatted CLI option block."""
        text = super()._format_action(action)
        return text + "\n" if text else text


class HelpArgumentParser(argparse.ArgumentParser):
    """Keep format_help() plain; add subtle cyan styling only when printing to a TTY."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("formatter_class", HelpFormatter)
        if sys.version_info >= (3, 14):
            # Apply the same styling on all supported Python versions.
            kwargs["color"] = False
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        stream = sys.stdout if file is None else file
        self._print_message(style_help(self.format_help(), stream), stream)
