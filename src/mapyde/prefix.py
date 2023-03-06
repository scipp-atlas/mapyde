"""
Copyright (c) 2022 Michael Hance and Giordon Stark. All rights reserved.
"""


from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mapyde.typing import PathOrStr, Self


class Prefix(sys.modules[__name__].__class__):  # type: ignore[misc]
    """
    A module-level wrapper around :mod:`mapyde` which will provide the prefixes

    .. rubric:: Example (callable)

    .. code-block:: pycon

        >>> import mapyde.prefix
        >>> import pathlib
        >>> curr_path = mapyde.prefix.data
        >>> curr_path  # doctest: +ELLIPSIS
        PosixPath('.../pyhf/schemas')
        >>> new_path = pathlib.Path("/home/root/my/new/path")
        >>> mapyde.prefix(new_path)  # doctest: +ELLIPSIS
        <module 'mapyde.prefix' from ...>
        >>> mapyde.prefix.data
        PosixPath('/home/root/my/new/path')
        >>> mapyde.prefix(curr_path)  # doctest: +ELLIPSIS
        <module 'mapyde.prefix' from ...>
        >>> mapyde.prefix.data  # doctest: +ELLIPSIS
        PosixPath('.../pyhf/schemas')

    .. rubric:: Example (context-manager)

    .. code-block:: pycon

        >>> import mapyde.prefix
        >>> import pathlib
        >>> curr_path = mapyde.prefix.data
        >>> curr_path  # doctest: +ELLIPSIS
        PosixPath('.../pyhf/schemas')
        >>> new_path = pathlib.Path("/home/root/my/new/path")
        >>> with mapyde.prefix(new_path):
        ...     print(repr(mapyde.prefix.data))
        ...
        PosixPath('/home/root/my/new/path')
        >>> mapyde.prefix.data  # doctest: +ELLIPSIS
        PosixPath('.../pyhf/schemas')

    """

    suffix_cards: str = "cards"
    suffix_likelihoods: str = "likelihoods"
    suffix_scripts: str = "scripts"
    suffix_templates: str = "templates"
    _data: Path = Path()
    _cards_path: Path | None = None
    _likelihoods_path: Path | None = None
    _scripts_path: Path | None = None
    _templates_path: Path | None = None
    _orig_path: Path = Path()

    __all__ = [
        "data",
        "cards",
        "likelihoods",
        "scripts",
        "templates",
        "suffix_cards",
        "suffix_likelihoods",
        "suffix_scripts",
        "suffix_templates",
    ]

    def __call__(self, new_path: PathOrStr) -> Self:
        """
        Change the local search path for finding data locally.

        Args:
            new_path (pathlib.Path): Path to folder containing the data

        Returns:
            self (mapyde.prefix.Prefix): Returns itself (for contextlib management)
        """
        self._orig_path, self.data = self.data, Path(new_path)
        return self

    def __enter__(self) -> None:
        pass

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """
        Reset the local data path for cards locally.

        Returns:
            None
        """
        self.data = self._orig_path

    def __dir__(self) -> list[str]:
        return self.__all__

    @property
    def data(self) -> Path:
        """
        The local path for data.
        """
        return self._data

    @data.setter
    def data(self, new_path: PathOrStr) -> None:
        self._data = Path(new_path)

    @property
    def cards(self) -> Path:
        """
        The local path for cards.
        """
        return self._cards_path or self.data / self.suffix_cards

    @cards.setter
    def cards(self, new_path: PathOrStr) -> None:
        """
        Set the local path for cards.
        """
        self._cards_path = Path(new_path)

    @property
    def likelihoods(self) -> Path:
        """
        The local path for likelihoods.
        """
        return self._likelihoods_path or self.data / self.suffix_likelihoods

    @likelihoods.setter
    def likelihoods(self, new_path: PathOrStr) -> None:
        """
        Set the local path for likelihoods.
        """
        self._likelihoods_path = Path(new_path)

    @property
    def scripts(self) -> Path:
        """
        The local path for scripts.
        """
        return self._scripts_path or self.data / self.suffix_scripts

    @scripts.setter
    def scripts(self, new_path: PathOrStr) -> None:
        """
        Set the local path for scripts.
        """
        self._scripts_path = Path(new_path)

    @property
    def templates(self) -> Path:
        """
        The local path for templates.
        """
        return self._templates_path or self.data / self.suffix_templates

    @templates.setter
    def templates(self, new_path: PathOrStr) -> None:
        """
        Set the local path for templates.
        """
        self._templates_path = Path(new_path)


sys.modules[__name__].__class__ = Prefix
