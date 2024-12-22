"""
luckydep is a dependency injection framework that provide
as less feature as as possible for the purpose of dependency injection.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, cast

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


class Value(Generic[_T]):
    """
    Value of a minimal dependency injection framework.

    *provide* is the construction of Value object, and *invoke* is
    represented by the single public method.

    In practice, the factory function is usually a lambda function,
    so it can invoke other captured dependencies when needed.
    """

    _value: _T | None
    _factory: Callable[[], _T]
    _invoked: bool

    def __init__(self, factory: Callable[[], _T]):
        self._factory = factory
        self._value = None
        self._invoked = False

    def value(self) -> _T:
        if not self._invoked:
            self._value = self._factory()
            self._invoked = True

        return cast(_T, self._value)
