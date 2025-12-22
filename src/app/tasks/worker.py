from . import broker # noqa: F401

import importlib

task_modules = [
    "app.api.v1.book.tasks",
]

for module in task_modules:
    importlib.import_module(module)