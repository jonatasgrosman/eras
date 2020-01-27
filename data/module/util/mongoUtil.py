from functools import wraps
import module.util.objectUtil as ObjectUtil
from bson.objectid import ObjectId


def mongo_result_wrapper(is_insert=False, is_single_result=False):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if is_insert:

                result = str(f(*args, **kwargs).inserted_id)

            else:

                result = f(*args, **kwargs)

                if not result:
                    return result

                if isinstance(result, dict):
                    return result

                if not isinstance(result, list) and not isinstance(result, dict):
                    result = list(result)

                if len(result) > 0:

                    if is_single_result:
                        result = result[0]

                    def function_to_apply(dictionary, key):
                        dictionary[key] = str(dictionary[key])

                    ObjectUtil.object_function_apply_by_type(result, ObjectId, function_to_apply)

                elif is_single_result:
                    result = None

            return result

        return decorated_function

    return wrapper
