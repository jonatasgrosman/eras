from functools import wraps


def exception_wrapper(exception_to_raise):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise exception_to_raise(e)
        return decorated_function
    return wrapper