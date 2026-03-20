from importlib import import_module


def test_build_greeting_mentions_subject_and_library() -> None:
    library = import_module("python_lib")
    greeting = library.build_greeting("demo-user")

    assert "demo-user" in greeting
    assert "python-lib" in greeting
