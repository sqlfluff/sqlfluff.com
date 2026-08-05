(function () {
  "use strict";

  var COOKIE_NAME = "sqlfluff-theme";
  var VALID_PREFERENCES = ["auto", "light", "dark"];
  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function readPreference() {
    var prefix = COOKIE_NAME + "=";
    var cookie = document.cookie.split("; ").find(function (item) {
      return item.indexOf(prefix) === 0;
    });
    var value = cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "auto";
    return VALID_PREFERENCES.indexOf(value) >= 0 ? value : "auto";
  }

  function resolveTheme(preference) {
    if (preference === "auto") {
      return mediaQuery.matches ? "dark" : "light";
    }
    return preference;
  }

  function applyPreference(preference) {
    var theme = resolveTheme(preference);
    var themeColour = document.querySelector('meta[name="theme-color"]');
    document.documentElement.dataset.themePreference = preference;
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    if (themeColour) {
      themeColour.setAttribute("content", theme === "dark" ? "#0d1117" : "#f7f8f8");
    }

    document.querySelectorAll("[data-sqlfluff-theme-value]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.sqlfluffThemeValue === preference));
    });
  }

  function writePreference(preference) {
    var hostname = window.location.hostname;
    var isSqlfluffDomain = hostname === "sqlfluff.com" || hostname.endsWith(".sqlfluff.com");
    var parts = [
      COOKIE_NAME + "=" + encodeURIComponent(preference),
      "Path=/",
      "SameSite=Lax",
      "Max-Age=31536000"
    ];

    if (isSqlfluffDomain) {
      parts.push("Domain=sqlfluff.com", "Secure");
    } else if (window.location.protocol === "https:") {
      parts.push("Secure");
    }

    document.cookie = parts.join("; ");
    applyPreference(preference);
  }

  function initialiseControls() {
    applyPreference(readPreference());

    document.querySelectorAll("[data-sqlfluff-theme-value]").forEach(function (button) {
      button.addEventListener("click", function () {
        writePreference(button.dataset.sqlfluffThemeValue);
      });
    });

    document.querySelectorAll("[data-sqlfluff-nav]").forEach(function (header) {
      var toggle = header.querySelector("[data-sqlfluff-nav-toggle]");
      var menu = header.querySelector("[data-sqlfluff-nav-menu]");
      if (!toggle || !menu) return;
      var toggleLabel = toggle.querySelector(".sqlfluff-visually-hidden");

      function setMenuState(isOpen) {
        menu.classList.toggle("is-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
        if (toggleLabel) toggleLabel.textContent = isOpen ? "Close navigation" : "Open navigation";
      }

      function closeMenu() {
        setMenuState(false);
      }

      toggle.addEventListener("click", function () {
        setMenuState(!menu.classList.contains("is-open"));
      });

      menu.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", closeMenu);
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && menu.classList.contains("is-open")) {
          closeMenu();
          toggle.focus();
        }
      });
    });
  }

  applyPreference(readPreference());
  mediaQuery.addEventListener("change", function () {
    if (readPreference() === "auto") applyPreference("auto");
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseControls);
  } else {
    initialiseControls();
  }
})();
