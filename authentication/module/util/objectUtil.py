def object_function_apply_by_key(object_to_apply, key_to_find, function_to_apply):

    if object_to_apply:

        if isinstance(object_to_apply, list) and len(object_to_apply) > 0:

            for item in object_to_apply:
                object_function_apply_by_key(item, key_to_find, function_to_apply)

        elif isinstance(object_to_apply, dict):

            for k in object_to_apply:

                if isinstance(object_to_apply[k], list):
                    for item in object_to_apply[k]:
                        object_function_apply_by_key(item, key_to_find, function_to_apply)

                elif isinstance(object_to_apply[k], dict):
                    object_function_apply_by_key(object_to_apply[k], key_to_find, function_to_apply)

                if k == key_to_find:
                    function_to_apply(object_to_apply, k)
