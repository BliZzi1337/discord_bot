import os

def list_cogs(exclude: list[str] = None) -> list[str]:
    if exclude is None:
        exclude = []
    return [
        f[:-3]  # ohne ".py"
        for f in os.listdir("cogs")
        if f.endswith(".py") and not f.startswith("_") and f[:-3] not in exclude
    ]
