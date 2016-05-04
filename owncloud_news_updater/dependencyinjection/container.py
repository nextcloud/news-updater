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

    def set(self, key, factory):
        if key in self._factories:
            msg = 'Factory already registered for key %s' % key
            raise AlreadyRegisteredException(msg)
        else:
            self._factories[key] = factory

    def get(self, key):
        if key not in self._singletons:
            if key in self._factories:
                self._singletons[key] = self._factories[key](self)
            else:
                msg = 'Unable to resolve factory for key %s' % key
                raise ResolveException(msg)
        return self._singletons[key]
