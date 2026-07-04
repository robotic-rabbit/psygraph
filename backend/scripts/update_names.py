import asyncio
import html
import json
import re

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


async def update_names():
    print("Reading data/key.js...")
    with open("data/key.js", "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 1. Extract ONLY the JavaScript object
    match = re.search(r"var subjects\s*=\s*(\{.*\});", raw_text, re.DOTALL)
    if not match:
        print("ERROR: Could not find 'var subjects = {...};' in the file!")
        return

    js_obj = match.group(1)

    # 2. Clean up the JavaScript to make it valid JSON
    # Fix HTML entities (e.g., O&apos;Malley becomes O'Malley)
    js_obj = html.unescape(js_obj)

    # NOTE: We DO NOT replace single quotes with double quotes here.
    # Single quotes inside strings (like O'Malley) are perfectly valid JSON!

    # Add double quotes around unquoted dictionary keys (e.g., 1 : -> "1":)
    js_obj = re.sub(r"([{,]\s*)(\w+)\s*:", r'\1"\2":', js_obj)

    # Remove trailing commas before closing brackets (JSON hates trailing commas)
    js_obj = re.sub(r",\s*([}\]])", r"\1", js_obj)

    # 3. Parse into a Python dictionary
    try:
        subjects = json.loads(js_obj)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return

    # 4. Update the Database
    print("Updating database...")
    async with AsyncSessionLocal() as db:
        updated_count = 0

        for univ_code, characters in subjects.items():
            univ_name = characters.get("name", univ_code)

            for char_num, char_data in characters.items():
                # FIXED: JS numbers became strings in JSON (e.g., "1" instead of 1)
                # We check if it's a numeric string instead of an actual integer
                if not str(char_num).isdigit():
                    continue

                # Convert back to integer for the DB code
                char_num = int(char_num)

                db_code = f"{univ_code}/{char_num}"
                char_name = char_data[0]
                img_path = char_data[1]

                # Point to your local data folder
                image_url = f"/data/profile_pics/{img_path}"

                query = text(
                    """
                    UPDATE entities 
                    SET name = :name, universe = :universe, image_url = :image_url 
                    WHERE name = :db_code AND entity_type = 'character'
                """
                )
                result = await db.execute(
                    query,
                    {
                        "name": char_name,
                        "universe": univ_name,
                        "image_url": image_url,
                        "db_code": db_code,
                    },
                )

                if result.rowcount > 0:
                    updated_count += 1

            await db.commit()
        print(
            f"Success! Updated {updated_count} characters with real names and local image paths."
        )


if __name__ == "__main__":
    asyncio.run(update_names())
