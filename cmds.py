from src.extslash import Slash


echo = Slash(name="echo", description="echos the input phrase")
echo.add_options(
    [echo.set_str_option(name='phrase', description='type the phrase you want to echo...', required=True)]
)
setup = Slash(name="setup", description="setup the bot")
