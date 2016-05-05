class ResolveException(Exception):
    pass


class AlreadyRegisteredException(Exception):
    pass


class Factory:
    """
    Wrapper for non shared factories
    """

    def __init__(self, factory):
        self.factory = factory

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


class SingletonFactory(Factory):
    """
    Wrapper for shared factories
    """

    def __init__(self, factory):
        super().__init__(factory)


class BaseContainer:
    """
    Simple container for Dependency Injection
    """

    def __init__(self):
        self._singletons = {}
        self._factories = {}

    def register(self, key, factory, shared=True):
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
        if key in self._factories:
            msg = 'Factory already registered for key %s' % key
            raise AlreadyRegisteredException(msg)
        else:
            if shared:
                self._factories[key] = SingletonFactory(factory)
            else:
                self._factories[key] = Factory(factory)

    def resolve(self, key):
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

    def alias(self, source, target):
        """
        Point a key to another key
        :argument source the key to resolve when the target is requested
        :argument target the name of the alias
        """
        self.register(target, lambda: self.resolve(source))

    def _resolve_class(self, clazz):
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
                arguments[name] = self.resolve(type_hint)
        return clazz(**arguments)
