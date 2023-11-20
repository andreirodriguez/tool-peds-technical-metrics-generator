from repo.DetailRepo import DetailRepo

class DetailModifier:
    def __init__(self, repo: DetailRepo):
        df_detail = repo.table()
        df_detail = df_detail[(df_detail['modified_functionality'] == 'Y')]
        repo.set_table(df_detail)