from src.extslash import Slash


cmd = Slash(name="echo", description="echos the input phrase")
cmd.add_options(
    [cmd.set_str_option(name='phrase', description='type the phrase you want to echo...', required=True)]
)
