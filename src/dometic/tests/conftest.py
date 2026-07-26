"""Test configuration: add src/ to sys.path so `import dometic` works."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
