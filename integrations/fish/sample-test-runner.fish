fish_add_path -g $HOME/.local/bin

function cpget --description 'Fetch contest samples and enter the workspace'
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
