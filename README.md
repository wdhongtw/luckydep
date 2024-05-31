# luckydep: A minimal dependency injection framework

`luckydep` is a minimal dependency framework, only one class with two method.

Full type-hint on public interface, provide type safety for library user.

## Motivation

Most popular DI frameworks in Python ecosystem have some design choices:

- Use decorator on injected function/class for object wiring.
- Declare container by inheriting some base-container class,
  and the order of object creation become explicit.

Highly integrate with user code, core use-cases will depend on the framework

While these design choices make it easier to test code, and reduce main
lines of code in main module/program, these do have some drawback.

- Core library now depends on particular framework, add unwanted noises.
- Declaring order of objects become important, which reduce the benefits of DI.

So comes this library. Inspired by golang library
[github.com/samber/do](https://do.samber.dev/docs/getting-started),
this library require user to do a little more stuff in main program,
for limiting the dependency of DI framework into one place.

## Usage

Assuming we have a `Service`, providing use-case `greeting`,
which need user to inject a `Store` instance and a `prefix` config.

```python
class Store:
    def get_name(self, user_id: int) -> str:
        raise NotImplementedError()

class FaKeStore(Store):
    def __init__(self, records: dict[int, str]):
        self._records = records

    def get_name(self, user_id: int) -> str:
        return self._records[user_id]

class Service:
    def __init__(self, store: Store, prefix: str):
        self._store = store
        self._prefix = prefix

    def greeting(self, user_id: int) -> str:
        name = self._store.get_name(user_id)
        return f"{self._prefix}, {name}"
```

With the help of `luckydep.Container`, we can register factory function
and later invoke the required instance.

```python
import luckydep

container = luckydep.Container()
container.provide(
    Service,
    lambda c: Service(
        store=c.invoke(Store),
        prefix=c.invoke(str, name="hello-prefix"),
    ),
)
container.provide(
    Store,
    lambda c: FaKeStore({7: "Alice"}),
)
container.provide(
    str,
    lambda c: "Hi",
    name="hello-prefix",
)

service = container.invoke(Service)
assert service.greeting(7) == "Hi, Alice"
```

Notice that the registration order of `Service`, `Store`
(and the `str` "hello-prefix") is not important here.

Since that all factory function is evaluate lazily, the factory function can
alway use `c.invoke` to ask another object, for which the factory function are
not registered already.

For custom types, we usually create only one instance, so we don't give a
explicit `name`, the name of the provided factory is `"default"` by default.

```python
class Obj: ...

container = luckydep.Container()

# both usage are equivalent
container.provide(Obj, lambda c: Obj())
container.provide(Obj, lambda c: Obj(), name="default")
```

## Limitation

No dependency cycle detection, this library just explode the stack and crash
immediately at runtime if there exists a dependency cycle.

Unlike some other framework, No config-file/environment-variable provider,
with the *provide` interface, it's easy to integrate with other library with a
simple lambda object.

```python
import os
import luckydep

os.environ["API_TOKEN"] = "some-token"

c = luckydep.Container()
# can use any config-file/environ/argument library you like here
c.provide(str, lambda c: os.environ.get("API_TOKEN", ""), name="api-token")

api_token = c.invoke(str, name="api-token")
assert api_token == "some-token"
```

Only return a singleton by invoke interface, since personally I think that's
the most important usage of dependency injection. To create a new instance
every time, we can register "factory function of some factory function".
Although the faction function need to be represent by some class,
see next limitation.

Can not provide a type which are not exists at runtime. For example,
`mypy` will complain when we want to provide a `Callable[[int, int], int]`
function to the container. Although this still work well in runtime since these
subscripted generic type instance is *comparable* and *hashable*.
Likewise, interface defined by `typing.Protocol` won't pass `mypy` check either.

As a result, structural typing is not possible by this library.
User need to establish a explicit type inheritance.

```python
import luckydep

class BinOp:
    def __call__(self, a: int, b: int) -> int:
        raise NotImplementedError()

class Add(BinOp):
    def __call__(self, a: int, b: int) -> int:
        return a + b

c = luckydep.Container()
c.provide(BinOp, lambda c: Add(), name="add-func")

operator = c.invoke(BinOp, name="add-func")
assert operator(2, 3) == 5
```

## Related Work

- [ets-labs/python-dependency-injector: Dependency injection framework for Python](https://github.com/ets-labs/python-dependency-injector)
- [dry-python/returns: Make your functions return something meaningful, typed, and safe!](https://github.com/dry-python/returns)
- [modern-python/that-depends: DI-framework, inspired by python-dependency-injector, but without wiring. Python 3.12 is supported](https://github.com/modern-python/that-depends)
