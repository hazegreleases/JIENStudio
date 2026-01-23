import sys
import os
import traceback

sys.path.append(os.getcwd())

try:
    print("Attempting to import weather module...")
    from app.core.augmentation.filters.libraries.core import weather
    print("Weather module imported successfully.")
    print("Content:", dir(weather))
except Exception:
    print("Failed to import weather module.")
    traceback.print_exc()

try:
    print("\nAttempting to load via augmentation_engine...")
    from app.core.augmentation_engine import load_filters
    registry = load_filters()
    print("Registry keys:", list(registry.keys()))
except Exception:
    print("Failed to load filters.")
    traceback.print_exc()
