"""Define loader methods in here so main does not get bloated"""
import importlib
import pkgutil


def load_text_core_commands() -> None:
    import core_commands.text

    for _, module_name, _ in pkgutil.iter_modules(core_commands.text.__path__):
        importlib.import_module(f"core_commands.text.{module_name}")


def load_extensions() -> None:
    import extensions

    for _, module_name, _ in pkgutil.iter_modules(extensions.__path__):
        importlib.import_module(f"extensions.{module_name}")
