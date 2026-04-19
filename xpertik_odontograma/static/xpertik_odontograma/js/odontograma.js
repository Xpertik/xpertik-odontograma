/* xpertik-odontograma v0.1.0 — placeholder dental-chart state sync.
 *
 * v0.1.0 renders a clinical-chart layout (5-face cross per tooth + per-tooth
 * estado block). On every change we:
 *   - sync the tooth's visual mode (caras vs estado) into data-mode,
 *   - paint the face/estado background from the option's data-color,
 *   - show/hide the causa <select> based on estado == "ausente",
 *   - serialize the full state to the hidden <input>.
 *
 * No framework, no build step. Vanilla DOM APIs only.
 * v0.2.0 will replace this chrome with an SVG selector; the hidden-input
 * contract (name + JSON payload) stays the same.
 */
(function () {
  "use strict";

  // ------------------------------------------------------------------
  // State serialization (DOM -> JSON payload for the hidden input)
  // ------------------------------------------------------------------

  function buildPayload(widget) {
    var payload = {};
    var teeth = widget.querySelectorAll(".xp-tooth");
    Array.prototype.forEach.call(teeth, function (tooth) {
      var fdi = tooth.getAttribute("data-fdi");
      if (!fdi) return;
      var mode = tooth.getAttribute("data-mode") || "caras";

      if (mode === "estado") {
        var estadoSelect = tooth.querySelector('[data-role="estado"]');
        var estadoValue = estadoSelect ? estadoSelect.value : "";
        if (!estadoValue) return;  // empty estado = no entry
        var entry = { estado: estadoValue };
        if (estadoValue === "ausente") {
          var causaSelect = tooth.querySelector('[data-role="causa"]');
          var causaValue = causaSelect ? causaSelect.value : "";
          if (causaValue) entry.causa = causaValue;
        }
        payload[fdi] = entry;
      } else {
        var caras = {};
        var faceSelects = tooth.querySelectorAll('[data-role="face"]');
        Array.prototype.forEach.call(faceSelects, function (select) {
          var face = select.getAttribute("data-face");
          var value = select.value;
          if (face && value) caras[face] = value;
        });
        if (Object.keys(caras).length > 0) {
          payload[fdi] = { caras: caras };
        }
      }
    });
    return payload;
  }

  function syncHiddenInput(widget) {
    var input = widget.querySelector('[data-xp-odontograma-input="true"]');
    if (!input) return;
    try {
      input.value = JSON.stringify(buildPayload(widget));
    } catch (err) {
      if (window.console && console.warn) {
        console.warn("xpertik-odontograma: failed to serialize state", err);
      }
    }
  }

  // ------------------------------------------------------------------
  // Visual painting (color a face / estado block from <option data-color>)
  // ------------------------------------------------------------------

  function colorFor(select) {
    var opt = select.options[select.selectedIndex];
    if (!opt) return "";
    return opt.getAttribute("data-color") || "";
  }

  function paintFace(select) {
    var face = select.closest(".xp-tooth__face");
    if (!face) return;
    var color = colorFor(select);
    if (color) {
      face.style.backgroundColor = color;
    } else {
      face.style.backgroundColor = "";
    }
    // Update the inline value label so the user sees the state text too.
    var valueLabel = face.querySelector(".xp-tooth__face-value");
    var opt = select.options[select.selectedIndex];
    var text = opt && select.value ? opt.textContent : "";
    if (text) {
      if (!valueLabel) {
        valueLabel = document.createElement("span");
        valueLabel.className = "xp-tooth__face-value";
        // Insert before the <select> so the text sits above the dropdown.
        face.insertBefore(valueLabel, select);
      }
      valueLabel.textContent = text;
    } else if (valueLabel) {
      valueLabel.textContent = "";
    }
    face.setAttribute("data-value", select.value || "");
  }

  function paintEstado(select) {
    var tooth = select.closest(".xp-tooth");
    if (!tooth) return;
    var estado = tooth.querySelector(".xp-tooth__estado");
    if (!estado) return;
    var color = colorFor(select);
    estado.style.backgroundColor = color || "";
    var label = estado.querySelector(".xp-tooth__estado-label");
    var opt = select.options[select.selectedIndex];
    if (label) {
      label.textContent = (opt && select.value) ? opt.textContent : "\u2014";
    }
    estado.setAttribute("data-estado", select.value || "");
    // Causa is only meaningful when estado == "ausente".
    if (select.value === "ausente") {
      tooth.classList.add("xp-tooth--causa-visible");
    } else {
      tooth.classList.remove("xp-tooth--causa-visible");
      var causaSelect = tooth.querySelector('[data-role="causa"]');
      if (causaSelect) causaSelect.value = "";
    }
  }

  // ------------------------------------------------------------------
  // Mode toggle (caras vs estado) — flips data-mode, which CSS reads.
  // ------------------------------------------------------------------

  function applyModeToggle(radio) {
    var tooth = radio.closest(".xp-tooth");
    if (!tooth) return;
    var mode = radio.value;
    tooth.setAttribute("data-mode", mode);
    tooth.classList.remove("xp-tooth--mode-caras", "xp-tooth--mode-estado");
    tooth.classList.add("xp-tooth--mode-" + mode);
  }

  // ------------------------------------------------------------------
  // Initial pass: paint everything that was pre-filled server-side, and
  // make sure causa-visible class reflects the current estado.
  // ------------------------------------------------------------------

  function hydrate(widget) {
    var faceSelects = widget.querySelectorAll('[data-role="face"]');
    Array.prototype.forEach.call(faceSelects, function (s) {
      if (s.value) paintFace(s);
    });
    var estadoSelects = widget.querySelectorAll('[data-role="estado"]');
    Array.prototype.forEach.call(estadoSelects, function (s) {
      paintEstado(s);
    });
  }

  // ------------------------------------------------------------------
  // Wire up one widget (delegate all change events on the root).
  // ------------------------------------------------------------------

  function wire(widget) {
    hydrate(widget);
    widget.addEventListener("change", function (evt) {
      var target = evt.target;
      if (!target || !target.matches) return;
      var role = target.getAttribute("data-role");
      if (role === "face") {
        paintFace(target);
      } else if (role === "estado") {
        paintEstado(target);
      } else if (role === "mode") {
        applyModeToggle(target);
      }
      if (role === "face" || role === "estado" || role === "mode" || role === "causa") {
        syncHiddenInput(widget);
      }
    });
  }

  function init() {
    var widgets = document.querySelectorAll(".xp-odontograma-widget");
    Array.prototype.forEach.call(widgets, function (widget) {
      try {
        wire(widget);
      } catch (err) {
        if (window.console && console.warn) {
          console.warn("xpertik-odontograma: widget init failed", err);
        }
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
