import json
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List

from . import io
from ..core import baseline
from ..core import plugins
from ..core.exceptions import InvalidBaselineError
from ..core.potential_secret import PotentialSecret
from .exceptions import SecretNotFoundOnSpecifiedLineError


def get_baseline_from_file(filename: str) -> Dict[str, Any]:
    """
    :raises: InvalidBaselineError
    """
    try:
        # TODO: how to quit early if no line numbers provided?
        # TODO: What to do about `custom_plugin_paths`?
        # TODO: Should we upgrade this?
        return baseline.load(baseline.load_from_file(filename), filename)
    except (IOError, json.decoder.JSONDecodeError):
        io.print_error('Not a valid baseline file!')
        raise InvalidBaselineError
    except KeyError:
        io.print_error('Not a valid baseline file!')
        raise InvalidBaselineError


def get_raw_secret_from_file(secret: PotentialSecret) -> str:
    """
    We're analyzing the contents straight from the baseline, and therefore, we don't know
    the secret value (by design). However, we have line numbers, filenames, and how we detected
    it was a secret in the first place, so we can reverse-engineer it.

    :raises: SecretNotFoundOnSpecifiedLineError
    """
    plugin = plugins.initialize.from_secret_type(secret.type)
    try:
        target_line = open_file(secret.filename)[secret.line_number - 1]
    except IndexError:
        raise SecretNotFoundOnSpecifiedLineError(secret.line_number)

    identified_secrets = plugin.analyze_line(
        filename=secret.filename,
        line=target_line,
        line_number=secret.line_number,     # TODO: this will be optional
    )

    for identified_secret in identified_secrets:
        if identified_secret == secret:
            return identified_secret.secret_value

    raise SecretNotFoundOnSpecifiedLineError(secret.line_number)


@lru_cache(maxsize=1)
def open_file(filename: str) -> List[str]:
    """
    Caches the open input file. This ensures that the audit functionality doesn't
    unnecessarily re-open the same file.

    :raises: FileNotFoundError
    """
    with open(filename) as f:
        return [line.rstrip() for line in f.readlines()]
