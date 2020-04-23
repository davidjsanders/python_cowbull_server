def check_kwargs(
    parameter_list,
    caller="unknown",
    **kwargs
):
    if not parameter_list:
        raise ValueError("check_kwargs: Parameter list must be specified")

    if len(kwargs) < 1:
        return True

    # Validate no extra parameters
    for kw in kwargs:
        if not kw in parameter_list:
            raise TypeError(
                "Parameter {} is not a valid parameter for {}; valid parameters are: {}"
                .format(kw, caller, parameter_list)
            )
    return True