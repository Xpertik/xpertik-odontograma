/*
 * Odontograma SVG widget — v0.3.0-alpha.1 placeholder client.
 *
 * Phase 2 ships only the constructor scaffolding and auto-mount hook.
 * Phase 5 will attach click handlers, popover rendering, and state
 * propagation (see sdd/v0-3-0-peru-ui/tasks Phase 5).
 */
(function () {
  "use strict";

  class OdontogramaChart {
    constructor(root) {
      this.root = root;
      this.input = root.querySelector('input[type="hidden"]');
      // Phase 5 will wire click handlers, popover, and state persistence.
    }
  }

  function init() {
    document
      .querySelectorAll('.xp-odontograma-widget:not([data-readonly="true"])')
      .forEach(function (root) {
        if (!root.__xpInstance) {
          root.__xpInstance = new OdontogramaChart(root);
        }
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Exported for Phase 5 / third-party integrations.
  window.OdontogramaChart = OdontogramaChart;
})();
