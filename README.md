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
fish用のPATH設定と `cpget` / `cprun` Functionも導入する。他のShellでは `~/.local/bin` をPATHへ追加する。
fish IntegrationはRepositoryへのSymlinkとして管理する。既に開いているfishでは次を実行して反映する。

```fish
source ~/.config/fish/conf.d/sample-test-runner.fish
```

独自に編集された同名のfish設定がある場合、Installerは上書きせず通知する。
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

AtCoderの公開SampleはLoginなしで取得する。認証が必要なContestやCodeForcesでは、
利用先に対応するEnvironment VariableをShellで設定する。

- AtCoder: `ATCODER_USERNAME` / `ATCODER_PASSWORD`
- CodeForces: `CODEFORCES_USERNAME` / `CODEFORCES_PASSWORD`

fishでは `set -gx VARIABLE value` でEnvironment Variableを設定できる。
fish Function経由なら `set -g` の設定値もCommand実行中だけexportする。
対象は上記Credentials、`SAMPLE_TEST_RUNNER_ROOT`、`XDG_STATE_HOME`（`cpget`）、
`CXX`、`TMPDIR`（`cprun`）。引数は空白を含むPathもそのまま渡す。

CredentialsをRepositoryに保存しない。保存先の既定は `~/workspace/competitive-programming`。
`SAMPLE_TEST_RUNNER_ROOT` で変更できる。fishでは取得成功後に生成されたWorkspaceへ移動する。
生成先は `~/.local/state/sample-test-runner/workspace` に保存する。

AtCoderはTask一覧に掲載されたURLを使い、2秒間隔で順にSampleをDownloadする。
HTTP 429では最大5回Retryし、待機時間は10・20・40・60・60秒。
`Retry-After`（秒数またはHTTP-date）がそれより長い場合は、その指定時間以上待機する。
Retry回数と待機時間をTerminalへ表示し、上限到達や403・404ではErrorとして終了する。
fishからABC086 AのSample取得と実行を確認した。最終確認時にAtCoderがHTTP 403を返したため、
Contest全体のLive取得は未確認。取得後のDirectory移動はIntegration testで確認した。
CodeForces側の現在のLogin/Scraping動作は未検証。

## Validation

```sh
.venv/bin/python -m unittest discover -s tests -v
```

23 Test casesでProblem ID、空白を含むAbsolute Path、Flat Source構成、Wrong answer、Compile error、Sample不足に加え、
fishからの設定値の受け渡し、取得後のDirectory移動、失敗時のExit code保持、AtCoderの実際のTask URLを使う処理を確認する。
429後の復旧、Retry上限、`Retry-After` の秒数・HTTP-date・不正値、逐次Downloadの待機も検証する。
fishがない環境ではfish専用の5件をSkipする。
Nvimの実際のKeymap入力から、[AtCoder ABC086 A](https://atcoder.jp/contests/abc086/tasks/abc086_a)の公式Sample 2個を実行して通過した。
