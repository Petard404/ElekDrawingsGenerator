"""Exception type carrying an error code, optional element ID and parameters."""

from __future__ import annotations


class HuiselekError(Exception):
    """A user-facing error. ``str()`` gives the Dutch message from labels.py."""

    def __init__(self, code: str, element_id: str | None = None, **params):
        super().__init__(code, element_id, params)
        self.code = code
        self.element_id = element_id
        self.params = params

    def __str__(self) -> str:
        from .labels import error_message  # lazy: labels sits below errors in the table

        return error_message(self.code, self.element_id, self.params)
