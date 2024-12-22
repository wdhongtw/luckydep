import unittest
from collections.abc import Callable

import luckydep


class TestContainer(unittest.TestCase):
    def test_composition(self) -> None:

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

        container = luckydep.Container()
        container.provide(
            str,
            lambda c: "Hi",
            name="hello-prefix",
        )
        container.provide(
            Store,
            lambda c: FaKeStore({7: "Alice"}),
        )
        container.provide(
            Service,
            lambda c: Service(
                store=c.invoke(Store),
                prefix=c.invoke(str, name="hello-prefix"),
            ),
        )
        service = container.invoke(Service)

        self.assertEqual("Hi, Alice", service.greeting(7))

    def test_default_name(self) -> None:
        c = luckydep.Container()
        c.provide(str, lambda c: "some-id")

        c.invoke(str, name="default")
        with self.assertRaises(Exception):
            c.invoke(str, name="other-name")

    def test_singleton(self) -> None:
        some_item = object()

        c = luckydep.Container()
        c.provide(object, lambda c: some_item)

        self.assertIs(c.invoke(object), c.invoke(object))

    def test_named_object(self) -> None:

        class Obj: ...

        c = luckydep.Container()
        c.provide(Obj, lambda c: Obj(), name="first")
        c.provide(Obj, lambda c: Obj(), name="second")

        self.assertIsNot(c.invoke(Obj, name="first"), c.invoke(Obj, name="second"))

    def test_wrap_utility(self) -> None:

        class Obj: ...

        c = luckydep.Container()
        c.provide(Obj, luckydep.wrap(lambda: Obj()))

        self.assertIsInstance(c.invoke(Obj), Obj)

    def test_function_object(self) -> None:

        class BinOp:
            def __call__(self, a: int, b: int) -> int:
                raise NotImplementedError()

        class Add(BinOp):
            def __call__(self, a: int, b: int) -> int:
                return a + b

        c = luckydep.Container()
        c.provide(BinOp, lambda c: Add(), name="add-func")

        operator = c.invoke(BinOp, name="add-func")
        self.assertEqual(5, operator(2, 3))


class TestValue(unittest.TestCase):

    def test_construction(self) -> None:

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

        value_service = luckydep.Value[Service](
            lambda: Service(
                value_store.value(),
                "Hi",
            )
        )
        value_store = luckydep.Value[Store](
            lambda: FaKeStore(
                {3: "Bob"},
            )
        )

        service = value_service.value()
        sentence = service.greeting(3)

        self.assertEqual("Hi, Bob", sentence)

    def test_function_value(self) -> None:

        add: Callable[[int, int], int] = lambda a, b: a + b

        value_op = luckydep.Value[Callable[[int, int], int]](lambda: add)
        op = value_op.value()

        self.assertEqual(5, op(2, 3))
