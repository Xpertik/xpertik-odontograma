/*
 * Peru odontogram chart — v0.3.0-alpha.1 client interaction.
 *
 * Attaches a contextual popover (HTML <dialog>) to each Peru SVG chart.
 * Catalog entries are filtered by the clicked zona:
 *   - face click   -> zona ∈ { corona, recuadro }
 *   - apice click  -> zona ∈ { raiz, sobre_apices }
 * Cross-teeth entries (cross_teeth=true) appear disabled with a tooltip
 * pointing to v0.4.0 (ADR-U7 / D3).
 *
 * State contract (ADR-U10):
 *   - The hidden <input id="id_{name}"> is the single source of truth.
 *   - User selection updates the JS in-memory state dict, re-serializes,
 *     writes it back to the hidden input, and minimally re-paints the
 *     affected face fill. Other overlays (aspa / corona ring / apice
 *     line / siglas) stay stale until form submit — documented as an
 *     alpha.1 limitation; full reactive re-render lands in alpha.2.
 */
(function () {
  "use strict";

  var TITLE_V040 = "Disponible en v0.4.0";
  var ROJO_NORMA = "#d32f2f";
  var AZUL_NORMA = "#1565c0";

  function symbolicToHex(symbolic) {
    if (symbolic === "rojo") return ROJO_NORMA;
    if (symbolic === "azul") return AZUL_NORMA;
    return "transparent";
  }

  class OdontogramaChart {
    constructor(root) {
      this.root = root;
      this.readonly = root.getAttribute("data-readonly") === "true";
      if (this.readonly) return;

      this.input = root.querySelector('input[type="hidden"]');
      this.catalogScript = root.querySelector(
        'script[type="application/json"][id$="__catalog"]'
      );
      this.catalog = this._parseCatalog();
      this.state = this._parseState();
      this.dialog = this._buildDialog();
      document.body.appendChild(this.dialog);
      this.currentSelection = null;

      this._attachListeners();
    }

    // ----- parsing --------------------------------------------------------

    _parseCatalog() {
      if (!this.catalogScript) return {};
      try {
        return JSON.parse(this.catalogScript.textContent || "{}") || {};
      } catch (e) {
        // Silently fall back to an empty catalog; the widget degrades to
        // a passive chart with no popover entries.
        return {};
      }
    }

    _parseState() {
      if (!this.input) return {};
      try {
        return JSON.parse(this.input.value || "{}") || {};
      } catch (e) {
        return {};
      }
    }

    _serializeState() {
      if (!this.input) return;
      this.input.value = JSON.stringify(this.state);
      // Dispatch a change event so frameworks / form logic downstream
      // can observe the mutation (ADR-U10).
      this.input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // ----- dialog construction -------------------------------------------

    _buildDialog() {
      var dialog = document.createElement("dialog");
      dialog.className = "xp-popover";
      dialog.setAttribute("role", "dialog");
      dialog.setAttribute("aria-modal", "true");
      dialog.setAttribute("aria-label", "Seleccionar nomenclatura");
      dialog.innerHTML =
        '<form method="dialog" class="xp-popover__form">' +
          '<h3 class="xp-popover__title"></h3>' +
          '<label class="xp-popover__main-label">' +
            '<span>Nomenclatura</span>' +
            '<select class="xp-popover__main" aria-label="Nomenclatura">' +
              '<option value="">— sin hallazgo —</option>' +
            '</select>' +
          '</label>' +
          '<div class="xp-popover__params"></div>' +
          '<div class="xp-popover__actions">' +
            '<button type="button" class="xp-popover__cancel">Cancelar</button>' +
            '<button type="submit" class="xp-popover__accept" value="confirm">Aceptar</button>' +
          '</div>' +
        '</form>';
      return dialog;
    }

    // ----- event wiring --------------------------------------------------

    _attachListeners() {
      // Delegated click on every face / apice path inside the SVG.
      this.root.addEventListener("click", (e) => this._handlePointer(e));

      // Keyboard activation — SVG elements accept Enter / Space when
      // focused (focusability is a11y-provided by consumers via tabindex
      // injection at a later phase; for alpha.1 we honour any focus).
      this.root.addEventListener("keydown", (e) => {
        if (e.key !== "Enter" && e.key !== " ") return;
        var target = e.target.closest(".xp-face, .xp-apice");
        if (!target) return;
        e.preventDefault();
        target.dispatchEvent(new MouseEvent("click", { bubbles: true }));
      });

      this.dialog
        .querySelector(".xp-popover__cancel")
        .addEventListener("click", () => this.dialog.close("cancel"));

      this.dialog
        .querySelector(".xp-popover__form")
        .addEventListener("submit", (e) => {
          e.preventDefault();
          this._applyPopoverSelection();
          this.dialog.close("confirm");
        });
    }

    _handlePointer(e) {
      var face = e.target.closest(".xp-face");
      var apice = e.target.closest(".xp-apice");
      if (face) {
        this._openPopover(
          "face",
          face.getAttribute("data-fdi"),
          face.getAttribute("data-face")
        );
      } else if (apice) {
        this._openPopover(
          "apice",
          apice.getAttribute("data-fdi"),
          null
        );
      }
    }

    // ----- popover population --------------------------------------------

    _openPopover(zoneType, fdi, faceKey) {
      this.currentSelection = { zoneType: zoneType, fdi: fdi, faceKey: faceKey };
      var title = this.dialog.querySelector(".xp-popover__title");
      var mainSelect = this.dialog.querySelector(".xp-popover__main");
      var paramsDiv = this.dialog.querySelector(".xp-popover__params");

      title.textContent =
        zoneType === "apice"
          ? "Diente " + fdi + " — ápice"
          : "Diente " + fdi + " — " + (faceKey || "cara");

      // Filter catalog entries by allowed zonas for this zoneType.
      var allowedZonas =
        zoneType === "apice" ? ["raiz", "sobre_apices"] : ["corona", "recuadro"];
      var entries = [];
      for (var i = 0; i < allowedZonas.length; i++) {
        var bucket = this.catalog[allowedZonas[i]] || [];
        for (var j = 0; j < bucket.length; j++) entries.push(bucket[j]);
      }

      // Rebuild the main select.
      mainSelect.innerHTML = '<option value="">— sin hallazgo —</option>';
      for (var k = 0; k < entries.length; k++) {
        var entry = entries[k];
        var opt = document.createElement("option");
        opt.value = entry.key;
        opt.textContent = entry.label;
        if (entry.cross_teeth) {
          opt.disabled = true;
          opt.title = TITLE_V040;
          opt.setAttribute("aria-disabled", "true");
        }
        mainSelect.appendChild(opt);
      }

      // Read the current value for this zone (if any).
      var toothState = this.state[fdi] || {};
      var current = "";
      var currentParams = {};
      if (zoneType === "apice" && toothState.apice) {
        current = toothState.apice.estado || "";
        currentParams = toothState.apice.parametros || {};
      } else if (
        zoneType === "face" &&
        toothState.caras &&
        toothState.caras[faceKey]
      ) {
        current = toothState.caras[faceKey];
        currentParams = toothState.parametros || {};
      }
      mainSelect.value = current;

      // Wire the main select → params sub-section refresh.
      var self = this;
      mainSelect.onchange = function () {
        self._updateParamsSection(entries, mainSelect.value, {});
      };
      this._updateParamsSection(entries, current, currentParams);

      if (typeof this.dialog.showModal === "function") {
        try {
          this.dialog.showModal();
        } catch (_) {
          this.dialog.setAttribute("open", "");
        }
      } else {
        this.dialog.setAttribute("open", "");
      }
    }

    _updateParamsSection(entries, selectedKey, currentParams) {
      var paramsDiv = this.dialog.querySelector(".xp-popover__params");
      paramsDiv.innerHTML = "";
      if (!selectedKey) return;
      var entry = null;
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].key === selectedKey) {
          entry = entries[i];
          break;
        }
      }
      if (!entry || !entry.parametros_schema) return;

      var schema = entry.parametros_schema;
      var keys = Object.keys(schema);
      for (var k = 0; k < keys.length; k++) {
        var paramName = keys[k];
        var allowed = schema[paramName] || [];
        var label = document.createElement("label");
        label.className = "xp-popover__param";
        var span = document.createElement("span");
        span.textContent = paramName;
        label.appendChild(span);
        var select = document.createElement("select");
        select.setAttribute("data-param", paramName);
        for (var v = 0; v < allowed.length; v++) {
          var option = document.createElement("option");
          option.value = String(allowed[v]);
          option.textContent = String(allowed[v]);
          select.appendChild(option);
        }
        if (currentParams[paramName] !== undefined) {
          select.value = String(currentParams[paramName]);
        }
        label.appendChild(select);
        paramsDiv.appendChild(label);
      }
    }

    // ----- apply + minimal repaint ---------------------------------------

    _applyPopoverSelection() {
      if (!this.currentSelection) return;
      var ctx = this.currentSelection;
      var mainSelect = this.dialog.querySelector(".xp-popover__main");
      var paramSelects = this.dialog.querySelectorAll(
        ".xp-popover__params select[data-param]"
      );
      var newKey = mainSelect.value;
      var newParams = {};
      paramSelects.forEach(function (sel) {
        if (sel.value !== "") newParams[sel.getAttribute("data-param")] = sel.value;
      });

      if (!this.state[ctx.fdi]) this.state[ctx.fdi] = {};
      var tooth = this.state[ctx.fdi];

      if (ctx.zoneType === "apice") {
        if (newKey) {
          tooth.apice = { estado: newKey };
          if (Object.keys(newParams).length > 0) {
            tooth.apice.parametros = newParams;
          }
        } else if (tooth.apice) {
          delete tooth.apice;
        }
      } else {
        if (!tooth.caras) tooth.caras = {};
        if (newKey) {
          tooth.caras[ctx.faceKey] = newKey;
          // Parameters on a face-level entry live at the tooth level
          // (e.g. restauracion.material). Only overwrite when present.
          if (Object.keys(newParams).length > 0) {
            tooth.parametros = Object.assign({}, tooth.parametros || {}, newParams);
          }
        } else {
          delete tooth.caras[ctx.faceKey];
          if (Object.keys(tooth.caras).length === 0) delete tooth.caras;
        }
      }

      this._serializeState();
      this._minimalRepaint(ctx, newKey);
    }

    _minimalRepaint(ctx, newKey) {
      // Face fills are the one overlay we can repaint client-side without
      // rerunning the full renderer. The other overlays (aspa / corona
      // ring / apice line / siglas) require a server re-render for now.
      if (ctx.zoneType !== "face") return;
      var facePath = this.root.querySelector(
        '.xp-face[data-fdi="' + ctx.fdi + '"][data-face="' + ctx.faceKey + '"]'
      );
      if (!facePath) return;
      if (!newKey) {
        facePath.setAttribute("fill", "transparent");
        return;
      }
      var color = "transparent";
      var zonas = ["corona", "recuadro", "raiz", "sobre_apices"];
      for (var i = 0; i < zonas.length; i++) {
        var bucket = this.catalog[zonas[i]] || [];
        for (var j = 0; j < bucket.length; j++) {
          if (bucket[j].key === newKey) {
            color = symbolicToHex(bucket[j].color_symbolic);
            break;
          }
        }
        if (color !== "transparent") break;
      }
      facePath.setAttribute("fill", color);
    }
  }

  function initAll() {
    var roots = document.querySelectorAll(
      ".xp-odontograma-widget.xp-peru[data-readonly='false']"
    );
    roots.forEach(function (root) {
      if (!root.__xpPeruInstance) {
        root.__xpPeruInstance = new OdontogramaChart(root);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }

  // Expose for testing / consumer customisation.
  window.PeruOdontogramaChart = OdontogramaChart;
})();
