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
            Elements.background_image AS background_image_id,
            Assets.name AS background_image_name,
            Assets.value AS background_image_data,
            Elements.background_color AS background_image_color
        FROM Elements
        LEFT JOIN Assets ON Elements.background_image = Assets.id;
    """
}
