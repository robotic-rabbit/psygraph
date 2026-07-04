import asyncio

import pandas as pd

from app.db.session import AsyncSessionLocal, init_db
from app.models.answer import Answer
from app.models.entity import Entity
from app.models.question import Question


async def ingest():
    await init_db()
    async with AsyncSessionLocal() as db:
        print("Ingesting questions...")
        items_df = pd.read_csv("data/characters-items-liked.csv")
        questions = [
            Question(id=row["ITEM_ID"], pole_left=row["pole1"], pole_right=row["pole2"])
            for _, row in items_df.iterrows()
        ]
        db.add_all(questions)
        await db.commit()

        print("Ingesting characters...")
        chars_df = pd.read_csv("data/SWCPQ-Features-Aggregated-Dataset.csv")

        for _, row in chars_df.iterrows():
            entity = Entity(
                name=row["Character_Name"],
                entity_type="character",
                universe=row.get("Universe"),
                is_aggregated=True,
            )
            db.add(entity)
            await db.flush()

            # FIX: Gather all answers for this character, then add_all once per character
            new_answers = []
            for q_id in items_df["ITEM_ID"]:
                col_name = str(q_id)
                if col_name in row and pd.notna(row[col_name]):
                    new_answers.append(
                        Answer(
                            entity_id=entity.id,
                            question_id=int(q_id),
                            value=float(row[col_name]),
                        )
                    )
            db.add_all(new_answers)

        await db.commit()
        print("Ingestion complete!")


if __name__ == "__main__":
    asyncio.run(ingest())
