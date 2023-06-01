from __future__ import annotations

import pytest
import tomli_w

import mapyde
import mapyde.utils


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
    assert "sherpa" in built
    assert built["madspin"]["skip"]
    assert built["base"]["engine"] == "docker"
    assert built["madgraph"]["params"] == "Higgsino"
    assert built["madgraph"]["paramcard"] == "Higgsino.slha"


def test_template_nested(tmp_path):
    template = tmp_path / "enable_madspin.toml"
    template.write_text(tomli_w.dumps({"madspin": {"skip": False}}))

    config = {
        "base": {
            "engine": "fakeengine",
            "path": "/data/users/{{USER}}/SUSY",
            "output": "mytag",
            "template": template.as_posix(),
            "rendered_engine": "{{base['engine']}}",
        },
        "madgraph": {
            "params": "fakeparams",
            "proc": {"name": "charginos", "card": "{{madgraph['proc']['name']}}"},
            "masses": {"MN2": 500},
        },
    }
    built = mapyde.utils.build_config(config)
    assert built
    assert "{{USER}}" not in built["base"]["path"]
    assert "madspin" in built
    assert "sherpa" in built
    assert not built["madspin"]["skip"]
    assert built["base"]["engine"] == "fakeengine"
    assert built["base"]["rendered_engine"] == "fakeengine"
    assert built["madgraph"]["params"] == "fakeparams"
    assert (
        built["madgraph"]["paramcard"] == "fakeparams.slha"
    ), "The rendering of the config happened prematurely, rather than after merging templates."


def test_template_max_nested(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()

    defaults = templates / "defaults.toml"

    template = mapyde.utils.load_config("defaults.toml", mapyde.prefix.templates)
    template["base"].pop("template")  # remove the template key to force recursion
    defaults.write_text(tomli_w.dumps(template))

    with mapyde.prefix(templates.parent):
        config = {
            "base": {
                "path": "/data/users/{{USER}}/SUSY",
                "output": "mytag",
            },
        }
        with pytest.raises(RuntimeError, match=r"Maximum template depth .* exceeded"):
            mapyde.utils.build_config(config)
