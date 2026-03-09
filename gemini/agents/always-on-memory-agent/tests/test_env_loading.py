import os
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"
DOTENV_BACKUP_PATH = PROJECT_ROOT / ".env.codex-backup"
PYTHON_BIN = PROJECT_ROOT / ".venv" / "bin" / "python"


class AgentEnvLoadingTests(unittest.TestCase):
    def setUp(self):
        if DOTENV_BACKUP_PATH.exists():
            self.fail(f"Unexpected backup file present: {DOTENV_BACKUP_PATH}")

        if DOTENV_PATH.exists():
            DOTENV_PATH.rename(DOTENV_BACKUP_PATH)

    def tearDown(self):
        if DOTENV_PATH.exists():
            DOTENV_PATH.unlink()

        if DOTENV_BACKUP_PATH.exists():
            DOTENV_BACKUP_PATH.rename(DOTENV_PATH)

    def run_agent_import(self, extra_env=None):
        env = os.environ.copy()
        env.pop("GOOGLE_API_KEY", None)
        if extra_env:
            env.update(extra_env)

        return subprocess.run(
            [str(PYTHON_BIN), "-c", "import os; import agent; print(os.getenv('GOOGLE_API_KEY', ''))"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_import_loads_google_api_key_from_project_dotenv(self):
        DOTENV_PATH.write_text("GOOGLE_API_KEY=from-dotenv\n", encoding="utf-8")

        result = self.run_agent_import()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stdout.strip(), "from-dotenv")

    def test_import_does_not_override_existing_google_api_key(self):
        DOTENV_PATH.write_text("GOOGLE_API_KEY=from-dotenv\n", encoding="utf-8")

        result = self.run_agent_import({"GOOGLE_API_KEY": "from-environment"})

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stdout.strip(), "from-environment")


if __name__ == "__main__":
    unittest.main()
