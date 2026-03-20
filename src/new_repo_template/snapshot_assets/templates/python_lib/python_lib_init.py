from importlib import import_module

build_greeting = import_module("python_lib.core").build_greeting

__all__ = ["build_greeting"]
