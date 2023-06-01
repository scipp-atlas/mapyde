from __future__ import annotations

import mapyde


def test_template_false():
    config = {
        "base": {
            "path": "/data/users/{{USER}}/SUSY",
            "output": "mytag",
            "template": False,
        },
        "madgraph": {
            "proc": {"name": "charginos", "card": "{{madgraph['proc']['name']}}"},
            "masses": {"MN2": 500},
        },
    }
    built = mapyde.utils.build_config(config)
    assert built
    assert "{{USER}}" not in built["base"]["path"]
    assert "madspin" not in built


def test_template_empty():
    config = {
        "base": {"path": "/data/users/{{USER}}/SUSY", "output": "mytag"},
        "madgraph": {
            "proc": {"name": "charginos", "card": "{{madgraph['proc']['name']}}"},
            "masses": {"MN2": 500},
        },
    }
    built = mapyde.utils.build_config(config)
    assert built
    assert "{{USER}}" not in built["base"]["path"]
    assert "madspin" in built
