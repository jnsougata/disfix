import inspect
from typing import List, Dict, Any, Optional, Union, Callable



def _build_prams(options: Dict[str, Any], callable: Callable):
    args = []
    kwargs = {}
    params = inspect.getfullargspec(callable)
    default_args = params.defaults
    default_kwargs = params.kwonlydefaults
    if default_args:
        default_list = [*default_args]
        for i in range(len(params.args[:2]) - len(default_list) - 1):
            default_list.insert(i, None)

        for arg, default_value in zip(params.args[2:], default_list):
            option = options.get(arg)
            if option:
                args.append(option.value)
            else:
                args.append(default_value)
    else:
        for arg in params.args[2:]:
            option = options.get(arg)
            if option:
                args.append(option.value)
            else:
                args.append(None)

    for kw in params.kwonlyargs:
        option = options.get(kw)
        if option:
            kwargs[kw] = option.value
        else:
            kwargs[kw] = default_kwargs.get(kw) if default_kwargs else None
    return args, kwargs
