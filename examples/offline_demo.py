"""Run the synthetic demo from a checkout without installing the package."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cuhkx_portfolio.demo import main

if __name__ == "__main__":
    main()
