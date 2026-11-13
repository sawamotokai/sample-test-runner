# Sample Test Runner

AtCoder・CodeForcesのSampleを取得し、C++の解答をCompileして比較する。
元のRepositoryの履歴を保持したmacOS向けInstallation Branch。

## Installation

```sh
brew install uv gcc
git clone https://github.com/sawamotokai/sample-test-runner.git ~/.local/share/sample-test-runner
cd ~/.local/share/sample-test-runner
bash install.sh
```

このBranchのInstallerはPython 3.12の専用Virtual environmentを作り、Lock済みDependenciesを導入する。
`~/.local/bin/cprun` と `cpget` はSource ScriptへのSymlink。sudoやSystem PythonへのPackage追加は不要。
fish用のPATH設定と `cpget` Functionも導入する。他のShellでは `~/.local/bin` をPATHへ追加する。
GitHubへのpush前は、このMacにあるLocal Branchを利用する。

## Sampleの実行

```sh
# 元のDirectory構成: A/A.cpp, A/1.in, A/1.out, ...
cprun a

# Source Fileを直接指定する。実行時のCurrent Directoryは任意。
cprun /path/to/A/A.cpp
```

`a.cpp` がContest Directory直下にある場合は、隣の `A/` からSampleを読む。
SourceのDirectoryに `.in` がある場合は、そのDirectoryを使う。Expected outputは同名の `.out`。

Compilerは `CXX` があればそれを使い、なければHomebrew GCCの `g++-<version>`、最後に `g++` の順で選ぶ。
C++17・UBSan・O2でCompileする。Binaryと実行結果はTemporary Directoryに置き、既存の `a.out` を上書きしない。
全Sample通過はExit code 0、Wrong answer・Compile/Runtime errorは1、引数・Sample不足は2。

## Nvim

NvChad Customの `Space d r` で、現在の `.cpp` Fileを保存してTerminal Split内でSampleを実行する。
実装は `~/.config/nvim/lua/configs/runner.lua`。

## Sampleの取得

```sh
cpget
```

元のParserはLoginを前提にしている。利用先に対応するEnvironment VariableをShellで設定する。

- AtCoder: `ATCODER_USERNAME` / `ATCODER_PASSWORD`
- CodeForces: `CODEFORCES_USERNAME` / `CODEFORCES_PASSWORD`

CredentialsをRepositoryに保存しない。保存先の既定は `~/workspace/competitive-programming`。
`SAMPLE_TEST_RUNNER_ROOT` で変更できる。fishでは取得成功後に生成されたWorkspaceへ移動する。
生成先は `~/.local/state/sample-test-runner/workspace` に保存する。

Website側の現在のLogin/Scraping動作は未検証。Installation時はMenu表示とCancelを確認し、認証やSubmissionは行っていない。

## Validation

```sh
.venv/bin/python -m unittest discover -s tests -v
```

6 Test casesでProblem ID、空白を含むAbsolute Path、Flat Source構成、Wrong answer、Compile error、Sample不足を確認。
Nvimの実際のKeymap入力から、[AtCoder ABC086 A](https://atcoder.jp/contests/abc086/tasks/abc086_a)の公式Sample 2個を実行して通過した。
