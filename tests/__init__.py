# VS Code works without sys.path mangling, but CLI needs sys.path to be changed
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
)
