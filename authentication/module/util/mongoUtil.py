import module.util.objectUtil as ObjectUtil
from functools import wraps


def mongo_result_wrapper(is_insert=False, is_single_result=False, apply_str_function_to_id=True, id_key='_id',
                         replace_id_key=True, id_key_replacement='id'):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if is_insert:

                result = str(f(*args, **kwargs).inserted_id)

            else:

                result = f(*args, **kwargs)

                if not isinstance(result, list) and not isinstance(result, dict):
                    result = list(result)

                if len(result) > 0:

                    if is_single_result:
                        result = result[0]

                    def function_to_apply(dictionary, key):
                        if apply_str_function_to_id:
                            dictionary[key] = str(dictionary[key])
                        if replace_id_key:
                            dictionary[id_key_replacement] = dictionary.pop(key)

                    ObjectUtil.object_function_apply_by_key(result, id_key, function_to_apply)

                elif is_single_result:
                    result = None

            return result

        return decorated_function

    return wrapper
