import os


def find_test_config(name):
    directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(directory, 'configs/%s' % name)


def assert_raises(exception):
    def decorator(fn):
        def func(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)

        return func

    return decorator
