import subprocess
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[1] / "src" / "cprun"
SOLUTION = '#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b<<"\\n";}\n'


class SampleRunnerTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="sample runner ")
        self.contest = Path(self.workspace.name)
        self.problem = self.contest / "A"
        self.problem.mkdir()
        self.source = self.problem / "A.cpp"
        self.source.write_text(SOLUTION)
        (self.problem / "1.in").write_text("2 3\n")
        (self.problem / "1.out").write_text("5\n")

    def tearDown(self):
        self.workspace.cleanup()

    def run_samples(self, argument):
        return subprocess.run([str(RUNNER), str(argument)], cwd=self.contest,
                              capture_output=True, text=True, timeout=30)

    def test_problem_id_runs_samples_and_preserves_existing_executable(self):
        executable = self.contest / "a.out"
        executable.write_text("preserve this file")
        completed = self.run_samples("a")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("Passed [1/1] tests", completed.stdout)
        self.assertEqual(executable.read_text(), "preserve this file")

    def test_source_path_with_spaces_runs_from_any_directory(self):
        completed = subprocess.run([str(RUNNER), str(self.source)], cwd="/",
                                   capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("Passed [1/1] tests", completed.stdout)

    def test_flat_source_uses_problem_subdirectory_for_samples(self):
        flat_source = self.contest / "a.cpp"
        flat_source.write_text(SOLUTION)
        completed = self.run_samples(flat_source)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_wrong_answer_returns_failure_and_shows_diff(self):
        (self.problem / "1.out").write_text("wrong\n")
        completed = self.run_samples("a")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("Failed sample 1", completed.stdout)
        self.assertIn("-wrong", completed.stdout)

    def test_compilation_error_returns_failure(self):
        self.source.write_text("not valid C++")
        completed = self.run_samples("a")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("Compilation Error", completed.stdout)

    def test_missing_samples_returns_error(self):
        completed = self.run_samples("b")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("No input files", completed.stderr)


if __name__ == "__main__":
    unittest.main()
