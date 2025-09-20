import json, os

_config = None
_modified = False


def _load_config():
    global _config, _modified

    if _config is not None:
        return _config

    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            _config = json.load(f)
    else:
        _config = {
            "volume": 20,
            "include_ops": True,
            "include_eds": True,
            "use-yt-dlp": True,
        }
        _modified = True
    return _config


def get_config(key, default=None):
    _load_config()
    return _config.get(key, default)


def set_config(key, value):
    global _modified
    _load_config()
    _config[key] = value
    _modified = True


def update_config(**kwargs):
    """Update only provided keys, leave others unchanged."""
    global _modified
    _load_config()
    for key, value in kwargs.items():
        _config[key] = value
    _modified = True


def save_config():
    """Write config dict to file."""
    if not _modified:
        return
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(_config, f, indent=4)
