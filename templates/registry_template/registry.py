from typing import Callable, Any, Dict, Optional
import inspect

_registry: list[tuple[str, str, Callable[..., None], dict]] = []


def register_command(
    group: str,
    name: str,
    help: Optional[str] = None,
    param_help: Optional[Dict[str,
                              str]] = None,
    **metadata
):
    """Register a command with optional metadata for argument parsing"""
    def decorator(func: Callable[..., None]):
        # Automatically extract function signature info
        sig = inspect.signature(func)
        func_metadata = {
            'signature': sig,
            'params': {
                name: param
                for name,
                param in sig.parameters.items()
            },
            'help': help or func.__doc__,
            'param_help': param_help or {},
            **metadata
        }

        _registry.append((group, name, func, func_metadata))
        return func

    return decorator


def get_registry() -> list[tuple[str, str, Callable[..., None], dict]]:
    return _registry.copy()
