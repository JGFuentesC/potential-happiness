import subprocess
import sys
from pathlib import Path

VENV_PATH = Path(__file__).parent.parent / ".venv"
KERNEL_NAME = "fakestore-venv"
DISPLAY_NAME = "Python (fakestore .venv)"


def get_python_path():
    if sys.platform == "win32":
        return VENV_PATH / "Scripts" / "python.exe"
    return VENV_PATH / "bin" / "python"


def install_kernel():
    python = get_python_path()
    if not python.exists():
        print(f"Error: venv not found at {python}")
        print("Run: uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt")
        sys.exit(1)

    print(f"Registering kernel '{KERNEL_NAME}'...")
    subprocess.check_call([
        str(python), "-m", "ipykernel", "install",
        "--user",
        "--name", KERNEL_NAME,
        "--display-name", DISPLAY_NAME,
    ])

    print(f"Kernel '{DISPLAY_NAME}' registered successfully!")
    print(f"Select it in Jupyter: Kernel → Change Kernel → {DISPLAY_NAME}")


if __name__ == "__main__":
    install_kernel()
