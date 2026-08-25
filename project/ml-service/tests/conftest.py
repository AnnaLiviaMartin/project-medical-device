import pathlib
import sys
import types

# Make the project root (parent of this tests/ directory, i.e. the folder that
# contains `app/` and `machine_learning/`) importable.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import app.inference
except ModuleNotFoundError:
    stub = types.ModuleType("app.inference")

    class ModelLoadError(RuntimeError):
        """Stand-in for app.inference.ModelLoadError - see the real module for details."""

    def run_model_on_image(image_path):  # pragma: no cover
        raise AssertionError(
            "The app.inference stub's run_model_on_image() was called directly. "
            "Patch 'app.main.run_model_on_image' in your test instead."
        )

    stub.ModelLoadError = ModelLoadError
    stub.run_model_on_image = run_model_on_image
    sys.modules["app.inference"] = stub
