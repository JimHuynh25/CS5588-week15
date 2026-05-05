from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app


if __name__ == "__main__":
    app.demo.launch(server_name="127.0.0.1", server_port=7862)
