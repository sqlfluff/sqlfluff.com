(function () {
  "use strict";

  var COOKIE_NAME = "sqlfluff-theme";
  var VALID_PREFERENCES = ["auto", "light", "dark"];
  var DARK_CLASS = "dark";
  var THEME_COLOURS = { light: "#f7f8f8", dark: "#0d1117" };
  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  var subscribers = [];

  function normalise(value) {
    return VALID_PREFERENCES.indexOf(value) >= 0 ? value : "auto";
  }

  function readCookie() {
    var prefix = COOKIE_NAME + "=";
    var cookie = document.cookie.split("; ").find(function (item) {
      return item.indexOf(prefix) === 0;
    });
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
  }

  // Same-origin fallback for readers whose browser or privacy settings reject
  // cookies. It cannot follow a reader between subdomains, so the cookie stays
  // the primary record and this is only consulted when the cookie is absent.
  function readFallback() {
    try {
      return window.localStorage.getItem(COOKIE_NAME) || "";
    } catch (error) {
      return "";
    }
  }

  function readPreference() {
    return normalise(readCookie() || readFallback());
  }

  function resolveTheme(preference) {
    if (preference === "auto") {
      return mediaQuery.matches ? "dark" : "light";
    }
    return preference;
  }

  function syncControls(preference) {
    document.querySelectorAll("[data-sqlfluff-theme-value]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.sqlfluffThemeValue === preference));
    });
  }

  function applyPreference(preference) {
    var root = document.documentElement;
    var theme = resolveTheme(preference);
    var themeColour = document.querySelector('meta[name="theme-color"]');

    root.dataset.themePreference = preference;
    root.dataset.theme = theme;
    root.style.colorScheme = theme;

    // Frameworks with their own dark styling, such as VitePress, key off a
    // `dark` class rather than an attribute. Setting both lets a consumer adopt
    // the shared tokens without shimming one signal onto the other.
    root.classList.toggle(DARK_CLASS, theme === "dark");

    if (themeColour) {
      themeColour.setAttribute("content", THEME_COLOURS[theme]);
    }

    syncControls(preference);

    subscribers.forEach(function (listener) {
      try {
        listener(preference, theme);
      } catch (error) {
        // A failing subscriber must not stop the others or the theme swap.
      }
    });
  }

  function writePreference(value) {
    var preference = normalise(value);
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

    try {
      window.localStorage.setItem(COOKIE_NAME, preference);
    } catch (error) {
      // Storage is optional; the cookie above is the primary record.
    }

    applyPreference(preference);
  }

  // The header separator is only drawn once content has scrolled under it. The
  // border is present by default and this removes it at the top of the page, so
  // a reader without JavaScript keeps a separated header rather than none.
  var scrollFrame = 0;

  function syncHeaderScroll() {
    scrollFrame = 0;
    var isTop = (window.scrollY || window.pageYOffset || 0) <= 0;

    document.querySelectorAll("[data-sqlfluff-nav]").forEach(function (header) {
      header.classList.toggle("is-top", isTop);
    });
  }

  function queueHeaderScroll() {
    if (scrollFrame) return;
    scrollFrame = window.requestAnimationFrame(syncHeaderScroll);
  }

  function setMenuState(header, isOpen) {
    var toggle = header.querySelector("[data-sqlfluff-nav-toggle]");
    var menu = header.querySelector("[data-sqlfluff-nav-menu]");
    if (!toggle || !menu) return;
    var label = toggle.querySelector(".sqlfluff-visually-hidden");

    menu.classList.toggle("is-open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
    if (label) label.textContent = isOpen ? "Close navigation" : "Open navigation";
  }

  function closeMenus() {
    document.querySelectorAll("[data-sqlfluff-nav]").forEach(function (header) {
      setMenuState(header, false);
    });
  }

  // Delegated from the document so the contract also holds for controls which
  // a client-rendered application mounts, replaces, or unmounts after load.
  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || typeof target.closest !== "function") return;

    var themeButton = target.closest("[data-sqlfluff-theme-value]");
    if (themeButton) {
      writePreference(themeButton.dataset.sqlfluffThemeValue);
      return;
    }

    var toggle = target.closest("[data-sqlfluff-nav-toggle]");
    if (toggle) {
      var header = toggle.closest("[data-sqlfluff-nav]");
      if (!header) return;
      var menu = header.querySelector("[data-sqlfluff-nav-menu]");
      setMenuState(header, !(menu && menu.classList.contains("is-open")));
      return;
    }

    if (target.closest("[data-sqlfluff-nav-menu] a")) {
      closeMenus();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;

    var open = document.querySelector("[data-sqlfluff-nav-menu].is-open");
    if (!open) return;

    var header = open.closest("[data-sqlfluff-nav]");
    var toggle = header && header.querySelector("[data-sqlfluff-nav-toggle]");
    closeMenus();
    if (toggle) toggle.focus();
  });

  applyPreference(readPreference());

  mediaQuery.addEventListener("change", function () {
    if (readPreference() === "auto") applyPreference("auto");
  });

  window.addEventListener("scroll", queueHeaderScroll, { passive: true });

  // Server-rendered chrome is not in the document while this runs in `head`.
  function syncRenderedChrome() {
    syncControls(readPreference());
    syncHeaderScroll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncRenderedChrome);
  } else {
    syncRenderedChrome();
  }

  window.sqlfluffTheme = {
    /** Current preference: `auto`, `light`, or `dark`. */
    get: function () {
      return readPreference();
    },
    /** Theme the current preference resolves to: `light` or `dark`. */
    resolved: function () {
      return resolveTheme(readPreference());
    },
    /** Store a preference and apply it. Invalid values fall back to `auto`. */
    set: writePreference,
    /** Refresh `aria-pressed` after an application renders its own controls. */
    sync: function () {
      syncControls(readPreference());
    },
    /**
     * Observe preference changes. The listener is called immediately with the
     * current state, then on every change. Returns an unsubscribe function.
     */
    subscribe: function (listener) {
      subscribers.push(listener);
      listener(readPreference(), resolveTheme(readPreference()));

      return function () {
        var index = subscribers.indexOf(listener);
        if (index >= 0) subscribers.splice(index, 1);
      };
    }
  };
})();
