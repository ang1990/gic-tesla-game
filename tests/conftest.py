import sys
from pathlib import Path

# Allow test modules to import from the project root without installation.
sys.path.insert(0, str(Path(__file__).parent.parent))
