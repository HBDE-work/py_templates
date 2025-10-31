import importlib
import pkgutil


class Directories:
    """Define loader methods in here as staticmethods"""
    @staticmethod
    def load_text_core_commands() -> None:
        import core_commands.text

        for _, module_name, _ in pkgutil.iter_modules(core_commands.text.__path__):
            importlib.import_module(f"core_commands.text.{module_name}")

    @staticmethod
    def load_extensions() -> None:
        import extensions

        for _, module_name, _ in pkgutil.iter_modules(extensions.__path__):
            importlib.import_module(f"extensions.{module_name}")
