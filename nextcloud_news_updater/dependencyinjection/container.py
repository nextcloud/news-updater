from typing import Callable, Any
from typing import Dict


class ResolveException(Exception):
    pass


class Factory:
    """
    Wrapper for non shared factories
    """

    def __init__(self, factory: Callable[['Container'], Any]) -> None:
        self.factory = factory

    def __call__(self, container: 'Container') -> Any:
        return self.factory(container)


class SingletonFactory(Factory):
    """
    Wrapper for shared factories
    """

    def __init__(self, factory: Callable[['Container'], Any]) -> None:
        super().__init__(factory)


class Container:
    """
    Simple container for Dependency Injection
    """

    def __init__(self) -> None:
        self._singletons = {}  # type: Dict[Any, Any]
        self._factories = {}  # type: Dict[Any, Factory]

    def register(self, key: Any, factory: Callable[['Container'], Any],
                 shared: bool = True) -> None:
        """
        Registers a factory function for creating the class
        :argument key name under which the dependencies will be
        registered
        :argument factory a function that receives the constructor as first
        argument and is used to create the class
        :argument shared if True, the factory result will be saved for reuse.
        This means that the same instance will be returned once the same key
        is requested again. If False requesting the same key will always return
        a new instance. Autoresolved classes will always be shared
        """
        if shared:
            self._factories[key] = SingletonFactory(factory)
        else:
            self._factories[key] = Factory(factory)

    def resolve(self, key: Any) -> Any:
        """
        Fetches an instance or creates one using the registered factory method
        :argument key the key to look up
        :return the created or looked up instance
        """
        if key not in self._singletons:
            # if registered, determine if the result will be shared
            if key in self._factories:
                factory = self._factories[key]
                result = factory(self)
                if isinstance(factory, SingletonFactory):
                    self._singletons[key] = result
                return result
            # if not registered, try to automatically resolve it based on
            # its annotations. Automatically resolved keys are always shared
            elif isinstance(type(key), type):
                result = self._resolve_class(key)
                self._singletons[key] = result
                return result
            else:
                msg = 'Unable to resolve factory for key %s' % key
                raise ResolveException(msg)
        else:
            return self._singletons[key]

    def alias(self, source: type, target: Any) -> Any:
        """
        Point a key to another key
        :argument source the key to resolve when the target is requested
        :argument target the name of the alias
        """
        self.register(target, lambda c: c.resolve(source))

    def _resolve_class(self, clazz: Any) -> object:
        """
        Constructs an instance based on the function annotations on an object's
        __init__ method
        :argument clazz the class to instantiate
        :return the instantiated class
        """
        arguments = {}
        if hasattr(clazz.__init__, '__annotations__'):
            annotations = clazz.__init__.__annotations__
            for name, type_hint in annotations.items():
                if name != 'return':
                    arguments[name] = self.resolve(type_hint)
        return clazz(**arguments)
