# All SQL commands for maps
sql_table = {
    "get_name": "SELECT name FROM Meta WHERE id = 1",

    "set_name": "UPDATE Meta SET name = ? WHERE id = 1",

    "get_elements": """
        SELECT
            Elements.id,
            Elements.name,
            Elements.x,
            Elements.y,
            Elements.width,
            Elements.height,
            Elements.background_image AS background_image,
            Assets.name AS background_image_name,
            Assets.value AS background_image_data,
            Elements.background_color AS background_image_color
        FROM Elements
        LEFT JOIN Assets ON Elements.background_image = Assets.id;
    """,
    "get_element": """
        SELECT
            Elements.id,
            Elements.name,
            Elements.x,
            Elements.y,
            Elements.width,
            Elements.height,
            Elements.background_image AS background_image,
            Assets.name AS background_image_name,
            Assets.value AS background_image_data,
            Elements.background_color AS background_image_color
        FROM Elements
        LEFT JOIN Assets ON Elements.background_image = Assets.id
        WHERE Elements.id = ?;
    """,

    "create_element": "INSERT INTO Elements (name, x, y, width, height) VALUES (?, ?, ?, ?, ?);",

    "edit_element": """
        UPDATE Elements SET
            name = ?,
            x = ?,
            y = ?,
            width = ?,
            height = ?,
            background_image = ?,
            background_color = ?
        WHERE id = ?
    """,

    "remove_element": "DELETE FROM Elements WHERE id = ?",

    "element_exists": "SELECT EXISTS (SELECT id FROM Elements WHERE id = ?)",

    "get_assets": "SELECT name, value FROM Assets",

    "create_asset": "INSERT INTO Assets (name, value) VALUES (?, ?)",

    "remove_asset": "DELETE FROM Assets WHERE id = ?",

    "asset_exists": "SELECT EXISTS (SELECT id FROM Assets WHERE id = ?)"
}
