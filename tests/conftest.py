import sys
from pathlib import Path

# Add repo root to sys.path so 'src' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
