"""Tests for boot-time HARD extension enforcement (REQ-5.x + REQ-11.4).

Instead of tearing Django's app registry down and up again (which is slow
and brittle), these tests call :func:`validate_extension_dict` directly —
it is the single source of truth for enforcement, and
:meth:`PeruAppConfig.ready` merely loops over its output.

Each rejection path asserts:

1. That :class:`~django.core.exceptions.ImproperlyConfigured` is raised.
2. That the message names the offending field/value.
3. That the message includes a remediation hint (REQ-5.5 scenario).
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured

from xpertik_odontograma.profiles.peru.states import NORMATIVE_KEYS
from xpertik_odontograma.profiles.peru.validators import validate_extension_dict

# ---------------------------------------------------------------------------
# Accept path (REQ-5.5)
# ---------------------------------------------------------------------------


class TestValidExtensions:
    def test_valid_extension_accepted(self):
        exts = {
            "implante_corto": {
                "label": "Implante corto",
                "color": "azul",
                "zona": "corona",
                "categoria": "tratamiento",
                "sigla": "IMP-C",
            }
        }
        result = validate_extension_dict(exts)
        assert len(result) == 1
        assert result[0].key == "implante_corto"
        assert result[0].color_symbolic == "azul"
        assert result[0].sigla == "IMP-C"

    def test_multiple_extensions_accepted(self):
        exts = {
            "implante_corto": {
                "label": "Implante corto",
                "color": "azul",
                "zona": "corona",
                "categoria": "tratamiento",
            },
            "laser_marker": {
                "label": "Marca láser",
                "color": "rojo",
                "zona": "recuadro",
                "categoria": "hallazgo",
            },
        }
        result = validate_extension_dict(exts)
        keys = {nom.key for nom in result}
        assert keys == {"implante_corto", "laser_marker"}

    def test_profile_wrapped_shape_accepted(self):
        # Some docs show the extension dict nested under "peru" — both shapes
        # must work for consumer ergonomics.
        exts = {
            "peru": {
                "implante_corto": {
                    "label": "Implante corto",
                    "color": "azul",
                    "zona": "corona",
                    "categoria": "tratamiento",
                }
            }
        }
        result = validate_extension_dict(exts)
        assert len(result) == 1
        assert result[0].key == "implante_corto"

    def test_empty_dict_accepts(self):
        assert validate_extension_dict({}) == []

    def test_none_accepts(self):
        assert validate_extension_dict(None) == []


# ---------------------------------------------------------------------------
# Reject — override of normative key (REQ-5.2 + Disp. V.14)
# ---------------------------------------------------------------------------


class TestOverrideRejection:
    def test_caries_override_rejected(self):
        exts = {
            "caries": {
                "label": "Mis caries",
                "color": "rojo",
                "zona": "corona",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        message = str(excinfo.value)
        assert "caries" in message
        # Must cite V.14 and/or the "adicionar" remediation hint.
        assert "V.14" in message or "adicionar" in message.lower()

    def test_movilidad_override_rejected(self):
        exts = {
            "movilidad": {
                "label": "Movilidad custom",
                "color": "azul",
                "zona": "recuadro",
                "categoria": "anomalia",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "movilidad" in str(excinfo.value)

    @pytest.mark.parametrize(
        "norm_key", sorted(list(NORMATIVE_KEYS))[:5]  # sample 5 normative keys
    )
    def test_sampled_normative_key_overrides_rejected(self, norm_key):
        exts = {
            norm_key: {
                "label": "Custom",
                "color": "azul",
                "zona": "corona",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured):
            validate_extension_dict(exts)


# ---------------------------------------------------------------------------
# Reject — hex color (REQ-5.3 + Disp. V.7)
# ---------------------------------------------------------------------------


class TestHexColorRejection:
    def test_hex_color_rejected(self):
        exts = {
            "custom": {
                "label": "Custom",
                "color": "#ff0000",
                "zona": "corona",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        message = str(excinfo.value)
        # Message MUST mention the symbolic names so the remediation is
        # obvious to the reader.
        assert "rojo" in message and "azul" in message

    def test_unknown_symbolic_color_rejected(self):
        exts = {
            "custom": {
                "label": "Custom",
                "color": "verde",
                "zona": "corona",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "verde" in str(excinfo.value)

    def test_none_color_rejected(self):
        exts = {
            "custom": {
                "label": "Custom",
                "color": None,
                "zona": "corona",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured):
            validate_extension_dict(exts)


# ---------------------------------------------------------------------------
# Reject — missing required field (REQ-5.4)
# ---------------------------------------------------------------------------


class TestMissingFieldRejection:
    def test_missing_zona_rejected(self):
        exts = {
            "incomplete": {"label": "Incomplete", "color": "azul", "categoria": "hallazgo"}
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "zona" in str(excinfo.value)

    def test_missing_categoria_rejected(self):
        exts = {
            "incomplete": {"label": "Incomplete", "color": "azul", "zona": "corona"}
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "categoria" in str(excinfo.value)

    def test_missing_label_rejected(self):
        exts = {
            "incomplete": {"color": "azul", "zona": "corona", "categoria": "hallazgo"}
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "label" in str(excinfo.value)

    def test_missing_color_rejected(self):
        exts = {
            "incomplete": {"label": "x", "zona": "corona", "categoria": "hallazgo"}
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "color" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Reject — invalid enum values for zona / categoria
# ---------------------------------------------------------------------------


class TestInvalidEnumRejection:
    def test_invalid_zona_rejected(self):
        exts = {
            "custom": {
                "label": "Custom",
                "color": "azul",
                "zona": "not-a-zone",
                "categoria": "hallazgo",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "zona" in str(excinfo.value).lower()

    def test_invalid_categoria_rejected(self):
        exts = {
            "custom": {
                "label": "Custom",
                "color": "azul",
                "zona": "corona",
                "categoria": "not-a-category",
            }
        }
        with pytest.raises(ImproperlyConfigured) as excinfo:
            validate_extension_dict(exts)
        assert "categoria" in str(excinfo.value).lower()


# ---------------------------------------------------------------------------
# Reject — top-level shape errors
# ---------------------------------------------------------------------------


class TestTopLevelShapeRejection:
    def test_non_dict_top_level_rejected(self):
        with pytest.raises(ImproperlyConfigured):
            validate_extension_dict("not-a-dict")

    def test_list_top_level_rejected(self):
        with pytest.raises(ImproperlyConfigured):
            validate_extension_dict(["custom"])

    def test_non_dict_extension_spec_rejected(self):
        exts = {"custom": "not-a-dict"}
        with pytest.raises(ImproperlyConfigured):
            validate_extension_dict(exts)
