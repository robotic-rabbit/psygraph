import asyncio

import pandas as pd

from app.db.session import AsyncSessionLocal, init_db
from app.models.answer import Answer
from app.models.entity import Entity
from app.models.question import Question


async def ingest():
    # 1. Initialize DB tables
    await init_db()
    async with AsyncSessionLocal() as db:

        # ---------------------------------------------------------
        # PART 1: Ingest the Questions (Sliders)
        # ---------------------------------------------------------
        print("Loading questions...")
        items_df = pd.read_csv("data/characters-items-liked.csv", sep="\t")

        questions = []
        for _, row in items_df.iterrows():
            questions.append(
                Question(
                    id=int(row["ITEM_ID"]),
                    pole_left=str(row["pole1"]),
                    pole_right=str(row["pole2"]),
                )
            )
        db.add_all(questions)
        await db.commit()
        print(f"Added {len(questions)} questions.")

        # ---------------------------------------------------------
        # PART 2: Ingest the Characters & Their Scores
        # ---------------------------------------------------------
        print("Loading characters (this takes a few seconds)...")
        # index_col=0 tells pandas that the first column (Unnamed: 0) is the row names
        chars_df = pd.read_csv(
            "data/characters-aggregated-scores.csv", sep="\t", index_col=0
        )

        entity_count = 0
        for char_name, row in chars_df.iterrows():
            # Create the Entity
            entity = Entity(
                name=str(char_name), entity_type="character", is_aggregated=True
            )
            db.add(entity)
            await db.flush()  # Get the auto-generated entity.id

            # Create the Answers for this character
            new_answers = []
            for col_name, value in row.items():
                # col_name looks like "BAP1", "BAP2", etc.
                # We extract the number to link it to the Question ID
                if col_name.startswith("BAP"):
                    question_id = int(col_name.replace("BAP", ""))

                    # Skip if the value is missing/NaN
                    if pd.notna(value):
                        new_answers.append(
                            Answer(
                                entity_id=entity.id,
                                question_id=question_id,
                                value=float(value),
                            )
                        )

            db.add_all(new_answers)
            entity_count += 1

            # Commit every 200 characters to save memory
            if entity_count % 200 == 0:
                await db.commit()
                print(f"Processed {entity_count} characters...")

        # Final commit for any remaining characters
        await db.commit()
        print(f"Done! Ingested {entity_count} characters and their scores.")


if __name__ == "__main__":
    asyncio.run(ingest())
