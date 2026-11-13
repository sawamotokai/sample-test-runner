fish_add_path -g $HOME/.local/bin

function cpget --description 'Fetch contest samples and enter the workspace'
    # Fish globals are not exported by default; limit these exports to cpget.
    for name in ATCODER_USERNAME ATCODER_PASSWORD CODEFORCES_USERNAME CODEFORCES_PASSWORD SAMPLE_TEST_RUNNER_ROOT XDG_STATE_HOME
        if set -q $name
            set -fx $name $$name
        end
    end
    command cpget $argv
    or return $status
    set -l state_dir $HOME/.local/state
    if set -q XDG_STATE_HOME
        set state_dir $XDG_STATE_HOME
    end
    set -l workspace_file $state_dir/sample-test-runner/workspace
    if test -f "$workspace_file"
        set -l contest_directory (cat "$workspace_file")
        if test -d "$contest_directory"
            cd "$contest_directory"
        end
    end
end

function cprun --description 'Compile a C++ solution and run its samples'
    for name in CXX TMPDIR
        if set -q $name
            set -fx $name $$name
        end
    end
    command cprun $argv
end
