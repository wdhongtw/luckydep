"""
luckydep is a dependency injection framework that provide
as less feature as as possible for the purpose of dependency injection.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

_T = TypeVar("_T", bound=object)


class Container:
    """
    Container of a minimal dependency injection framework.

    Type must be specified manually, and no annotation-based wiring support.
    """

    def __init__(self) -> None:
        """
        Construct a container.
        """
        self._factories: dict[Any, Any] = {}
        self._instances: dict[Any, Any] = {}

    def provide(
        self,
        cls: type[_T],
        factory: Callable[[Container], _T],
        *,
        name: str = "default",
    ) -> None:
        """
        Provide a factory function for "cls" of "name".

        factory can use the container instance to invoke required dependencies.
        """
        self._factories[cls, name] = factory

    def invoke(
        self,
        cls: type[_T],
        *,
        name: str = "default",
    ) -> _T:
        """
        Return a singleton "cls" object by "name".

        Invoke the factory function if necessary.
        """
        identifier = (cls, name)
        if identifier in self._instances:
            return self._instances[identifier]

        self._instances[identifier] = self._factories[cls, name](self)
        return self._instances[identifier]


def wrap(factory: Callable[[], _T]) -> Callable[[Container], _T]:
    """
    wrap the factory function which don't need container to registration
    """

    def wrapped(container: Container) -> _T:
        return factory()

    return wrapped
