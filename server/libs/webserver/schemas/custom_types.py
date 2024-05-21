valid_name = r"^[a-zA-Zа-яА-Я0-9_ ()-]+$"  # noqa: RUF001
""" Only latin and cyrillic characters, numbers, underscores, spaces, parentheses and dashes are allowed. """

valid_device_id = r"^(device_)(?:0|[1-9]\d{0,1})$"
""" Only `device_0` to `device_99` are allowed. """

valid_group_id = r"^(group_)(?:0|[1-9]\d{0,1})$"
""" Only `group_0` to `group_99` are allowed. """

valid_setting_key = r"^[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*$"
""" Only alphanumeric characters and underscores are allowed. """


valid_name_type = {
    "type": "string",
    "pattern": valid_name,
    "minLength": 1,
    "maxLength": 75,
}

valid_device_id_type = {
    "type": "string",
    "pattern": valid_device_id,
}

valid_group_id_type = {
    "type": "string",
    "pattern": valid_group_id,
}

valid_setting_key_type = {
    "type": "string",
    "pattern": valid_setting_key,
}
