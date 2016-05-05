class ResolveException(Exception):
    pass


class AlreadyRegisteredException(Exception):
    pass


class BaseContainer:
    """
    Simple container for Dependency Injection
    """

    def __init__(self):
        self._singletons = {}
        self._factories = {}

    def register(self, key, factory):
        """
        Registers a factory function for creating the class
        :argument key name under which the dependencies will be
        registered
        :argument factory a function that receives the constructor as first
        argument and is used to create the class
        """
        if key in self._factories:
            msg = 'Factory already registered for key %s' % key
            raise AlreadyRegisteredException(msg)
        else:
            self._factories[key] = factory

    def resolve(self, key):
        """
        Fetches an instance or creates one using the registered factory method
        :argument key the key to look up
        :return the created or looked up instance
        """
        if key not in self._singletons:
            if key in self._factories:
                self._singletons[key] = self._factories[key](self)
            elif isinstance(type(key), type):
                self._singletons[key] = self._create_class(key)
            else:
                msg = 'Unable to resolve factory for key %s' % key
                raise ResolveException(msg)
        return self._singletons[key]

    def _create_class(self, clazz):
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
