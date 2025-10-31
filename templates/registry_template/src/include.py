"""Define loader methods in here so main does not get bloated"""
import importlib
import pkgutil


def load_core_commands() -> None:
    from .core_commands import errors, text

    for subpackage in (text, errors):
        for _, module_name, _ in pkgutil.iter_modules(subpackage.__path__):
            importlib.import_module(f"{subpackage.__name__}.{module_name}")


def load_global_commands() -> None:
    from .core_commands import version


def load_extensions() -> None:
    from . import extensions

    for _, module_name, _ in pkgutil.iter_modules(extensions.__path__):
        importlib.import_module(f"{extensions.__name__}.{module_name}")
