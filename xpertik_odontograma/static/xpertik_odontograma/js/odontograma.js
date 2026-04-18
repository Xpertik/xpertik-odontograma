/* xpertik-odontograma v0.1.0 — minimal state-sync stub.
 *
 * v0.1.0 renders <select> elements per tooth/face; on any change we
 * serialize the form state back into the hidden input carried by the
 * widget. No framework, no build step.
 *
 * v0.2.0 will replace the <select> chrome with an SVG-driven selector;
 * the widget signature (name + hidden input) stays the same, so this
 * glue is all that changes.
 */
(function () {
  "use strict";

  function buildPayload(container) {
    var payload = {};
    var selects = container.querySelectorAll('[data-role="estado"], [data-role="face"]');
    Array.prototype.forEach.call(selects, function (select) {
      var fdi = select.getAttribute("data-fdi");
      if (!fdi) return;

      var value = select.value;
      var role = select.getAttribute("data-role");

      if (role === "estado") {
        if (!value) return;
        payload[fdi] = payload[fdi] || {};
        // 'estado' and 'caras' are XOR per the spec; drop any caras from the
        // same tooth if the user just picked an estado.
        delete payload[fdi].caras;
        payload[fdi].estado = value;
      } else if (role === "face") {
        var face = select.getAttribute("data-face");
        if (!face) return;
        if (!value) return;
        if (payload[fdi] && payload[fdi].estado) {
          // User set an estado AND is editing faces — keep estado; skip.
          return;
        }
        payload[fdi] = payload[fdi] || { caras: {} };
        payload[fdi].caras = payload[fdi].caras || {};
        payload[fdi].caras[face] = value;
      }
    });
    return payload;
  }

  function syncInput(widget) {
    var input = widget.querySelector('[data-xp-odontograma-input="true"]');
    if (!input) return;
    try {
      input.value = JSON.stringify(buildPayload(widget));
    } catch (err) {
      // Swallow — never break form submission because of serialization.
      if (window.console && console.warn) {
        console.warn("xpertik-odontograma: failed to serialize state", err);
      }
    }
  }

  function init() {
    var widgets = document.querySelectorAll(".xp-odontograma-widget");
    Array.prototype.forEach.call(widgets, function (widget) {
      widget.addEventListener("change", function (evt) {
        if (!evt.target || !evt.target.matches) return;
        if (!evt.target.matches('[data-role="estado"], [data-role="face"]')) return;
        syncInput(widget);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
