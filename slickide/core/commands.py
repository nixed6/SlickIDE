class CommandRegistry:
    def __init__(self):
        self._commands = {}

    def register(self, name, callback):
        self._commands[name] = callback

    def execute(self, name, *args, **kwargs):
        if name in self._commands:
            return self._commands[name](*args, **kwargs)
        else:
            print(f"Command '{name}' not found.")