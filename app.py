import sys
import os

# Add project root to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.ui import main

if __name__ == "__main__":
    main()
