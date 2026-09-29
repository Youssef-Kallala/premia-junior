from pathlib import Path 
files = [
    "premia_junior/__init__.py",
    "premia_junior/products/__init__.py",
    "premia_junior/models/__init__.py",
    "premia_junior/methods/__init__.py",
    "premia_junior/engine/__init__.py",
    "premia_junior/utils/__init__.py",
    "tests/__init__.py",
]
for p in files:
    path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)