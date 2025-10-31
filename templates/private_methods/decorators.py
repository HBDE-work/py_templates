from enum import StrEnum
from inspect import stack
from typing import Callable, ParamSpec, TypeVar


class MethodAccess(StrEnum):
    private = "private"
    public = "public"
    unknown = "unknown"


P = ParamSpec("P")
R = TypeVar("R")


def public(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to mark a function or method as public."""
    func.__access__ = MethodAccess.public
    return func


def private(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to mark a function or method as private."""
    func.__access__ = MethodAccess.private
    return func


def private_enforced(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to mark a function or method as private and enfroced at runtime.

    Raises:
        PermissionError if executed from outside of the same module or class
    """

    def wrapper(*args, **kwargs):
        caller = stack()[1].frame.f_locals.get("self", None)
        if caller is not args[0]:  # only allow internal calls
            raise PermissionError(
                f"Cannot call private method '{func.__name__}' from outside the class."
            )
        return func(*args, **kwargs)

    wrapper.__access__ = MethodAccess.private
    return wrapper