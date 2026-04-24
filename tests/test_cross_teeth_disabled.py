"""Cross-teeth nomenclaturas surface as disabled entries (v0.3.0-alpha.1).

Per spec C2 / REQ-6 and design ADR-U7, nomenclaturas with
``cross_teeth=True`` are included in the popover catalog but marked
disabled with the ``Disponible en v0.4.0`` tooltip. The client-side
JS (``peru-chart.js``) consumes the ``cross_teeth`` flag to render them
as ``<option disabled aria-disabled="true" title="Disponible en v0.4.0">``.

These tests verify the contract at the catalog-blob layer emitted by
:class:`PeruOdontogramaWidget` — the JS reads the same blob.
"""

from __future__ import annotations

import json
import re

from xpertik_odontograma.profiles.peru.states import CATALOG
from xpertik_odontograma.profiles.peru.widgets import PeruOdontogramaWidget

# Nomenclaturas flagged ``cross_teeth=True`` in the v0.2.0 norm catalog.
CROSS_TEETH_KEYS: frozenset[str] = frozenset(
    n.key for n in CATALOG if n.cross_teeth
)


def test_catalog_has_six_cross_teeth_entries():
    # VI.1.1 aparato_orto_fijo, VI.1.2 aparato_orto_removible,
    # VI.1.7 diastema, VI.1.16 geminacion_fusion,
    # VI.1.31 supernumerario, VI.1.32 transposicion — exactly 6.
    assert CROSS_TEETH_KEYS == frozenset(
        {
            "aparato_orto_fijo",
            "aparato_orto_removible",
            "diastema",
            "geminacion_fusion",
            "supernumerario",
            "transposicion",
        }
    )


def test_catalog_by_zona_preserves_cross_teeth_flag():
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    # Walk every zona bucket and spot-check each cross-teeth key.
    all_entries = {
        entry["key"]: entry
        for bucket in catalog.values()
        for entry in bucket
    }
    for key in CROSS_TEETH_KEYS:
        assert key in all_entries, f"{key} missing from catalog_by_zona"
        assert all_entries[key]["cross_teeth"] is True
    # Non-cross-teeth entries keep the flag as False.
    assert all_entries["caries"]["cross_teeth"] is False
    assert all_entries["restauracion"]["cross_teeth"] is False


def test_rendered_catalog_script_blob_round_trips_cross_teeth_flag():
    # The <script type="application/json"> blob is what the client JS
    # reads. Ensure cross_teeth booleans survive JSON serialization.
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("odontograma", {}, {})
    # Extract the JSON blob between the opening <script> tag and </script>.
    match = re.search(
        r'<script type="application/json" id="id_odontograma__catalog">\s*(.+?)\s*</script>',
        html,
        re.DOTALL,
    )
    assert match is not None, "catalog script blob not found"
    blob = json.loads(match.group(1))
    all_entries = {
        entry["key"]: entry
        for bucket in blob.values()
        for entry in bucket
    }
    for key in CROSS_TEETH_KEYS:
        assert all_entries[key]["cross_teeth"] is True


def test_corona_bucket_has_expected_non_cross_teeth_core_entries():
    # REQ-5 — the corona bucket feeds the face-click popover; it must
    # expose the 5 corona-level core nomenclaturas (caries, restauracion,
    # ausente, fractura, desgaste is RECUADRO so it goes elsewhere).
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    corona_keys = {e["key"] for e in catalog.get("corona", [])}
    assert {"caries", "restauracion", "ausente", "fractura"} <= corona_keys


def test_raiz_bucket_exposes_apice_nomenclaturas():
    # The apice-click popover filters by zona ∈ {raiz, sobre_apices}.
    # Ensure the two apice-core entries live in the ``raiz`` bucket.
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    raiz_keys = {e["key"] for e in catalog.get("raiz", [])}
    assert {"tratamiento_pulpar", "remanente_radicular"} <= raiz_keys


def test_cross_teeth_entries_carry_parametros_schema_or_none():
    # Structural invariant: parametros_schema is either None or a dict,
    # never an unserializable object. This safeguards the JSON blob.
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    for bucket in catalog.values():
        for entry in bucket:
            schema = entry["parametros_schema"]
            assert schema is None or isinstance(schema, dict)
