from src.extslash import Slash


cmd_one = Slash(name="extended", description="adds slash command to dpy")
cmd_one.add_options(
    [
        cmd_one.set_int_option(name='rate', description='rate the lib 1 -> 10', required=True),
        cmd_one.set_str_option(name='name', description='type your name', required=True),
    ]
)
