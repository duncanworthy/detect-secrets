from typing import Any
from typing import NamedTuple
from typing import NoReturn
from typing import Optional
from typing import Set


class SelfAwareCallable:
    """
    This distinguishes itself from a normal callable, since it knows things about itself.
    """
    # The import path of the function
    path: str

    # The variable names for its inputs
    injectable_variables: Set[str]

    def __call__(self, *args: Any, **kwargs: Any) -> NoReturn:
        """
        This is needed, since you can't inherit Callable.
        Source: https://stackoverflow.com/a/52654516/13340678
        """
        pass


class SecretContext(NamedTuple):
    # Keeps track of the current secret in the process
    current_index: int
    num_total_secrets: int

    secret: 'PotentialSecret'       # noqa: F821
    header: Optional[str] = None

    # Either secret context is provided...
    snippet: Optional['CodeSnippet'] = None

    # ...or error information. But it has an XOR relationship.
    error: Optional['SecretNotFoundOnSpecifiedLineError'] = None
