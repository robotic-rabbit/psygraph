# NOTE: Just some AI Slop for now replicating the original
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ScoringService:
    def __init__(self):
        self.character_matrix: np.ndarray | None = None
        # FIX 1: Separate set for O(1) lookup, list for strict math ordering
        self.question_ids_set: set[int] = set()
        self.question_ids_list: list[int] = []
        self.entity_meta: dict = {}
        self.e_index: dict[int, int] = {}

    async def load_matrix(self, db: AsyncSession):
        # FIX 2: Use .mappings() to get safe named Row objects instead of brittle tuples
        result = await db.execute(
            text(
                "SELECT id, name, entity_type, universe, image_url FROM entities WHERE is_aggregated = True"
            )
        )
        entities = result.mappings().all()
        self.entity_meta = {e["id"]: e for e in entities}

        result = await db.execute(
            text(
                """
            SELECT entity_id, question_id, value 
            FROM answers 
            WHERE entity_id IN (SELECT id FROM entities WHERE is_aggregated = True)
        """
            )
        )
        answers = result.fetchall()

        if not answers:
            self.character_matrix = np.empty((0, 0))
            return

        df = pd.DataFrame(answers, columns=["entity_id", "question_id", "value"])
        matrix_df = df.pivot(index="entity_id", columns="question_id", values="value")
        matrix_df = matrix_df.reindex(index=self.entity_meta.keys())

        # FIX 1 CONTINUED: Sort the list to guarantee matrix column order never shifts
        self.question_ids_list = sorted(matrix_df.columns.astype(int).tolist())
        self.question_ids_set = set(self.question_ids_list)
        self.e_index = {eid: i for i, eid in enumerate(matrix_df.index)}

        self.character_matrix = matrix_df.to_numpy(dtype=np.float64)

    def score(
        self, user_answers: dict[int, int], version_items: list[int]
    ) -> list[tuple[int, float]]:
        if self.character_matrix is None or self.character_matrix.shape[0] == 0:
            return []

        # O(1) lookup to filter valid questions
        common_q_ids = [qid for qid in version_items if qid in self.question_ids_set]
        if not common_q_ids:
            return []

        # Build user vector strictly aligned to the sorted list order
        user_vec = np.array(
            [float(user_answers.get(qid, np.nan)) for qid in common_q_ids]
        )

        # Find exact matrix column indices based on the strictly ordered list
        col_indices = [self.question_ids_list.index(qid) for qid in common_q_ids]
        X_sub = self.character_matrix[:, col_indices]

        scores = self._pearson_scores(user_vec, X_sub)
        e_ids = list(self.e_index.keys())

        return sorted(
            zip(e_ids, scores),
            key=lambda x: x[1] if not np.isnan(x[1]) else -1.0,
            reverse=True,
        )

    @staticmethod
    def _pearson_scores(user_vec: np.ndarray, X: np.ndarray) -> np.ndarray:
        if np.all(np.isnan(user_vec)):
            return np.full(X.shape[0], np.nan)

        u = user_vec - np.nanmean(user_vec)
        u_std = np.nanstd(user_vec, ddof=1)
        out = np.full(X.shape[0], np.nan)

        for i in range(X.shape[0]):
            v = X[i] - np.nanmean(X[i])
            v_std = np.nanstd(X[i], ddof=1)
            denom = u_std * v_std
            if denom == 0:
                r = 0.0
            else:
                r = np.nansum(u * v) / denom
                r = float(np.clip(r, -1.0, 1.0))
            out[i] = (r + 1.0) * 50.0
        return out
