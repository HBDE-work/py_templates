#!/usr/bin/env python3

from decorators import MethodAccess, private, private_enforced, public


class Service:
    @public
    def start(self) -> None:
        print("Starting service")

    @private
    def _connect_to_db(self) -> None:
        print("Connecting to DB")

    @private_enforced
    def _update_internals(self) -> None:
        print("Update internals")


def main():
    for name, method in Service.__dict__.items():
        if callable(method):
            print(f"{name:15} -> {getattr(method, '__access__', MethodAccess.unknown)}")
    s = Service()
    s.start()
    s._connect_to_db()
    s._update_internals()


if __name__ == '__main__':
    main()
