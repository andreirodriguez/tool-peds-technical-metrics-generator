def get_files_lines_per_type(repo_with_pr_id, commit_df, type, column):
    result = commit_df[(commit_df['repo_with_pr_id'] == repo_with_pr_id) & 
                    (commit_df['type'] == type)]
    return result[column].values[0] if not result.empty else []

def get_all_files_lines(repo_with_pr_id, commit_df, column):
    result = commit_df[commit_df['repo_with_pr_id'] == repo_with_pr_id]
    return result[column].values[0] if not result.empty else []


def get_type_of_commit(commit_message: str, file_count: int) -> str:
    """get the type of the commit
    - devops
    - feat
    - fix
    - perf
    - refactor
    - test
    - style
    - chore
    - ci
    - docs
    - other"""

    if ("MERGE" in commit_message.upper() and file_count == 0) or "[CI-RELEASE" in commit_message.upper():
        return "devops"

    if ("FEAT:" in commit_message.upper() or "FEAT(" in commit_message.upper() or "FEAT (" in commit_message.upper()):
        return "feat"

    if "FIX:" in commit_message.upper() or "FIX(" in commit_message.upper():
        return "fix"

    if "PERF:" in commit_message.upper() or "PERF(" in commit_message.upper():
        return "perf"

    if "REFACTOR:" in commit_message.upper() or "REFACTOR(" in commit_message.upper():
        return "refactor"

    if "TEST:" in commit_message.upper() or "TEST(" in commit_message.upper():
        return "test"

    if "STYLE:" in commit_message.upper() or "STYLE(" in commit_message.upper():
        return "style"

    if "CHORE:" in commit_message.upper() or "CHORE(" in commit_message.upper():
        return "chore"

    if ("CI:" in commit_message.upper() or "CI(" in commit_message.upper() or "CI (" in commit_message.upper()):
        return "ci"

    if ("DOCS:" in commit_message.upper() or "DOCS(" in commit_message.upper()
        or "DOC:" in commit_message.upper() or "DOC(" in commit_message.upper() ):
        return "docs"

    return "other"
