var cookieconsent = (function (e) {
  var t = {};
  function i(n) {
    if (t[n]) return t[n].exports;
    var o = (t[n] = { i: n, l: !1, exports: {} });
    return e[n].call(o.exports, o, o.exports, i), (o.l = !0), o.exports;
  }
  return (
    (i.m = e),
    (i.c = t),
    (i.d = function (e, t, n) {
      i.o(e, t) || Object.defineProperty(e, t, { enumerable: !0, get: n });
    }),
    (i.r = function (e) {
      "undefined" != typeof Symbol &&
        Symbol.toStringTag &&
        Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }),
        Object.defineProperty(e, "__esModule", { value: !0 });
    }),
    (i.t = function (e, t) {
      if ((1 & t && (e = i(e)), 8 & t)) return e;
      if (4 & t && "object" == typeof e && e && e.__esModule) return e;
      var n = Object.create(null);
      if (
        (i.r(n),
        Object.defineProperty(n, "default", { enumerable: !0, value: e }),
        2 & t && "string" != typeof e)
      )
        for (var o in e)
          i.d(
            n,
            o,
            function (t) {
              return e[t];
            }.bind(null, o)
          );
      return n;
    }),
    (i.n = function (e) {
      var t =
        e && e.__esModule
          ? function () {
              return e.default;
            }
          : function () {
              return e;
            };
      return i.d(t, "a", t), t;
    }),
    (i.o = function (e, t) {
      return Object.prototype.hasOwnProperty.call(e, t);
    }),
    (i.p = ""),
    i((i.s = 51))
  );
})([
  function (e, t, i) {
    "use strict";
    e.exports = function (e) {
      var t = [];
      return (
        (t.toString = function () {
          return this.map(function (t) {
            var i = (function (e, t) {
              var i = e[1] || "",
                n = e[3];
              if (!n) return i;
              if (t && "function" == typeof btoa) {
                var o =
                    ((r = n),
                    "/*# sourceMappingURL=data:application/json;charset=utf-8;base64," +
                      btoa(unescape(encodeURIComponent(JSON.stringify(r)))) +
                      " */"),
                  a = n.sources.map(function (e) {
                    return "/*# sourceURL=" + n.sourceRoot + e + " */";
                  });
                return [i].concat(a).concat([o]).join("\n");
              }
              var r;
              return [i].join("\n");
            })(t, e);
            return t[2] ? "@media " + t[2] + "{" + i + "}" : i;
          }).join("");
        }),
        (t.i = function (e, i) {
          "string" == typeof e && (e = [[null, e, ""]]);
          for (var n = {}, o = 0; o < this.length; o++) {
            var a = this[o][0];
            null != a && (n[a] = !0);
          }
          for (o = 0; o < e.length; o++) {
            var r = e[o];
            (null != r[0] && n[r[0]]) ||
              (i && !r[2]
                ? (r[2] = i)
                : i && (r[2] = "(" + r[2] + ") and (" + i + ")"),
              t.push(r));
          }
        }),
        t
      );
    };
  },
  function (e, t, i) {
    var n,
      o,
      a = {},
      r =
        ((n = function () {
          return window && document && document.all && !window.atob;
        }),
        function () {
          return void 0 === o && (o = n.apply(this, arguments)), o;
        }),
      s = function (e, t) {
        return t ? t.querySelector(e) : document.querySelector(e);
      },
      c = (function (e) {
        var t = {};
        return function (e, i) {
          if ("function" == typeof e) return e();
          if (void 0 === t[e]) {
            var n = s.call(this, e, i);
            if (
              window.HTMLIFrameElement &&
              n instanceof window.HTMLIFrameElement
            )
              try {
                n = n.contentDocument.head;
              } catch (e) {
                n = null;
              }
            t[e] = n;
          }
          return t[e];
        };
      })(),
      l = null,
      p = 0,
      d = [],
      u = i(38);
    function m(e, t) {
      for (var i = 0; i < e.length; i++) {
        var n = e[i],
          o = a[n.id];
        if (o) {
          o.refs++;
          for (var r = 0; r < o.parts.length; r++) o.parts[r](n.parts[r]);
          for (; r < n.parts.length; r++) o.parts.push(h(n.parts[r], t));
        } else {
          var s = [];
          for (r = 0; r < n.parts.length; r++) s.push(h(n.parts[r], t));
          a[n.id] = { id: n.id, refs: 1, parts: s };
        }
      }
    }
    function _(e, t) {
      for (var i = [], n = {}, o = 0; o < e.length; o++) {
        var a = e[o],
          r = t.base ? a[0] + t.base : a[0],
          s = { css: a[1], media: a[2], sourceMap: a[3] };
        n[r] ? n[r].parts.push(s) : i.push((n[r] = { id: r, parts: [s] }));
      }
      return i;
    }
    function k(e, t) {
      var i = c(e.insertInto);
      if (!i)
        throw new Error(
          "Couldn't find a style target. This probably means that the value for the 'insertInto' parameter is invalid."
        );
      var n = d[d.length - 1];
      if ("top" === e.insertAt)
        n
          ? n.nextSibling
            ? i.insertBefore(t, n.nextSibling)
            : i.appendChild(t)
          : i.insertBefore(t, i.firstChild),
          d.push(t);
      else if ("bottom" === e.insertAt) i.appendChild(t);
      else {
        if ("object" != typeof e.insertAt || !e.insertAt.before)
          throw new Error(
            "[Style Loader]\n\n Invalid value for parameter 'insertAt' ('options.insertAt') found.\n Must be 'top', 'bottom', or Object.\n (https://github.com/webpack-contrib/style-loader#insertat)\n"
          );
        var o = c(e.insertAt.before, i);
        i.insertBefore(t, o);
      }
    }
    function v(e) {
      if (null === e.parentNode) return !1;
      e.parentNode.removeChild(e);
      var t = d.indexOf(e);
      t >= 0 && d.splice(t, 1);
    }
    function f(e) {
      var t = document.createElement("style");
      if (
        (void 0 === e.attrs.type && (e.attrs.type = "text/css"),
        void 0 === e.attrs.nonce)
      ) {
        var n = (function () {
          0;
          return i.nc;
        })();
        n && (e.attrs.nonce = n);
      }
      return b(t, e.attrs), k(e, t), t;
    }
    function b(e, t) {
      Object.keys(t).forEach(function (i) {
        e.setAttribute(i, t[i]);
      });
    }
    function h(e, t) {
      var i, n, o, a;
      if (t.transform && e.css) {
        if (
          !(a =
            "function" == typeof t.transform
              ? t.transform(e.css)
              : t.transform.default(e.css))
        )
          return function () {};
        e.css = a;
      }
      if (t.singleton) {
        var r = p++;
        (i = l || (l = f(t))),
          (n = x.bind(null, i, r, !1)),
          (o = x.bind(null, i, r, !0));
      } else
        e.sourceMap &&
        "function" == typeof URL &&
        "function" == typeof URL.createObjectURL &&
        "function" == typeof URL.revokeObjectURL &&
        "function" == typeof Blob &&
        "function" == typeof btoa
          ? ((i = (function (e) {
              var t = document.createElement("link");
              return (
                void 0 === e.attrs.type && (e.attrs.type = "text/css"),
                (e.attrs.rel = "stylesheet"),
                b(t, e.attrs),
                k(e, t),
                t
              );
            })(t)),
            (n = z.bind(null, i, t)),
            (o = function () {
              v(i), i.href && URL.revokeObjectURL(i.href);
            }))
          : ((i = f(t)),
            (n = w.bind(null, i)),
            (o = function () {
              v(i);
            }));
      return (
        n(e),
        function (t) {
          if (t) {
            if (
              t.css === e.css &&
              t.media === e.media &&
              t.sourceMap === e.sourceMap
            )
              return;
            n((e = t));
          } else o();
        }
      );
    }
    e.exports = function (e, t) {
      if ("undefined" != typeof DEBUG && DEBUG && "object" != typeof document)
        throw new Error(
          "The style-loader cannot be used in a non-browser environment"
        );
      ((t = t || {}).attrs = "object" == typeof t.attrs ? t.attrs : {}),
        t.singleton || "boolean" == typeof t.singleton || (t.singleton = r()),
        t.insertInto || (t.insertInto = "head"),
        t.insertAt || (t.insertAt = "bottom");
      var i = _(e, t);
      return (
        m(i, t),
        function (e) {
          for (var n = [], o = 0; o < i.length; o++) {
            var r = i[o];
            (s = a[r.id]).refs--, n.push(s);
          }
          e && m(_(e, t), t);
          for (o = 0; o < n.length; o++) {
            var s;
            if (0 === (s = n[o]).refs) {
              for (var c = 0; c < s.parts.length; c++) s.parts[c]();
              delete a[s.id];
            }
          }
        }
      );
    };
    var g,
      y =
        ((g = []),
        function (e, t) {
          return (g[e] = t), g.filter(Boolean).join("\n");
        });
    function x(e, t, i, n) {
      var o = i ? "" : n.css;
      if (e.styleSheet) e.styleSheet.cssText = y(t, o);
      else {
        var a = document.createTextNode(o),
          r = e.childNodes;
        r[t] && e.removeChild(r[t]),
          r.length ? e.insertBefore(a, r[t]) : e.appendChild(a);
      }
    }
    function w(e, t) {
      var i = t.css,
        n = t.media;
      if ((n && e.setAttribute("media", n), e.styleSheet))
        e.styleSheet.cssText = i;
      else {
        for (; e.firstChild; ) e.removeChild(e.firstChild);
        e.appendChild(document.createTextNode(i));
      }
    }
    function z(e, t, i) {
      var n = i.css,
        o = i.sourceMap,
        a = void 0 === t.convertToAbsoluteUrls && o;
      (t.convertToAbsoluteUrls || a) && (n = u(n)),
        o &&
          (n +=
            "\n/*# sourceMappingURL=data:application/json;base64," +
            btoa(unescape(encodeURIComponent(JSON.stringify(o)))) +
            " */");
      var r = new Blob([n], { type: "text/css" }),
        s = e.href;
      (e.href = URL.createObjectURL(r)), s && URL.revokeObjectURL(s);
    }
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Active","always_active":"Always active","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactive","nb_agree":"I agree","nb_changep":"Change my preferences","nb_ok":"OK","nb_reject":"I decline","nb_text":"We use cookies and other tracking technologies to improve your browsing experience on our website, to show you personalized content and targeted ads, to analyze our website traffic, and to understand where our visitors are coming from.","nb_title":"We use cookies","pc_fnct_text_1":"Functionality cookies","pc_fnct_text_2":"These cookies are used to provide you with a more personalized experience on our website and to remember choices you make when you use our website.","pc_fnct_text_3":"For example, we may use functionality cookies to remember your language preferences or remember your login details.","pc_minfo_text_1":"More information","pc_minfo_text_2":"For any queries in relation to our policy on cookies and your choices, please contact us.","pc_minfo_text_3":"To find out more, please visit our <a href=\'%s\' target=\'_blank\'>Privacy Policy</a>.","pc_save":"Save my preferences","pc_sncssr_text_1":"Strictly necessary cookies","pc_sncssr_text_2":"These cookies are essential to provide you with services available through our website and to enable you to use certain features of our website.","pc_sncssr_text_3":"Without these cookies, we cannot provide you certain services on our website.","pc_title":"Cookies Preferences Center","pc_trck_text_1":"Tracking cookies","pc_trck_text_2":"These cookies are used to collect information to analyze the traffic to our website and how visitors are using our website.","pc_trck_text_3":"For example, these cookies may track things such as how long you spend on the website or the pages you visit which helps us to understand how we can improve our website for you.","pc_trck_text_4":"The information collected through these tracking and performance cookies do not identify any individual visitor.","pc_trgt_text_1":"Targeting and advertising cookies","pc_trgt_text_2":"These cookies are used to show advertising that is likely to be of interest to you based on your browsing habits.","pc_trgt_text_3":"These cookies, as served by our content and/or advertising providers, may combine information they collected from our website with other information they have independently collected relating to your web browser\'s activities across their network of websites.","pc_trgt_text_4":"If you choose to remove or disable these targeting or advertising cookies, you will still see adverts but they may not be relevant to you.","pc_yprivacy_text_1":"Your privacy is important to us","pc_yprivacy_text_2":"Cookies are very small text files that are stored on your computer when you visit a website. We use cookies for a variety of purposes and to enhance your online experience on our website (for example, to remember your account login details).","pc_yprivacy_text_3":"You can change your preferences and decline certain types of cookies to be stored on your computer while browsing our website. You can also remove any cookies already stored on your computer, but keep in mind that deleting cookies may prevent you from using parts of our website.","pc_yprivacy_title":"Your privacy","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privacy Policy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Active","always_active":"Always active","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactive","nb_agree":"I agree","nb_changep":"Change my preferences","nb_ok":"OK","nb_reject":"I decline","nb_text":"We use cookies and other tracking technologies to improve your browsing experience on our website, to show you personalised content and targeted ads, to analyse our website traffic, and to understand where our visitors are coming from.","nb_title":"We use cookies","pc_fnct_text_1":"Functionality cookies","pc_fnct_text_2":"These cookies are used to provide you with a more personalised experience on our website and to remember choices you make when you use our website.","pc_fnct_text_3":"For example, we may use functionality cookies to remember your language preferences or remember your login details.","pc_minfo_text_1":"More information","pc_minfo_text_2":"For any queries in relation to our policy on cookies and your choices, please contact us.","pc_minfo_text_3":"To find out more, please visit our <a href=\'%s\' target=\'_blank\'>Privacy Policy</a>.","pc_save":"Save my preferences","pc_sncssr_text_1":"Strictly necessary cookies","pc_sncssr_text_2":"These cookies are essential to provide you with services available through our website and to enable you to use certain features of our website.","pc_sncssr_text_3":"Without these cookies, we cannot provide you certain services on our website.","pc_title":"Cookies Preferences Centre","pc_trck_text_1":"Tracking cookies","pc_trck_text_2":"These cookies are used to collect information to analyse the traffic to our website and how visitors are using our website.","pc_trck_text_3":"For example, these cookies may track things such as how long you spend on the website or the pages you visit which helps us to understand how we can improve our website for you.","pc_trck_text_4":"The information collected through these tracking and performance cookies do not identify any individual visitor.","pc_trgt_text_1":"Targeting and advertising cookies","pc_trgt_text_2":"These cookies are used to show advertising that is likely to be of interest to you based on your browsing habits.","pc_trgt_text_3":"These cookies, as served by our content and/or advertising providers, may combine information they collected from our website with other information they have independently collected relating to your web browser\'s activities across their network of websites.","pc_trgt_text_4":"If you choose to remove or disable these targeting or advertising cookies, you will still see adverts but they may not be relevant to you.","pc_yprivacy_text_1":"Your privacy is important to us","pc_yprivacy_text_2":"Cookies are very small text files that are stored on your computer when you visit a website. We use cookies for a variety of purposes and to enhance your online experience on our website (for example, to remember your account login details).","pc_yprivacy_text_3":"You can change your preferences and decline certain types of cookies to be stored on your computer while browsing our website. You can also remove any cookies already stored on your computer, but keep in mind that deleting cookies may prevent you from using parts of our website.","pc_yprivacy_title":"Your privacy","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privacy Policy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktiv","always_active":"Immer aktiv","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inaktiv","nb_agree":"Alle akzeptieren","nb_changep":"Einstellungen ändern","nb_ok":"OK","nb_reject":"Ich lehne ab","nb_text":"Diese Website verwendet Cookies und Targeting Technologien, um Ihnen ein besseres Internet-Erlebnis zu ermöglichen und die Werbung, die Sie sehen, besser an Ihre Bedürfnisse anzupassen. Diese Technologien nutzen wir außerdem, um Ergebnisse zu messen, um zu verstehen, woher unsere Besucher kommen oder um unsere Website weiter zu entwickeln.","nb_title":"Ihre Privatsphäre ist uns wichtig","pc_fnct_text_1":"Funktions Cookies","pc_fnct_text_2":"Diese Cookies werden verwendet, um Ihnen ein persönlicheres Erlebnis auf unserer Website zu ermöglichen und um sich an Ihre Entscheidungen zu erinnern, die Sie bei der Nutzung unserer Website getroffen haben.","pc_fnct_text_3":"Beispielsweise können wir Funktions-Cookies verwenden, um Ihre Spracheinstellungen oder Ihre Anmeldedaten zu speichern.","pc_minfo_text_1":"Mehr Informationen","pc_minfo_text_2":"Bei Fragen in Bezug auf unseren Umgang mit Cookies und Ihrer Privatsphäre kontaktieren Sie uns bitte.","pc_minfo_text_3":"Details finden Sie in unserer <a href=\'%s\' target=\'_blank\'>Datenschutzrichtlinie</a>.","pc_save":"Einstellungen speichern","pc_sncssr_text_1":"Technisch notwendige Cookies","pc_sncssr_text_2":"Diese Cookies sind für die Bereitstellung von Diensten, die über unsere Website verfügbar sind, und für die Verwendung bestimmter Funktionen unserer Website von wesentlicher Bedeutung.","pc_sncssr_text_3":"Ohne diese Cookies können wir Ihnen bestimmte Dienste auf unserer Website nicht zur Verfügung stellen.","pc_title":"Cookie Einstellungen","pc_trck_text_1":"Tracking und Performance Cookies","pc_trck_text_2":"Diese Cookies werden zum Sammeln von Informationen verwendet, um den Verkehr auf unserer Website und die Nutzung unserer Website durch Besucher zu analysieren.","pc_trck_text_3":"Diese Cookies können beispielsweise nachverfolgen, wie lange Sie auf der Website verweilen oder welche Seiten Sie besuchen. So können wir verstehen, wie wir unsere Website für Sie verbessern können.","pc_trck_text_4":"Die durch diese Tracking- und Performance-Cookies gesammelten Informationen identifizieren keinen einzelnen Besucher.","pc_trgt_text_1":"Targeting und Werbung Cookies","pc_trgt_text_2":"Diese Cookies werden genutzt, um Werbung anzuzeigen, die Sie aufgrund Ihrer Surfgewohnheiten wahrscheinlich interessieren wird.","pc_trgt_text_3":"Diese Cookies, die von unseren Inhalten und / oder Werbeanbietern bereitgestellt werden, können Informationen, die sie von unserer Website gesammelt haben, mit anderen Informationen kombinieren, welche sie durch Aktivitäten Ihres Webbrowsers in Ihrem Netzwerk von Websites gesammelt haben.","pc_trgt_text_4":"Wenn Sie diese Targeting- oder Werbe-Cookies entfernen oder deaktivieren, werden weiterhin Anzeigen angezeigt. Diese sind für Sie jedoch möglicherweise nicht relevant.","pc_yprivacy_text_1":"Ihre Privatsphäre ist uns wichtig","pc_yprivacy_text_2":"Cookies sind sehr kleine Textdateien, die auf Ihrem Rechner gespeichert werden, wenn Sie eine Website besuchen. Wir verwenden Cookies für eine Reihe von Auswertungen, um damit Ihren Besuch auf unserer Website kontinuierlich verbessern zu können (z. B. damit Ihnen Ihre Login-Daten erhalten bleiben).","pc_yprivacy_text_3":"Sie können Ihre Einstellungen ändern und verschiedenen Arten von Cookies erlauben, auf Ihrem Rechner gespeichert zu werden, während Sie unsere Webseite besuchen. Sie können auf Ihrem Rechner gespeicherte Cookies ebenso weitgehend wieder entfernen. Bitte bedenken Sie aber, dass dadurch Teile unserer Website möglicherweise nicht mehr in der gedachten Art und Weise nutzbar sind.","pc_yprivacy_title":"Ihre Privatsphäre","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Datenschutzrichtlinie</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Actif","always_active":"Toujours activé","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactif","nb_agree":"J\'accepte","nb_changep":"Changer mes préférences","nb_ok":"OK","nb_reject":"Je refuse","nb_text":"Nous utilisons des cookies et d\'autres technologies de suivi pour améliorer votre expérience de navigation sur notre site, pour vous montrer un contenu personnalisé et des publicités ciblées, pour analyser le trafic de notre site et pour comprendre la provenance de nos visiteurs.","nb_title":"Nous utilisons des cookies","pc_fnct_text_1":"Cookies de Fonctionnalité","pc_fnct_text_2":"Ces cookies servent à vous offrir une expérience plus personnalisée sur notre site Web et à mémoriser les choix que vous faites lorsque vous utilisez notre site Web.","pc_fnct_text_3":"Par exemple, nous pouvons utiliser des cookies de fonctionnalité pour mémoriser vos préférences de langue ou vos identifiants de connexion.","pc_minfo_text_1":"Plus d\'information","pc_minfo_text_2":"Pour toute question relative à notre politique en matière de cookies et à vos choix, veuillez nous contacter.","pc_minfo_text_3":"Pour en savoir plus, merci de consulter notre <a href=\'%s\' target=\'_blank\'>Politique de confidentialité</a>.","pc_save":"Sauvegarder mes préférences","pc_sncssr_text_1":"Cookies strictement nécessaires","pc_sncssr_text_2":"Ces cookies sont essentiels pour vous fournir les services disponibles sur notre site Web et vous permettre d’utiliser certaines fonctionnalités de notre site Web.","pc_sncssr_text_3":"Sans ces cookies, nous ne pouvons pas vous fournir certains services sur notre site Web.","pc_title":"Espace de Préférences des Cookies","pc_trck_text_1":"Cookies de suivi et de performance","pc_trck_text_2":"Ces cookies sont utilisés pour collecter des informations permettant d\'analyser le trafic sur notre site et la manière dont les visiteurs utilisent notre site.","pc_trck_text_3":"Par exemple, ces cookies peuvent suivre des choses telles que le temps que vous passez sur le site Web ou les pages que vous visitez, ce qui nous aide à comprendre comment nous pouvons améliorer notre site Web pour vous.","pc_trck_text_4":"Les informations collectées via ces cookies de suivi et de performance n\' identifient aucun visiteur en particulier.","pc_trgt_text_1":"Cookies de ciblage et de publicité","pc_trgt_text_2":"Ces cookies sont utilisés pour afficher des publicités susceptibles de vous intéresser en fonction de vos habitudes de navigation.","pc_trgt_text_3":"Ces cookies, tels que servis par nos fournisseurs de contenu et / ou de publicité, peuvent associer des informations qu\'ils ont collectées sur notre site Web à d\'autres informations qu\'ils ont collectées de manière indépendante et concernant les activités du votre navigateur Web sur son réseau de sites Web.","pc_trgt_text_4":"Si vous choisissez de supprimer ou de désactiver ces cookies de ciblage ou de publicité, vous verrez toujours des annonces, mais elles risquent de ne pas être pertinentes.","pc_yprivacy_text_1":"Votre confidentialité est importante pour nous","pc_yprivacy_text_2":"Les cookies sont de très petits fichiers texte qui sont stockés sur votre ordinateur lorsque vous visitez un site Web. Nous utilisons des cookies à diverses fins et pour améliorer votre expérience en ligne sur notre site Web (par exemple, pour mémoriser les informations de connexion de votre compte).","pc_yprivacy_text_3":"Vous pouvez modifier vos préférences et refuser l\'enregistrement de certains types de cookies sur votre ordinateur lors de la navigation sur notre site. Vous pouvez également supprimer les cookies déjà stockés sur votre ordinateur, mais gardez à l\'esprit que leur suppression peut vous empêcher d\'utiliser des éléments de notre site Web.","pc_yprivacy_title":"Votre confidentialité","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Politique de confidentialité</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Activo","always_active":"Siempre activo","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactivo","nb_agree":"Aceptar","nb_changep":"Configurar","nb_ok":"OK","nb_reject":"Renuncio","nb_text":"Usamos cookies y otras técnicas de rastreo para mejorar tu experiencia de navegación en nuestra web, para mostrarte contenidos personalizados y anuncios adecuados, para analizar el tráfico en nuestra web y para comprender de donde llegan nuestros visitantes.","nb_title":"Utilizamos cookies","pc_fnct_text_1":"Cookies de funcionalidad","pc_fnct_text_2":"Estas cookies son utilizadas para proveerte una experiencia más personalizada y recordar tus elecciones en nuestra web.","pc_fnct_text_3":"Por ejemplo, podemos utilizar cookies de funcionalidad para recordar tus preferencias de idioma o tus detalles de acceso.","pc_minfo_text_1":"Más información","pc_minfo_text_2":"Para cualquier pregunta en relación con nuestra política de cookies y tus preferencias, contacta con nosotros, por favor.","pc_minfo_text_3":"Para saber más, visita nuestra página sobre la <a href=\'%s\' target=\'_blank\'>Política de privacidad</a>.","pc_save":"Guardar mis preferencias","pc_sncssr_text_1":"Cookies estrictamente necesarias","pc_sncssr_text_2":"Estos cookies son esenciales para proveerte los servicios disponibles en nuestra web y para permitirte utilizar algunas características de nuestra web.","pc_sncssr_text_3":"Sin estas cookies, no podemos proveer algunos servicios de nuestro sitio web.","pc_title":"Centro de Preferencias de Cookies","pc_trck_text_1":"Cookies de rastreo y rendimiento","pc_trck_text_2":"Estas cookies son utilizadas para recopilar información, para analizar el tráfico y la forma en que los usuarios utilizan nuestra web.","pc_trck_text_3":"Por ejemplo, estas cookies pueden recopilar datos como cuánto tiempo llevas navegado en nuestro sitio web o qué páginas visitas, cosa que nos ayuda a comprender cómo podemos mejorar nuestra web para ti.","pc_trck_text_4":"La información recopilada con estas cookies de rastreo y rendimiento no identifican a ningún visitante individual.","pc_trgt_text_1":"Cookies de seguimiento y publicidad","pc_trgt_text_2":"Estas cookies son utilizadas para enseñarte anuncios que pueden ser interesantes basados en tus costumbres de navegación.","pc_trgt_text_3":"Estas cookies, servidas por nuestros proveedores de contenido y/o de publicidad, pueden combinar la información que ellos recogieron de nuestro sitio web con otra información recopilada por ellos en relación con las actividades de su navegador a través de su red de sitios web.","pc_trgt_text_4":"Si eliges cancelar o inhabilitar las cookies de seguimiento y publicidad, seguirás viendo anuncios pero estos podrían no ser de tu interés.","pc_yprivacy_text_1":"Tu privacidad es importante para nosotros","pc_yprivacy_text_2":"Las cookies son pequeños archivos de texto que se almacenan en tu navegador cuando visitas nuestra web. Utilizamos cookies para diferentes objetivos y para mejorar tu experiencia en nuestro sitio web (por ejemplo, para recordar tus detalles de acceso).","pc_yprivacy_text_3":"Puedes cambiar tus preferencias y rechazar que algunos tipos de cookies sean almacenados mientras estás navegando en nuestra web. También puedes cancelar cualquier cookie ya almacenada en tu navegador, pero recuerda que cancelar las cookies puede impedirte utilizar algunas partes de nuestra web.","pc_yprivacy_title":"Tu privacidad","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Política de privacidad</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Actiu","always_active":"Sempre actiu","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactiu","nb_agree":"Estic d’acord","nb_changep":"Canviar preferències","nb_ok":"OK","nb_reject":"Declino","nb_text":"Fem servir cookies i altres tecnologies de seguiment per millorar la teva experiència de navegació al nostre lloc web, per mostrar-te contingut personalitzat i anuncis interessants per a tu, per analitzar el nostre tràfic i entendre d’on venen els nostres visitants.","nb_title":"Fem servir cookies","pc_fnct_text_1":"Cookies de funcionalitat","pc_fnct_text_2":"Aquestes cookies ens permeten oferir-vos una experiència personalitzada i recordar la vostra configuració quan feu servir el nostre lloc web.","pc_fnct_text_3":"Per exemple, podem fer servir funcionalitat per recordar el vostre idioma o les vostres credencials.","pc_minfo_text_1":"Més informació","pc_minfo_text_2":"Per qualsevol pregunta relacionada amb la nostra política de cookies i les vostres opcions, si us plau contacti’ns.","pc_minfo_text_3":"Per saber més, si us plau visiti la nostra <a href=\'%s\' target=\'_blank\'>Política de privacitat</a>.","pc_save":"Guarda les meves preferències","pc_sncssr_text_1":"Cookies estrictament necessàries","pc_sncssr_text_2":"Aquestes cookies són essencials per oferir-vos el nostres serveis i funcionalitats al nostre lloc web.","pc_sncssr_text_3":"Sense aquestes cookies, no us podem oferir alguns serveis.","pc_title":"Centre de Preferències de Cookies","pc_trck_text_1":"Cookies de seguiment i rendiment","pc_trck_text_2":"Aquestes cookies es fan servir per recollir informació, analitzar el tràfic i veure com es fa servir el nostre lloc web.","pc_trck_text_3":"Per exemple, aquestes cookies podrien fer el seguiment de quant de temps visiteu el nostre web o quines pàgines visiteu les quals ens poden ajudar a entendre com millorar el lloc web per vosaltres.","pc_trck_text_4":"La informació recollida gràcies a aquestes cookies de seguiment i rendiment no us identifiquen de forma individual.","pc_trgt_text_1":"Cookies de publicitat i focalització","pc_trgt_text_2":"Aquestes cookies es fan servir per mostrar anuncis que poden ser del vostre interès basats en els vostres hàbits d’us.","pc_trgt_text_3":"Aquestes cookies, servides tal i com ho fan els nostres proveïdors de publicitat i contingut, poden combinar informació recollida al nostre lloc web amb altra informació que hagin recollit independentment relacionada amb activitat a la seva xarxa de llocs web.","pc_trgt_text_4":"Si vostè decideix eliminar o deshabilitat aquestes cookies, encara veurà publicitat però aquesta pot no ser rellevant per vostè.","pc_yprivacy_text_1":"La vostra privacitat és important per nosaltres","pc_yprivacy_text_2":"Les cookies són uns arxius de text molt petits que es guarden al vostre  ordinador quan visiteu un lloc web. Fem servir cookies per una varietat de finalitats i millorar la vostra experiència al nostre lloc web (per exemple, per recordar les vostres credencials).","pc_yprivacy_text_3":"Pot canviar les vostres preferències i rebutjar l’emmagatzematge al vostre ordinador de certs tipus de cookies mentres navega pel nostre. Pot eliminar qualsevol cookie ja emmagatzemada al vostre ordinador, però tingui en compte que eliminar cookies pot impedir que faci servir parts del nostre lloc web.","pc_yprivacy_title":"La vostra privacitat","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Política de privacitat</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Attivo","always_active":"Sempre attivo","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inattivo","nb_agree":"Accetto","nb_changep":"Cambia le mie impostazioni","nb_ok":"OK","nb_reject":"Rifiuto","nb_text":"Noi usiamo i cookies e altre tecniche di tracciamento per migliorare la tua esperienza di navigazione nel nostro sito, per mostrarti contenuti personalizzati e annunci mirati, per analizzare il traffico sul nostro sito, e per capire da dove arrivano i nostri visitatori.","nb_title":"Noi usiamo i cookies","pc_fnct_text_1":"Cookies funzionali","pc_fnct_text_2":"Questi cookies sono utilizzati per offrirti un’esperienza più personalizzata nel nostro sito e per ricordare le scelte che hai fatto mentre usavi il nostro sito.","pc_fnct_text_3":"Per esempio, possiamo usare cookies funzionali per memorizzare le tue preferenze sulla lingua o i tuoi dettagli di accesso.","pc_minfo_text_1":"Più informazioni","pc_minfo_text_2":"Per qualsiasi domanda relativa alla nostra politica sui cookies e le tue scelte, per favore contattaci.","pc_minfo_text_3":"Per saperne di più, visita per favore la nostra pagina sulla <a href=\'%s\' target=\'_blank\'>Politica sulla riservatezza</a>.","pc_save":"Salva le mie impostazioni","pc_sncssr_text_1":"Cookies strettamente necessari","pc_sncssr_text_2":"Questi cookies sono essenziali per fornirti i servizi disponibili nel nostro sito e per renderti disponibili alcune funzionalità del nostro sito web.","pc_sncssr_text_3":"Senza questi cookies, non possiamo fornirti alcuni servizi del nostro sito.","pc_title":"Centro Preferenze sui Cookies","pc_trck_text_1":"Cookies di tracciamento e prestazione","pc_trck_text_2":"Questi cookies sono utilizzati per raccogliere informazioni per analizzare il traffico verso il nostro sito e il modo in cui i visitatori utilizzano il nostro sito.","pc_trck_text_3":"Per esempio, questi cookies possono tracciare cose come quanto a lungo ti fermi nel nostro sito o le pagine che visiti, cosa che ci aiuta a capire come possiamo migliorare il nostro sito per te.","pc_trck_text_4":"Le informazioni raccolte attraverso questi cookies di tracciamento e performance non identificano alcun visitatore individuale.","pc_trgt_text_1":"Cookies di targeting e pubblicità","pc_trgt_text_2":"Questi cookies sono usati per mostrare annunci pubblicitari che possano verosimilmente essere di tuo interesse in base alle tue abitudini di navigazione.","pc_trgt_text_3":"Questi cookies, cosí come forniti dai nostri fornitori di  contenuti o annunci pubblicitari, possono combinare le informazioni che raccolgono dal nostro sito web con quelle che hanno indipendentemente raccolto in relazione all’attività del tuo browser attraverso la loro rete di siti web.","pc_trgt_text_4":"Se scegli di rimuovere o disabilitare questo tipo di cookies di targeting e pubblicità, vedrai ancora annunci pubblicitari ma potrebbero essere irrilevanti per te.","pc_yprivacy_text_1":"La tua privacy è importante per noi","pc_yprivacy_text_2":"I cookies sono dei piccolissimi file di testo che vengono memorizzati nel tuo computer quando visiti un sito web. Noi usiamo i cookies per una varietà di scopi e per migliorare la tua esperienza online nel nostro sito web (per esempio, per ricordare i tuoi dettagli di accesso).","pc_yprivacy_text_3":"Tu puoi cambiare le tue impostazioni e rifiutare che alcuni tipi di cookies vengano memorizzati sul tuo computer mentre stai navigando nel nostro sito web. Puoi anche rimuovere qualsiasi cookie già memorizzato nel tuo computer, ma ricorda che cancellare i cookies può impedirti di utilizzare alcune parti del nostro sito.","pc_yprivacy_title":"La tua privacy","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Politica sulla riservatezza</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktiv","always_active":"Alltid aktiv","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inaktiv","nb_agree":"Jag accepterar","nb_changep":"Ändra mina inställningar","nb_ok":"OK","nb_reject":"Jag avböjer","nb_text":"Vi använder cookies och andra spårningsteknologier för att förbättra din surfupplevelse på vår webbplats, för att visa dig personligt innehåll och riktade annonser, för att analysera vår webbplatstrafik och för att förstå var våra besökare kommer ifrån.","nb_title":"Vi använder oss av cookies","pc_fnct_text_1":"Funktionella cookies","pc_fnct_text_2":"Dessa cookies används för att ge dig en mer personlig upplevelse på vår webbplats och för att komma ihåg val du gör när du använder vår webbplats.","pc_fnct_text_3":"Vi kan till exempel använda funktions cookies för att komma ihåg dina språkinställningar eller dina inloggningsuppgifter.","pc_minfo_text_1":"Mer information","pc_minfo_text_2":"Kontakta oss om du har frågor angående vår policy om cookies och dina val.","pc_minfo_text_3":"För att ta reda på mer, läs vår <a href=\'%s\' target=\'_blank\'>integritetspolicy</a>.","pc_save":"Spara mina inställningar","pc_sncssr_text_1":"Absolut nödvändiga cookies","pc_sncssr_text_2":"Dessa cookies är viktiga för att förse dig med tjänster som är tillgängliga via vår webbplats och för att du ska kunna använda vissa funktioner på vår webbplats.","pc_sncssr_text_3":"Utan dessa cookies kan vi inte tillhandahålla vissa tjänster på vår webbplats.","pc_title":"Cookies Inställningar","pc_trck_text_1":"Spårnings- och prestanda cookies","pc_trck_text_2":"Dessa cookies används för att samla in information för att analysera trafiken på vår webbplats och hur våra besökare använder den.","pc_trck_text_3":"Dessa cookies kan till exempel spåra hur länge du spenderar på webbplatsen eller vilka sidor du besöker vilket hjälper oss att förstå hur vi kan förbättra vår webbplats för dig.","pc_trck_text_4":"Informationen som samlas in genom dessa spårnings- och prestanda cookies identifierar ingen enskild besökare.","pc_trgt_text_1":"Inriktnings- och reklamcookies","pc_trgt_text_2":"Dessa cookies används för att visa reklam som sannolikt kommer att vara av intresse för dig baserat på dina surfvanor.","pc_trgt_text_3":"Dessa kakor, som betjänas av vårt innehåll och / eller reklamleverantörer, kan kombinera information som de samlat in från vår webbplats med annan information som de har samlat in oberoende om din webbläsares aktiviteter i deras nätverk av webbplatser.","pc_trgt_text_4":"Om du väljer att ta bort eller inaktivera dessa inriktnings- och reklamcookies kommer du fortfarande att se annonser men de kanske inte är relevanta för dig.","pc_yprivacy_text_1":"Din integritet är viktig för oss","pc_yprivacy_text_2":"Cookies är mycket små textfiler som lagras på din dator när du besöker en webbplats. Vi använder cookies till olika ändamål och för att kunna förbättra din onlineupplevelse på vår webbplats (till exempel som att komma ihåg dina inloggningsuppgifter).","pc_yprivacy_text_3":"Du kan ändra dina inställningar och avaktivera vissa typer av cookies som ska lagras på din dator när du surfar på vår webbplats. Du kan också ta bort alla cookies som redan är lagrade på din dator, men kom ihåg att radering av cookies kan hindra dig från att använda delar av vår webbplats.","pc_yprivacy_title":"Din integritet","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Integritetspolicy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Actief","always_active":"Altijd actief","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactief","nb_agree":"Ik ga akkoord","nb_changep":"Wijzig mijn voorkeuren","nb_ok":"OK","nb_reject":"Ik weiger","nb_text":"Wij maken gebruik van cookies en andere tracking-technologieën om uw surfervaring op onze website te verbeteren, om gepersonaliseerde inhoud en advertenties te tonen, om ons websiteverkeer te analyseren en om te begrijpen waar onze bezoekers vandaan komen.","nb_title":"Wij gebruiken cookies","pc_fnct_text_1":"Functionele cookies","pc_fnct_text_2":"Deze cookies worden gebruikt om u een persoonlijkere ervaring op onze website te bieden en om keuzes te onthouden die u maakt wanneer u onze website gebruikt.","pc_fnct_text_3":"Functionele cookies worden bijvoorbeeld gebruikt om uw taalvoorkeuren of inloggegevens te onthouden.","pc_minfo_text_1":"Meer informatie","pc_minfo_text_2":"Voor vragen in verband met ons cookiebeleid en uw keuzes kan u ons contacteren.","pc_minfo_text_3":"Voor meer informatie, bezoek ons <a href=\'%s\' target=\'_blank\'>Privacybeleid</a>.","pc_save":"Sla mijn voorkeuren op","pc_sncssr_text_1":"Strikt noodzakelijke cookies","pc_sncssr_text_2":"Deze cookies zijn essentieel om u de diensten aan te bieden die beschikbaar zijn via onze website en om u in staat te stellen bepaalde functies van onze website te gebruiken.","pc_sncssr_text_3":"Zonder deze cookies kunnen we u bepaalde diensten op onze website niet aanbieden.","pc_title":"Cookie instellingen","pc_trck_text_1":"Tracking- en prestatie cookies","pc_trck_text_2":"Deze cookies worden gebruikt om informatie te verzamelen om het verkeer naar onze website te analyseren en hoe bezoekers onze website gebruiken.","pc_trck_text_3":"Deze cookies kunnen gegevens zoals hoe lang u op de website doorbrengt of de pagina\'s die u bezoekt, bijhouden. Dit helpt ons te begrijpen hoe we onze website voor u kunnen verbeteren.","pc_trck_text_4":"Individuele bezoekers kunnen niet geïdentificeerd worden aan hand van de informatie in deze cookies.","pc_trgt_text_1":"Targeting- en advertentie cookies","pc_trgt_text_2":"Deze cookies worden gebruikt om advertenties weer te geven die u waarschijnlijk interesseren op basis van uw surfgedrag.","pc_trgt_text_3":"Deze cookies, zoals aangeboden op basis van de inhoud van onze site en/of reclame aanbieders, kunnen informatie die ze van onze website hebben verzameld combineren met andere informatie die ze onafhankelijk hebben verzameld met betrekking tot de activiteiten van uw webbrowser via hun netwerk van websites.","pc_trgt_text_4":"Als u ervoor kiest deze targeting- of advertentiecookies te verwijderen of uit te schakelen, ziet u nog steeds advertenties, maar deze zijn mogelijk niet relevant voor u.","pc_yprivacy_text_1":"Uw privacy is belangrijk voor ons","pc_yprivacy_text_2":"Cookies zijn kleine tekstbestanden die bij het bezoeken van een website op uw computer worden opgeslagen. We gebruiken cookies voor verschillende doeleinden en om uw online ervaring op onze website te verbeteren (bijvoorbeeld om de inloggegevens voor uw account te onthouden).","pc_yprivacy_text_3":"U kunt uw voorkeuren wijzigen en bepaalde soorten cookies weigeren die op uw computer worden opgeslagen tijdens het browsen op onze website. U kunt ook alle cookies verwijderen die al op uw computer zijn opgeslagen, maar houd er rekening mee dat het verwijderen van cookies ertoe kan leiden dat u delen van onze website niet kunt gebruiken.","pc_yprivacy_title":"Jouw privacy","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privacybeleid</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Ativo","always_active":"Sempre ativo","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inativo","nb_agree":"Concordo","nb_changep":"Alterar as minhas preferências","nb_ok":"OK","nb_reject":"Eu recuso","nb_text":"Utilizamos cookies e outras tecnologias de medição para melhorar a sua experiência de navegação no nosso site, de forma a mostrar conteúdo personalizado, anúncios direcionados, analisar o tráfego do site e entender de onde vêm os visitantes.","nb_title":"O nosso site usa cookies","pc_fnct_text_1":"Cookies de funcionalidade","pc_fnct_text_2":"Estes cookies são usados ​​para fornecer uma experiência mais personalizada no nosso site e para lembrar as escolhas que faz ao usar o nosso site.","pc_fnct_text_3":"Por exemplo, podemos usar cookies de funcionalidade para se lembrar das suas preferências de idioma e/ ou os seus detalhes de login.","pc_minfo_text_1":"Mais Informações","pc_minfo_text_2":"Para qualquer dúvida sobre a nossa política de cookies e as suas opções, entre em contato connosco.","pc_minfo_text_3":"Para obter mais detalhes, por favor consulte a nossa <a href=\'%s\' target=\'_blank\'>Política de Privacidade</a>.","pc_save":"Guardar as minhas preferências","pc_sncssr_text_1":"Cookies estritamente necessários","pc_sncssr_text_2":"Estes cookies são essenciais para fornecer serviços disponíveis no nosso site e permitir que possa usar determinados recursos no nosso site.","pc_sncssr_text_3":"Sem estes cookies, não podemos fornecer certos serviços no nosso site.","pc_title":"Centro de preferências de cookies","pc_trck_text_1":"Cookies de medição e desempenho","pc_trck_text_2":"Estes cookies são usados ​​para coletar informações para analisar o tráfego no nosso site e entender como é que os visitantes estão a usar o nosso site.","pc_trck_text_3":"Por exemplo, estes cookies podem medir fatores como o tempo despendido no site ou as páginas visitadas, isto vai permitir entender como podemos melhorar o nosso site para os utilizadores.","pc_trck_text_4":"As informações coletadas por meio destes cookies de medição e desempenho não identificam nenhum visitante individual.","pc_trgt_text_1":"Cookies de segmentação e publicidade","pc_trgt_text_2":"Estes cookies são usados ​​para mostrar publicidade que provavelmente lhe pode interessar com base nos seus hábitos e comportamentos de navegação.","pc_trgt_text_3":"Estes cookies, servidos pelo nosso conteúdo e/ ou fornecedores de publicidade, podem combinar as informações coletadas no nosso site com outras informações coletadas independentemente relacionadas com as atividades na rede de sites do seu navegador.","pc_trgt_text_4":"Se optar por remover ou desativar estes cookies de segmentação ou publicidade, ainda verá anúncios, mas estes poderão não ser relevantes para si.","pc_yprivacy_text_1":"A sua privacidade é importante para nós","pc_yprivacy_text_2":"Cookies são pequenos arquivos de texto que são armazenados no seu computador quando visita um site. Utilizamos cookies para diversos fins e para aprimorar sua experiência no nosso site (por exemplo, para se lembrar dos detalhes de login da sua conta).","pc_yprivacy_text_3":"Pode alterar as suas preferências e recusar o armazenamento de certos tipos de cookies no seu computador enquanto navega no nosso site. Pode também remover todos os cookies já armazenados no seu computador, mas lembre-se de que a exclusão de cookies pode impedir o uso de determinadas áreas no nosso site.","pc_yprivacy_title":"A sua privacidade","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Política de Privacidade</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Päällä","always_active":"Aina päällä","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Pois päältä","nb_agree":"Hyväksyn","nb_changep":"Muuta asetuksiani","nb_ok":"OK","nb_reject":"Kieltäydyn","nb_text":"Käytämme evästeitä ja muita seurantateknologioita parantaaksemme käyttäjäkokemusta verkkosivustollamme, näyttääksemme sinulle personoituja sisältöjä ja mainoksia, analysoidaksemme verkkoliikennettä sekä lisätäksemme ymmärrystämme käyttäjiemme sijainnista.","nb_title":"Käytämme evästeitä","pc_fnct_text_1":"Toiminnallisuusevästeet","pc_fnct_text_2":"Näitä evästeitä käytetään personoidumman käyttäjäkokemuksen luomiseksi sekä valintojesi tallentamiseksi sivustollamme.","pc_fnct_text_3":"Esim. voimme käyttää toiminnallisuusevästeitä muistaaksemme kielivalintasi sekä kirjautumistietosi.","pc_minfo_text_1":"Lisätietoa","pc_minfo_text_2":"Evästeisiin liittyvissä kysymyksissä ole hyvä ja ota meihin yhteyttä.","pc_minfo_text_3":"Lue lisää <a href=\'%s\' target=\'_blank\'>Tietosuojakäytäntö</a>.","pc_save":"Tallenna asetukseni","pc_sncssr_text_1":"Tärkeät evästeet","pc_sncssr_text_2":"Nämä evästeet mahdollistavat verkkosivustomme palveluiden sekä tiettyjen ominaisuuksien käyttämisen.","pc_sncssr_text_3":"Ilman näitä evästeitä emme voi tarjota sinulle tiettyjä palveluita sivustollamme.","pc_title":"Evästeasetukset","pc_trck_text_1":"Seuranta- ja tehokkuusevästeet","pc_trck_text_2":"Näiden evästeiden avulla kerätään tietoa sivustomme liikenteestä sekä käyttötavoista.","pc_trck_text_3":"Esim. nämä evästeet voivat seurata sitä, paljonko aikaa vietät sivustollamme, mikä auttaa meitä parantamaan sivustomme käyttökokemusta jatkossa.","pc_trck_text_4":"Näiden evästeiden avulla kerätty tietoa ei voida yhdistää yksittäiseen käyttäjään.","pc_trgt_text_1":"Kohdennus- ja mainosevästeet","pc_trgt_text_2":"Näitä evästeitä käytetään näyttämään mainoksia, jotka selauskäytöksesi perusteella todennäköisesti kiinnostavat sinua.","pc_trgt_text_3":"Nämä sisältö- ja/tai mainoskumppanimme tarjoamat evästeet voivat yhdistää sivustoltamme kerättyä tietoa muilta heidän verkostoonsa kuuluvilta sivustoilta kerättyihin tietoihin.","pc_trgt_text_4":"Jos päätät poistaa tai kytkeä pois päältä nämä kohdennus- ja mainosevästeet, näet yhä mainoksia, mutta ne eivät välttämättä ole sinulle oleellisia.","pc_yprivacy_text_1":"Yksityisyytesi on meille tärkeää","pc_yprivacy_text_2":"Evästeet ovat pieniä tekstitiedostoja, jotka tallennetaan laitteeseesi verkkosivulla vieraillessasi. Käytämme evästeitä useaan tarkoitukseen ja parantaaksesi käyttökokemustasi verkkosivustollamme (esim. muistaaksemme kirjautumistietosi).","pc_yprivacy_text_3":"Voit muuttaa asetuksiasi ja kieltää sivustoltamme tiettyjen evästetyyppien tallentamisen laitteellesi. Voit myös poistaa minkä tahansa jo tallennetun evästeen laitteeltasi, mutta huomaathan, että evästeiden poistaminen saattaa estää sinua käyttämästä osaa sivustomme sisällöstä.","pc_yprivacy_title":"Yksityisyytesi","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Tietosuojakäytäntö</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktív","always_active":"Mindig aktív","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inaktív","nb_agree":"Elfogadom","nb_changep":"Beállítások megváltoztatása","nb_ok":"OK","nb_reject":"Elutasítom","nb_text":"Az oldal sütiket és egyéb nyomkövető technológiákat alkalmaz, hogy javítsa a böngészési élményét, azzal hogy személyre szabott tartalmakat és célzott hirdetéseket jelenít meg, és elemzi a weboldalunk forgalmát, hogy megtudjuk honnan érkeztek a látogatóink.","nb_title":"Az oldal sütiket használ","pc_fnct_text_1":"Funkcionális sütik","pc_fnct_text_2":"Ezeket a sütiket arra használjuk, hogy személyre szabottabb élményt nyújtsunk weboldalunkon, és hogy az oldal rögzítse a webhelyünk használata során tett döntéseket.","pc_fnct_text_3":"Például arra használhatunk funkcionális sütiket, hogy emlékezzünk a nyelvi beállításokra, vagy a bejelentkezési adataira.","pc_minfo_text_1":"Egyéb információk","pc_minfo_text_2":"A sütikre vonatkozó irányelveinkkel és az Ön választásával kapcsolatosan felmerülő bármilyen kérdésével keressen meg bennünket.","pc_minfo_text_3":"Ha többet szeretne megtudni, kérjük, keresse fel a <a href=\'%s\' target=\'_blank\'>Adatvédelmi irányelvek</a>.","pc_save":"Beállítások mentése","pc_sncssr_text_1":"Feltétlenül szükséges sütik","pc_sncssr_text_2":"Ezek a sütik elengedhetetlenek a weboldalunkon elérhető szolgáltatások nyújtásához, valamint weboldalunk bizonyos funkcióinak használatához.","pc_sncssr_text_3":"A feltétlenül szükséges sütik használata nélkül weboldalunkon nem tudunk bizonyos szolgáltatásokat nyújtani Önnek.","pc_title":"Sütikre beállítási központ","pc_trck_text_1":"Követési és teljesítménnyel kapcsolatos sütik","pc_trck_text_2":"Ezeket a sütiket arra használjuk, hogy információkat gyűjtsünk weboldalunk forgalmáról és látogatóiról, webhelyünk használatának elemzéséhez.","pc_trck_text_3":"Például ezek a sütik nyomon követhetik a webhelyen töltött időt vagy a meglátogatott oldalakat, amely segít megérteni, hogyan javíthatjuk webhelyünket az Ön nagyobb megelégedettségére.","pc_trck_text_4":"Ezekkel a nyomkövető és teljesítménnyel kapcsolatos sütikkel összegyűjtött információk egyetlen személyt sem azonosítanak.","pc_trgt_text_1":"Célirányos és hirdetési sütik","pc_trgt_text_2":"Ezeket a sütiket olyan hirdetések megjelenítésére használjuk, amelyek valószínűleg érdekli Önt a böngészési szokásai alapján.","pc_trgt_text_3":"Ezek a sütik, amelyeket a tartalom és / vagy a reklámszolgáltatók szolgáltatnak, egyesíthetik a weboldalunktól gyűjtött információkat más információkkal, amelyeket önállóan összegyűjtöttek az Ön böngészőjének tevékenységeivel kapcsolatban a webhely-hálózaton keresztül.","pc_trgt_text_4":"Ha Ön úgy dönt, hogy eltávolítja vagy letiltja ezeket a célirányos vagy hirdetési sütiket, akkor is látni fogja a hirdetéseket, de lehet, hogy nem lesznek relevánsak az Ön számára.","pc_yprivacy_text_1":"Az ön adatainak védelem fontos számunkra","pc_yprivacy_text_2":"A sütik egészen kicsi szöveges fájlok, amelyeket a számítógépén tárolnak, amikor meglátogat egy weboldalt. Sütiket használunk különféle célokra, és weboldalunkon az online élmény fokozása érdekében (például a fiókjának bejelentkezési adatainak megjegyzésére).","pc_yprivacy_text_3":"Webhelyünk böngészése közben megváltoztathatja a beállításait, és elutasíthatja a számítógépén tárolni kívánt bizonyos típusú sütik használatát. A számítógépen már tárolt sütiket eltávolíthatja, de ne feledje, hogy a sütik törlése megakadályozhatja weboldalunk egyes részeinek használatát.","pc_yprivacy_title":"Az ön adatai védelme","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Adatvédelmi irányelvek</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktivno","always_active":"Uvijek aktivno","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktivno","nb_agree":"Slažem se","nb_changep":"Promjeni moje postavke","nb_ok":"OK","nb_reject":"Odbijam","nb_text":"Koristimo kolačiće i druge tehnologije praćenja da bismo poboljšali vaše korisničko iskustvo na našoj web stranici, kako bismo vam prikazali personalizirani sadržaj i ciljane oglase, analizirali promet na našoj web stranici i razumjeli odakle dolaze naši posjetitelji.","nb_title":"Mi koristimo kolačiće","pc_fnct_text_1":"Kolačići funkcionalnosti","pc_fnct_text_2":"Ovi se kolačići koriste kako bi vam pružili personalizirano korisničko iskustvo na našoj web stranici i za pamćenje izbora koje napravite kada koristite našu web stranicu.","pc_fnct_text_3":"Na primjer, možemo koristiti kolačiće funkcionalnosti da bismo zapamtili vaše jezične postavke ili upamtili vaše podatke za prijavu.","pc_minfo_text_1":"Više informacija","pc_minfo_text_2":"Za sve upite vezane uz naša pravila o kolačićima i vašim izborima, molimo da nas kontaktirate.","pc_minfo_text_3":"Da bi saznali više, posjetite naša <a href=\'%s\' target=\'_blank\'>Pravila o privatnosti</a>.","pc_save":"Spremi moje postavke","pc_sncssr_text_1":"Strogo potrebni kolačići","pc_sncssr_text_2":"Ovi su kolačići neophodni za pružanje usluga dostupnih putem naše web stranice i omogućavanje korištenja određenih značajki naše web stranice.","pc_sncssr_text_3":"Bez ovih kolačića ne možemo vam pružiti određene usluge na našoj web stranici.","pc_title":"Centar za postavke kolačića","pc_trck_text_1":"Kolačići za praćenje i performanse","pc_trck_text_2":"Ovi se kolačići koriste za prikupljanje podataka za analizu prometa na našoj web stranici i za informaciju kako posjetitelji koriste našu web stranicu.","pc_trck_text_3":"Na primjer, ti kolačići mogu pratiti stvari poput dugovanja na web stranici ili stranicama koje posjetite što nam pomaže da shvatimo kako možemo poboljšati vaše korisničko iskustvo na našoj web stranici.","pc_trck_text_4":"Informacije prikupljene ovim praćenjem i kolačići izvedbe ne identificiraju nijednog pojedinačnog posjetitelja.","pc_trgt_text_1":"Kolačići za ciljano oglašavanje","pc_trgt_text_2":"Ovi se kolačići koriste za prikazivanje oglasa koji bi vas mogli zanimati na temelju vaših navika pregledavanja web stranica.","pc_trgt_text_3":"Ovi kolačići, posluženi od naših pružatelja sadržaja i / ili oglašavanja, mogu kombinirati podatke koje su prikupili s naše web stranice s drugim podacima koje su neovisno prikupili, a odnose se na aktivnosti vašeg web preglednika kroz njihovu mrežu web stranica.","pc_trgt_text_4":"Ako odlučite ukloniti ili onemogućiti ove kolačiće za ciljano oglašavanje, i dalje ćete vidjeti oglase, ali oni možda nisu relevantni za vas.","pc_yprivacy_text_1":"Vaša privatnost nam je važna","pc_yprivacy_text_2":"Kolačići su vrlo male tekstualne datoteke koje se pohranjuju na vašem računalu kada posjetite web stranicu. Mi koristimo kolačiće za različite svrhe i za poboljšanje vašeg mrežnog iskustva na našoj web stranici (na primjer, za pamćenje podataka za prijavu na vaš korisnički račun).","pc_yprivacy_text_3":"Možete promijeniti svoje postavke i odbiti određene vrste kolačića koji će se pohraniti na vašem računalu tijekom pregledavanja naše web stranice. Također možete ukloniti sve kolačiće koji su već pohranjeni na vašem računalu, ali imajte na umu da vas brisanje kolačića može spriječiti da koristite dijelove naše web stranice.","pc_yprivacy_title":"Vaša privatnost","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Pravila o privatnosti</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktivní","always_active":"Vždy aktivní","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktivní","nb_agree":"Souhlasím","nb_changep":"Upravit mé předvolby","nb_ok":"OK","nb_reject":"Odmítám","nb_text":"Tyto webové stránky používají soubory cookies a další sledovací nástroje s cílem vylepšení uživatelského prostředí, zobrazení přizpůsobeného obsahu a  reklam, analýzy návštěvnosti webových stránek a zjištění zdroje návštěvnosti.","nb_title":"Používáme soubory cookies","pc_fnct_text_1":"Cookies pro funkcionality","pc_fnct_text_2":"Tyto soubory cookie se používají k tomu, aby vám na našich webových stránkách poskytovaly personalizovaný uživatelský zážitek a aby si pamatovaly vaše volby, které jste použili při používání našich webových stránek.","pc_fnct_text_3":"Můžeme například používat soubory cookie k zapamatování vašeho jazyka nebo k zapamatování vašich přihlašovacích údajů.","pc_minfo_text_1":"Další informace","pc_minfo_text_2":"V případě jakýchkoliv dotazů  ohledně našich zásad týkajících se souborů cookie a vašich možností nás prosím kontaktujte.","pc_minfo_text_3":"Pro více informací navštivte naši stránku <a href=\'%s\' target=\'_blank\'>Zásady ochrany osobních údajů</a>.","pc_save":"Uložit mé předvolby","pc_sncssr_text_1":"Bezpodmínečně nutné soubory cookies","pc_sncssr_text_2":"Tyto soubory cookies jsou nezbytné k tomu, abychom vám mohli poskytovat služby dostupné prostřednictvím našeho webu a abychom vám umožnili používat určité funkce našeho webu.","pc_sncssr_text_3":"Bez těchto cookies vám nemůžeme na naší webové stránce poskytovat určité služby.","pc_title":"Centrum předvoleb souborů Cookies","pc_trck_text_1":"Sledovací a výkonnostní soubory cookies","pc_trck_text_2":"Tyto soubory cookies se používají ke shromažďování informací pro analýzu provozu na našich webových stránkách a sledování používání našich webových stránek uživateli.","pc_trck_text_3":"Tyto soubory cookies mohou například sledovat věci jako je doba kterou na webu trávíte, nebo stránky, které navštěvujete, což nám pomáhá pochopit, jak pro vás můžeme vylepšit náš web.","pc_trck_text_4":"Informace shromážděné prostřednictvím těchto sledovacích a výkonnostních cookies neidentifikují žádné osoby.","pc_trgt_text_1":"Cookies pro cílení a reklamu","pc_trgt_text_2":"Tyto soubory cookie se používají k zobrazování reklamy, která vás pravděpodobně bude zajímat na základě vašich zvyků při procházení.","pc_trgt_text_3":"Tyto soubory cookie, jsou požadovány námi/nebo poskytovateli reklam, mohou kombinovat informace shromážděné z našich webových stránek s dalšími informacemi, které nezávisle shromáždily z jiných webových stránek, týkající se činností vašeho internetového prohlížeče v rámci jejich reklamní sítě webových stránek.","pc_trgt_text_4":"Pokud se rozhodnete tyto soubory cookies pro cílení nebo reklamu odstranit nebo deaktivovat, budou se vám reklamy stále zobrazovat, ale nemusí pro vás být nadále personalizované a relevantní.","pc_yprivacy_text_1":"Vaše soukromí je pro nás důležité","pc_yprivacy_text_2":"Soubory cookies jsou velmi malé textové soubory, které se ukládají do vašeho zařízení při navštěvování webových stránek. Soubory Cookies používáme pro různé účely a pro vylepšení vašeho online zážitku na webové stránce (například pro zapamatování přihlašovacích údajů k vašemu účtu).","pc_yprivacy_text_3":"Při procházení našich webových stránek můžete změnit své předvolby a odmítnout určité typy cookies, které se mají ukládat do vašeho počítače. Můžete také odstranit všechny soubory cookie, které jsou již uloženy ve vašem počítači, ale mějte na paměti, že odstranění souborů cookie vám může zabránit v používání částí našeho webu.","pc_yprivacy_title":"Vaše soukromí","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Zásady ochrany osobních údajů</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktiv","always_active":"Altid aktiv","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inaktiv","nb_agree":"Jeg accepterer","nb_changep":"Skift indstillinger","nb_ok":"OK","nb_reject":"Jeg nægter","nb_text":"Vi bruger cookies og andre tracking teknologier for at forbedre din oplevelse på vores website, til at vise personaliseret indhold, målrettede annoncer og til at forstå hvor vores besøgende kommer fra.","nb_title":"Vi bruger cookies","pc_fnct_text_1":"Funktions cookies","pc_fnct_text_2":"Disse cookies anvendes for at kunne give dig en personaliseret oplevelse af vores hjemmeside, og for at kunne huske valg du har truffet.","pc_fnct_text_3":"Eksempelvis kan vi bruge funktions cookies til at huske sprog-indstillinger eller dine login informationer.","pc_minfo_text_1":"Mere information","pc_minfo_text_2":"Har du spørgsmål vedr. vores cookiepolitik og dine valgmuligheder, så kontakt os venligst.","pc_minfo_text_3":"For at finde ud af mere, så læs venligst vores <a href=\'%s\' target=\'_blank\'>Fortrolighedspolitik</a>.","pc_save":"Gem mine indstillinger","pc_sncssr_text_1":"Nødvendige cookies","pc_sncssr_text_2":"Disse Cookies er essentielle for at du kan bruge vores hjemmeside.","pc_sncssr_text_3":"Uden disse cookies kan vi ikke garantere vores hjemmeside virker ordentligt.","pc_title":"Cookie indstillinger","pc_trck_text_1":"Tracking og performance cookies","pc_trck_text_2":"Disse cookies anvendes til at analysere besøg på vores hjemmeside, og hvordan du bruger vores hjemmeside.","pc_trck_text_3":"Eksempelvis kan vi tracke hvor lang tid du bruger hjemmesiden, eller hvilke sider du kigger på. Det hjælper os til at forstå hvordan vi kan forbedre hjemmesiden.","pc_trck_text_4":"Informationerne kan ikke identificere dig som individ og er derfor anonyme.","pc_trgt_text_1":"Målretning og annoncecookies","pc_trgt_text_2":"Disse cookies anvendes for at kunne vise annoncer, som sandsynligvis er interessante for dig, baseret på dine browser profil.","pc_trgt_text_3":"Disse cookies, som sættes af vores indhold og/eller annoncepartnere, kan kombinere information fra flere hjemmesider i hele det netværk som partnerne styrer.","pc_trgt_text_4":"Hvis du deaktiverer denne indstilling vil du fortsat se reklamer, men de vil ikke længere være målrettet til dig.","pc_yprivacy_text_1":"Dit privatliv er vigtigt for os","pc_yprivacy_text_2":"Cookies er en lille tekstfil, som gemmes på din computer, når du besøger et website. Vi bruger cookies til en række formål, og for at forbedre din oplevelse på vores website (eksempelvis for at huske dine login oplysninger).","pc_yprivacy_text_3":"Du kan ændre dine indstillinger og afvise forskellige typer cookies, som gemmes på din computer, når du besøger vores website. Du kan også fjerne cookies som allerede er gemt på din computer, men bemærk venligst at sletning af cookies kan betyde der er dele af hjemmesiden som ikke virker.","pc_yprivacy_title":"Dit privatliv","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Fortrolighedspolitik</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Active","always_active":"Întotdeauna active","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inactive","nb_agree":"Sunt de acord","nb_changep":"Vreau să schimb setările","nb_ok":"OK","nb_reject":"Refuz","nb_text":"Folosim cookie-uri și alte tehnologii de urmărire pentru a îmbunătăți experiența ta de navigare pe website-ul nostru, pentru afișa conținut și reclame personalizate, pentru a analiza traficul de pe website-ul nostru și pentru a înțelege de unde vin vizitatorii noștri.","nb_title":"Folosim cookie-uri","pc_fnct_text_1":"Cookie-uri funcționale","pc_fnct_text_2":"Aceste cookie-uri sunt folosite pentru a-ți asigura o experiență personalizată pe website-ul nostru și pentru salvarea alegerilor pe care le faci când folosești website-ul nostru.","pc_fnct_text_3":"De exemplu, putem folosi cookie-uri funcționale pentru a salva preferințele tale legate de limba website-ului nostru sau datele de logare.","pc_minfo_text_1":"Mai multe informații","pc_minfo_text_2":"Pentru mai multe informații cu privire la politica noastră de cookie-uri și preferințele tale, te rugăm să ne contactezi.","pc_minfo_text_3":"Pentru a afla mai multe, te rugăm să citești <a href=\'%s\' target=\'_blank\'>Politica noastră de confidențialitate</a>.","pc_save":"Salvează","pc_sncssr_text_1":"Cookie-uri strict necesare","pc_sncssr_text_2":"Aceste cookie-uri sunt esențiale pentru a putea beneficia de serviciile disponibile pe website-ul nostru.","pc_sncssr_text_3":"Fără aceste cookie-uri nu poți folosi anumite funcționalități ale website-ului nostru.","pc_title":"Preferințe pentru Cookie-uri","pc_trck_text_1":"Cookie-uri de analiză și performanță","pc_trck_text_2":"Acest tip de cookie-uri sunt folosite pentru a colecta informații în vederea analizării traficului pe website-ul nostru și modul în care vizitatorii noștri folosesc website-ul.","pc_trck_text_3":"De exemplu, aceste cookie-uri pot urmări cât timp petreci pe website sau paginile pe care le vizitezi, ceea ce ne ajută să înțelegem cum putem îmbunătăți website-ul pentru tine.","pc_trck_text_4":"Informațiile astfel colectate nu identifică individual vizitatorii.","pc_trgt_text_1":"Cookie-uri pentru marketing și publicitate","pc_trgt_text_2":"Aceste cookie-uri sunt folosite pentru a-ți afișa reclame cât mai pe interesul tău, în funcție de obiceiurile tale de navigare.","pc_trgt_text_3":"Aceste cookie-uri, așa cum sunt afișate de furnizori noștri de conținut și/sau publicitate, pot combina informații de pe website-ul nostru cu alte informații pe care furnizori noștri le-au colectat în mod independent cu privire la activitatea ta în rețeaua lor de website-uri.","pc_trgt_text_4":"Dacă alegi să ștergi sau să dezactivezi aceste cookie-uri tot vei vedea reclame, dar se poate ca aceste reclame să nu fie relevante pentru tine.","pc_yprivacy_text_1":"Confidențialitatea ta este importantă pentru noi","pc_yprivacy_text_2":"Cookie-urile sunt fișiere text foarte mici ce sunt salvate în browser-ul tău atunci când vizitezi un website. Folosim cookie-uri pentru mai multe scopuri, dar și pentru a îți oferi cea mai bună experiență de utilizare posibilă (de exemplu, să reținem datele tale de logare în cont).","pc_yprivacy_text_3":"Îți poți modifica preferințele și poți refuza ca anumite tipuri de cookie-uri să nu fie salvate în browser în timp ce navigezi pe website-ul nostru. Deasemenea poți șterge cookie-urile salvate deja în browser, dar reține că este posibil să nu poți folosi anumite părți ale website-ul nostru în acest caz.","pc_yprivacy_title":"Confidențialitatea ta","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Politica noastră de confidențialitate</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktívne","always_active":"Vždy aktívne","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktívne","nb_agree":"Súhlasím","nb_changep":"Zmeniť moje nastavenia","nb_ok":"OK","nb_reject":"Odmietam","nb_text":"Súbory cookie a ďalšie technológie sledovania používame na zlepšenie vášho zážitku z prehliadania našich webových stránok, na to, aby sme vám zobrazovali prispôsobený obsah a cielené reklamy, na analýzu návštevnosti našich webových stránok a na pochopenie toho, odkiaľ naši návštevníci prichádzajú.","nb_title":"Používame cookies","pc_fnct_text_1":"Funkčné cookies","pc_fnct_text_2":"Tieto súbory cookie sa používajú na to, aby vám poskytli osobnejšie prostredie na našej webovej stránke, a na zapamätanie si rozhodnutí, ktoré urobíte pri používaní našej webovej stránky.","pc_fnct_text_3":"Napríklad môžeme použiť funkčné cookies na zapamätanie vašich jazykových preferencií alebo na zapamätanie vašich prihlasovacích údajov.","pc_minfo_text_1":"Viac informácií","pc_minfo_text_2":"Ak máte akékoľvek otázky týkajúce sa našich zásad týkajúcich sa súborov cookie a vašich možností, kontaktujte nás.","pc_minfo_text_3":"Ak sa chcete dozvedieť viac, navštívte <a href=\'%s\' target=\'_blank\'>Zásady ochrany osobných údajov</a>.","pc_save":"Ulož moje predvoľby","pc_sncssr_text_1":"Nevyhnutne potrebné cookies","pc_sncssr_text_2":"Tieto súbory cookie sú nevyhnutné na to, aby sme vám mohli poskytovať služby dostupné prostredníctvom našej webovej stránky a aby ste mohli používať určité funkcie našej webovej stránky.","pc_sncssr_text_3":"Bez týchto súborov cookie vám nemôžeme poskytnúť určité služby na našom webe.","pc_title":"Centrum predvolieb cookies","pc_trck_text_1":"Sledovacie a výkonnostné cookies","pc_trck_text_2":"Tieto súbory cookie sa používajú na zhromažďovanie informácií na analýzu prenosu na našom webe a toho, ako návštevníci používajú náš web.","pc_trck_text_3":"Tieto súbory cookie môžu napríklad sledovať napríklad to, koľko času strávite na webových stránkach alebo navštívených stránkach, čo nám pomáha pochopiť, ako môžeme pre vás vylepšiť naše webové stránky.","pc_trck_text_4":"Informácie zhromaždené prostredníctvom týchto súborov cookie na sledovanie a výkonnosť neidentifikujú žiadneho jednotlivého návštevníka.","pc_trgt_text_1":"Zacielenie a reklamné cookies","pc_trgt_text_2":"Tieto súbory cookie sa používajú na zobrazovanie reklám, ktoré by vás mohli pravdepodobne zaujímať na základe vašich zvykov pri prehliadaní.","pc_trgt_text_3":"Tieto súbory cookie, ktoré slúžia pre náš obsah a/alebo poskytovateľov reklám, môžu kombinovať informácie zhromaždené z našej webovej stránky s ďalšími informáciami, ktoré nezávisle zhromaždili, týkajúce sa aktivít vášho webového prehliadača v rámci ich siete webových stránok.","pc_trgt_text_4":"Ak sa rozhodnete odstrániť alebo zakázať tieto súbory cookie pre zacielenie alebo reklamu, stále sa vám budú zobrazovať reklamy, ktoré však pre vás nemusia byť relevantné.","pc_yprivacy_text_1":"Vaše súkromie je pre nás dôležité","pc_yprivacy_text_2":"Súbory cookie sú veľmi malé textové súbory, ktoré sa ukladajú do vášho počítača pri návšteve webovej stránky. Súbory cookie používame na rôzne účely a na zlepšenie vášho online zážitku z našej webovej stránky (napríklad na zapamätanie prihlasovacích údajov vášho účtu).","pc_yprivacy_text_3":"Môžete zmeniť svoje predvoľby a odmietnuť určité typy súborov cookie, ktoré sa majú ukladať vo vašom počítači pri prehliadaní našich webových stránok. Môžete tiež odstrániť všetky súbory cookie, ktoré sú už uložené vo vašom počítači, ale nezabudnite, že vymazanie súborov cookie vám môže zabrániť v používaní častí našej webovej stránky.","pc_yprivacy_title":"Vaše súkromie","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Zásady ochrany osobných údajov</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktivni","always_active":"Vedno aktivni","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktivni","nb_agree":"Se strinjam","nb_changep":"Spremeni moje nastavitve","nb_ok":"V redu","nb_reject":"Zavračam","nb_text":"Piškotke in druge sledilne tehnologije uporabljamo za izboljšanje vaše uporabniške izkušnje med brskanjem po naši spletni strani, za  prikazovanje personaliziranih vsebin oz. targetiranih oglasov, za analizo obiskov naše spletne strani in za vpogled v to, iz kje prihajajo naši gostje.","nb_title":"Uporabljamo piškotke","pc_fnct_text_1":"Funkcionalni piškotki (ang. functionality cookies)","pc_fnct_text_2":"Ti piškotki se uporabljajo za zagotavljanje bolj personalizirane izkušnje na naši spletni strani in za shranjevanje vaših odločitev ob uporabi naše spletne strani.","pc_fnct_text_3":"Funkcionalne piškotke lahko, na primer, uporabljamo za to, da si zapomnimo vaše jezikovne nastavitve oz. podatke za vpis v vaš račun.","pc_minfo_text_1":"Več informacij","pc_minfo_text_2":"Če imate kakršnakoli vprašanja v zvezi z našim pravilnikom o piškotkih in vaših izbirah, nas prosim kontaktirajte.","pc_minfo_text_3":"Za več informacij si prosim oglejte naš <a href=\'%s\' target=\'_blank\'>Politika zasebnosti</a>.","pc_save":"Shrani moje nastavitve","pc_sncssr_text_1":"Nujno potrebni piškotki (ang. strictly necessary cookies)","pc_sncssr_text_2":"Ti piškotki so ključnega pomena pri zagotavljanju storitev, ki so na voljo na naši spletni strani, in pri omogočanju določenih funkcionalnosti naše spletne strani.","pc_sncssr_text_3":"Brez teh piškotkov vam ne moremo zagotoviti določenih storitev na naši spletni strani.","pc_title":"Nastavitve piškotkov","pc_trck_text_1":"Sledilni in izvedbeni piškotki (ang. tracking and performance cookies)","pc_trck_text_2":"Ti piškotki se uporabljajo za zbiranje podatkov za analizo obiskov naše spletne strani in vpogled v to, kako gostje uporabljajo našo spletno stran.","pc_trck_text_3":"Ti piškotki lahko, na primer, spremljajo stvari kot so to, koliko časa preživite na naši spletni strani oz. katere strani obiščete, kar nam pomaga pri razumevanju, kako lahko za vas izboljšamo spletno stran.","pc_trck_text_4":"Podatki, ki jih zbirajo ti piškotki, ne identificirajo nobenega posameznega uporabnika.","pc_trgt_text_1":"Ciljni in oglaševalski piškotki (ang. targeting and advertising cookies)","pc_trgt_text_2":"Ti piškotki se uporabljajo za prikazovanje spletnih oglasov, ki vas bodo na podlagi vaših navad pri brskanju verjetno zanimali.","pc_trgt_text_3":"Ti piškotki, ki jih uporabljajo naši oglaševalski ponudniki oz. ponudniki vsebine, lahko združujejo podatke, ki so jih zbrali na naši spletni strani, z drugimi podatki, ki so jih zbrali neodvisno v povezavi z dejavnostmi vašega spletnega brskalnika na njihovi mreži spletnih mest.","pc_trgt_text_4":"Če se odločite izbrisati oz. onemogočiti te ciljne in oglaševalske piškotke, boste še vedno videvali oglase, vendar ti morda ne bodo relevantni za vas.","pc_yprivacy_text_1":"Cenimo vašo zasebnost","pc_yprivacy_text_2":"Piškotki so majhne besedilne datoteke, ki se shranijo na vašo napravo ob obisku spletne strani. Piškotke uporabljamo v več namenov, predvsem pa za izboljšanje vaše spletne izkušnje na naši strani (na primer za shranjevanje podatkov ob vpisu v vaš račun).","pc_yprivacy_text_3":"Vaše nastavitve lahko spremenite in onemogočite določenim vrstam piškotkov, da bi se shranili na vašo napravo med brskanjem po naši spletni strani. Poleg tega lahko odstranite katerekoli piškotke, ki so že shranjeni v vaši napravi, a upoštevajte, da vam bo po izbrisu piškotkov morda onemogočeno uporabljati dele naše spletne strani.","pc_yprivacy_title":"Vaša zasebnost","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Politika zasebnosti</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktywne","always_active":"Zawsze aktywne","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Nieaktywne","nb_agree":"Zgoda","nb_changep":"Zmiana ustawień","nb_ok":"OK","nb_reject":"Odmawiam","nb_text":"Używamy plików cookie i innych technologii śledzenia, aby poprawić jakość przeglądania naszej witryny, wyświetlać spersonalizowane treści i reklamy, analizować ruch w naszej witrynie i wiedzieć, skąd pochodzą nasi użytkownicy.","nb_title":"Używamy pliki cookie","pc_fnct_text_1":"Funkcjonalne","pc_fnct_text_2":"Te pliki cookie służą do bardziej spersonalizowanego korzystania z naszej strony internetowej i do zapamiętywania wyborów dokonywanych podczas korzystania z naszej strony internetowej.","pc_fnct_text_3":"Na przykład możemy używać funkcjonalnych plików cookie do zapamiętywania preferencji językowych lub zapamiętywania danych logowania.","pc_minfo_text_1":"Więcej informacji","pc_minfo_text_2":"W przypadku jakichkolwiek pytań dotyczących naszej polityki dotyczącej plików cookie i Twoich wyborów, skontaktuj się z nami.","pc_minfo_text_3":"Aby dowiedzieć się więcej, odwiedź naszą <a href=\'%s\' target=\'_blank\'>Polityka prywatności</a>.","pc_save":"Zapisz ustawienia","pc_sncssr_text_1":"Niezbędne","pc_sncssr_text_2":"Te pliki cookie są niezbędne do świadczenia usług dostępnych za pośrednictwem naszej strony internetowej i umożliwienia korzystania z niektórych funkcji naszej strony internetowej.","pc_sncssr_text_3":"Bez tych plików cookie nie możemy zapewnić usług na naszej stronie internetowej.","pc_title":"Centrum ustawień cookie","pc_trck_text_1":"Śledzenie i wydajność","pc_trck_text_2":"Te pliki cookie służą do zbierania informacji w celu analizy ruchu na naszej stronie internetowej i sposobu, w jaki użytkownicy korzystają z naszej strony internetowej.","pc_trck_text_3":"Na przykład te pliki cookie mogą śledzić takie rzeczy, jak czas spędzony na stronie lub odwiedzane strony, co pomaga nam zrozumieć, w jaki sposób możemy ulepszyć naszą witrynę internetową.","pc_trck_text_4":"Informacje zebrane przez te pliki nie identyfikują żadnego konkretnego użytkownika.","pc_trgt_text_1":"Targeting i reklama","pc_trgt_text_2":"Te pliki cookie służą do wyświetlania reklam, które mogą Cię zainteresować na podstawie Twoich zwyczajów przeglądania.","pc_trgt_text_3":"Pliki te tworzone przez naszych dostawców treści i/lub reklam, mogą łączyć informacje zebrane z naszej strony z innymi informacjami, które gromadzili niezależnie w związku z działaniami przeglądarki internetowej w ich sieci witryn.","pc_trgt_text_4":"Jeśli zdecydujesz się usunąć lub wyłączyć te pliki cookie, reklamy nadal będą wyświetlane, ale mogą one nie być odpowiednie dla Ciebie.","pc_yprivacy_text_1":"Twoja prywatność jest dla nas ważna","pc_yprivacy_text_2":"Pliki cookie to bardzo małe pliki tekstowe, które są tworzone i przechowywane na komputerze użytkownika podczas odwiedzania strony internetowej. Używamy plików cookie do różnych celów, w tym do ulepszania obsługi online na naszej stronie internetowej (na przykład, aby zapamiętać dane logowania do konta).","pc_yprivacy_text_3":"Możesz zmienić swoje ustawienia i odrzucić niektóre rodzaje plików cookie, które mają być przechowywane na twoim komputerze podczas przeglądania naszej strony. Możesz również usunąć wszystkie pliki cookie już zapisane na komputerze, ale pamiętaj, że usunięcie plików cookie może uniemożliwić korzystanie z części naszej strony internetowej.","pc_yprivacy_title":"Twoja prywatność","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Polityka prywatności</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktivno","always_active":"Uvek aktivno","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktivno","nb_agree":"Slažem se","nb_changep":"Promeni moja podešavanja","nb_ok":"OK","nb_reject":"Odbijam","nb_text":"Mi koristimo kolačiće i ostale tehnologije za praćenje kako bismo unapredili vašu pretragu na našem veb sajtu, prikazali personalizovani sadržaj i ciljane reklame, analizirali posete na našem sajtu i razumeli odakle dolaze naši posetioci sajta.","nb_title":"Mi koristimo kolačiće","pc_fnct_text_1":"Funkcionalni kolačići","pc_fnct_text_2":"Ovi kolačići koriste se za pružanje personalizovanijeg iskustva na našem veb sajtu i za pamćenje izbora koje pravite kada koristite naš veb sajt.","pc_fnct_text_3":"Na primer, možemo da koristimo funkcionalne kolačiće da bismo zapamtili vaše jezičke postavke ili vaše podatke za prijavu.","pc_minfo_text_1":"Više informacija","pc_minfo_text_2":"Za bilo koja pitanja vezana za našu politiku o kolačićma i vašim izborima, molimo vas kontaktirajte nas.","pc_minfo_text_3":"Da saznate više, pogledajte našu <a href=\'%s\' target=\'_blank\'>Pravila o privatnosti</a>.","pc_save":"Sačuvaj moja podešavanja","pc_sncssr_text_1":"Obavezni kolačići","pc_sncssr_text_2":"Ovi kolačići su neophodni za pružanje usluga dostupnih putem našeg veb sajta i za omogućavanje korišćenja određenih funkcija našeg veb sajta.","pc_sncssr_text_3":"Bez ovih kolačića ne možemo vam pružiti određene usluge na našem veb sajtu.","pc_title":"Centar za podešavanje kolačića","pc_trck_text_1":"Kolačići za praćenje i performanse","pc_trck_text_2":"Ovi kolačići koriste se za prikupljanje informacija za analizu saobraćaja na našem veb sajtu i kako posetioci koriste naš veb sajt.","pc_trck_text_3":"Na primer, ovi kolačići mogu pratiti stvari poput vremena koliko provodite na veb stranici ili stranicama koje posećujete što nam pomaže da shvatimo kako možemo da poboljšamo naš veb sajt.","pc_trck_text_4":"Informacije prikupljene ovim kolačićima za praćenje i performanse ne identifikuju nijednog pojedinačnog posetioca.","pc_trgt_text_1":"Kolačići za ciljanje i oglašavanje","pc_trgt_text_2":"Ovi kolačići koriste se za prikazivanje reklama koje će vas verovatno zanimati na osnovu vaših navika pregledanja.","pc_trgt_text_3":"Ovi kolačići, opsluženi od strane naših dobavljača sadržaja i / ili oglašavanja, mogu kombinovati informacije koje su sakupili sa našeg veb sajta sa drugim informacijama koje su nezavisno prikupili u vezi sa aktivnostima vašeg veb pretraživača kroz mrežu njihovih veb sajtova.","pc_trgt_text_4":"Ako odlučite da uklonite ili onemogućite ove ciljane ili reklamne kolačiće i dalje ćete videti reklame, ali one možda neće biti relevantne za vas.","pc_yprivacy_text_1":"Vaša privatnost je važna za nas","pc_yprivacy_text_2":"Kolačići su veoma mali tekstualni fajlovi koji su sačuvani na vašem računaru kada posetite veb sajt. Mi koristimo kolačiće za različite svrhe i kako bi unapredili vaše onlajn iskustvo na našem veb sajtu (na primer, kako bi zapamtili vaše pristupne podatke).","pc_yprivacy_text_3":"Vi možete promeniti vaša podešavanja i odbiti određenu vrstu kolačića koji će biti sačuvani na vašem računaru dok pregledate naš veb sajt. Takođe možete izbrisati bilo koje kolačiće koji su već sačuvani u vašem računaru, ali imajte na umu da brisanjem kolačića možete onemogućiti pristup nekim delovima našeg veb sajta.","pc_yprivacy_title":"Vaša privatnost","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Pravila o privatnosti</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Įjungta","always_active":"Visada įjungta","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Išjungta","nb_agree":"Sutinku","nb_changep":"Keisti mano pasirinkimus","nb_ok":"Gerai","nb_reject":"Aš atsisakau","nb_text":"Mes naudojame slapukus ir kitas stebėjimo technologijas, siekdami pagerinti jūsų naršymo mūsų svetainėje patirtį, parodyti jums pritaikytą turinį ir tikslinius skelbimus, išanalizuoti mūsų svetainės srautą ir suprasti, iš kur ateina mūsų lankytojai.","nb_title":"Mes naudojame slapukus","pc_fnct_text_1":"Funkcionalumo slapukai","pc_fnct_text_2":"Šie slapukai naudojami siekiant suteikti jums asmeniškesnę patirtį mūsų svetainėje ir prisiminti pasirinkimus, kuriuos atlikote, kai naudojatės mūsų svetaine.","pc_fnct_text_3":"Pvz., Mes galime naudoti funkcinius slapukus, kad prisimintume jūsų kalbos nustatymus arba prisimintume jūsų prisijungimo duomenis.","pc_minfo_text_1":"Daugiau informacijos","pc_minfo_text_2":"Dėl bet kokių klausimų, susijusių su mūsų slapukų politika ir jūsų pasirinkimais, susisiekite su mumis.","pc_minfo_text_3":"Norėdami sužinoti daugiau, susipažinkite su mūsų <a href=\'%s\' target=\'_blank\'>Privatumo politika</a>.","pc_save":"Išsaugoti mano pasirinkimus","pc_sncssr_text_1":"Privalomi slapukai","pc_sncssr_text_2":"Šie slapukai yra būtini norint suteikti jums paslaugas, pasiekiamas mūsų svetainėje, ir leisti naudotis tam tikromis mūsų svetainės funkcijomis.","pc_sncssr_text_3":"Be šių slapukų mes negalime jums suteikti tam tikrų paslaugų mūsų svetainėje.","pc_title":"Slapukų Pasirinkimo Centras","pc_trck_text_1":"Stebėjimo ir našumo slapukai","pc_trck_text_2":"Šie slapukai naudojami rinkti informaciją, siekiant analizuoti srautą į mūsų svetainę ir tai, kaip lankytojai naudojasi mūsų svetaine.","pc_trck_text_3":"Pavyzdžiui, šie slapukai gali sekti kiek laiko praleidžiate svetainėje ar lankomuose puslapiuose, o tai padeda mums suprasti, kaip galime patobulinti savo svetainę.","pc_trck_text_4":"Informacija, surinkta naudojant šiuos stebėjimo ir našumo slapukus, neatpažįsta konkretaus lankytojo.","pc_trgt_text_1":"Tiksliniai ir reklaminiai slapukai","pc_trgt_text_2":"Šie slapukai naudojami rodyti reklamą, kuri greičiausiai jus domina, atsižvelgiant į jūsų naršymo įpročius.","pc_trgt_text_3":"Šie slapukai, kuriuos teikia mūsų turinio ir (arba) reklamos teikėjai, gali apjungti informaciją, kurią jie surinko iš mūsų svetainės, su kita informacija, kurią jie rinko nepriklausomai, apie jūsų interneto naršyklės veiklą jų svetainių tinkle.","pc_trgt_text_4":"Jei nuspręsite pašalinti arba išjungti šiuos tikslinius ar reklamavimo slapukus, vis tiek pamatysite skelbimus, tačiau jie gali būti jums neaktualūs.","pc_yprivacy_text_1":"Mums rūpi jūsų privatumas","pc_yprivacy_text_2":"Slapukai yra labai maži tekstiniai failai, kurie saugomi jūsų kompiuteryje, kai apsilankote svetainėje. Mes naudojame slapukus įvairiais tikslais ir siekdami pagerinti jūsų internetinę patirtį mūsų svetainėje (pavyzdžiui, jei norite, kad būtu įsimenami jūsų prisijungimo duomenys).","pc_yprivacy_text_3":"Naršydami mūsų svetainėje galite pakeisti savo nustatymus ir atsisakyti tam tikrų tipų slapukų, kurie bus saugomi jūsų kompiuteryje. Taip pat galite pašalinti visus slapukus, jau saugomus jūsų kompiuteryje, tačiau nepamirškite, kad ištrynę slapukus galite nepilnai naudotis mūsų svetaine.","pc_yprivacy_title":"Jūsų privatumas","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privatumo politika</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktīvs","always_active":"Vienmēr aktīvs","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Neaktīvs","nb_agree":"Es piekrītu","nb_changep":"Mainīt manas preferences","nb_ok":"OK","nb_reject":"Es noraidu","nb_text":"Mēs izmantojam sīkdatnes un citas izsekošanas tehnoloģijas, lai uzlabotu Jūsu pārlūkošanas pieredzi mūsu vietnē, parādītu Jums personalizētu saturu un mērķētas reklāmas, analizētu mūsu vietnes datplūsmu un saprastu, no kurienes nāk mūsu apmeklētāji.","nb_title":"Mēs izmantojam sīkdatnes","pc_fnct_text_1":"Funkcionalitātes sīkdatnes","pc_fnct_text_2":"Šīs sīkdatnes tiek izmantotas, lai Jūs nodrošinātu ar personalizētu pieredzi mūsu mājaslapā un lai atcerētos izvēles, kuras veicat izmantojot mūsu mājaslapu.","pc_fnct_text_3":"Piemēram, mēs varam izmantot funkcionalitātes sīkdatnes, lai atcerētos Jūsu valodas preferences vai konta pieteikšanās datus.","pc_minfo_text_1":"Vairāk informācijas","pc_minfo_text_2":"Par jautājumiem saistītiem ar mūsu sīkdatņu politiku un Jūsu izvēlēm, lūdzu, sazinieties ar mums.","pc_minfo_text_3":"Lai uzzinātu vairāk, lūdzu apmeklējiet mūsu <a href=\'%s\' target=\'_blank\'>Privacy Policy</a>.","pc_save":"Saglabāt manas preferences","pc_sncssr_text_1":"Strikti nepieciešamās sīkdatnes","pc_sncssr_text_2":"Šīs sīkdatnes ir nepieciešamas, lai nodrošinātu Jums pakalpojumus, kas pieejami caur mūsu mājaslapu un ļautu Jums izmantot noteiktas mūsu vietnes funkcijas.","pc_sncssr_text_3":"Bez šīm sīkdatnēm, mēs nevaram Jums nodrošināt noteiktus pakalpojumus mūsu mājaslapā.","pc_title":"Sīkdatņu Preferenču Centrs","pc_trck_text_1":"Izsekošanas sīkdatnes","pc_trck_text_2":"Šīs sīkdatnes tiek izmantotas informācijas apkopošanai, lai analizētu mūsu mājaslapas datplūsmu, un kā apmeklētāji izmanto mūsu mājaslapu.","pc_trck_text_3":"Piemēram, šīs sīkdatnes var izsekot cik daudz laika Jūs pavadāt mājaslapā vai Jūsu apmeklētās lapas, kas mums palīdz saprast, kā mēs Jums varam uzlabot mūsu mājaslapu.","pc_trck_text_4":"Informācija, kas savākta, izmantojot šīs izsekošanas un veiktspējas sīkdatnes, neidentificē nevienu atsevišķu apmeklētāju.","pc_trgt_text_1":"Mērķauditorijas atlases un reklāmas sīkdatnes","pc_trgt_text_2":"Šīs sīkdatnes tiek izmantotas, lai rādītu reklāmas, kas iespējams, Jūs interesēs, pamatojoties uz Jūsu pārlūkošanas paradumiem.","pc_trgt_text_3":"Šīs sīkdatnes, ko apkalpo mūsu satura un/vai reklāmas nodrošinātāji, var apvienot informāciju , kas savākta no mūsu mājaslapas ar citu viņu rīcībā esošo informāciju, ko viņi ir neatkarīgi apkopojuši, kas saistīta ar Jūsu tīmekļa pārlūkprogrammas darbību viņu vietņu tīklā.","pc_trgt_text_4":"Ja Jūs izvēlaties noņemt vai atspējot šīs mērķauditorijas atlases vai reklāmas sīkdatnes, Jūs joprojām redzēsiet reklāmas, bet tās var nebūt Jums aktuālas.","pc_yprivacy_text_1":"Mums ir svarīgs Jūsu privātums","pc_yprivacy_text_2":"Sīkdatnes ir ļoti mazi teksta faili, kas tiek saglabāti Jūsu datorā, kad apmeklējat mājaslapu. Mēs izmantojam sīkdatnes dažādiem mērķiem, un lai uzlabotu Jūsu tiešsaistes pieredzi mūsu mājaslapā (piemēram, lai atcerētos Jūsu konta pieteikšanās datus).","pc_yprivacy_text_3":"Jūs varat mainīt savas preferences un noraidīt noteiktus sīkfailu veidus, kas saglabātos Jūsu datorā, pārlūkojot mūsu mājaslapu. Jūs varat arī noņemt sīkfailus, kas jau ir saglabāti Jūsu datorā, taču paturiet prātā, ka sīkdatņu dzēšana var liegt Jums izmantot atsevišķas daļas no mūsu mājaslapas.","pc_yprivacy_title":"Jūsu privātums","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privacy Policy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Активно","always_active":"Всегда активно","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Неактивно","nb_agree":"Я согласен","nb_changep":"Изменить мои предпочтения","nb_ok":"Ок","nb_reject":"Я отказываюсь","nb_text":"Мы используем файлы куки и другие технологии отслеживания для улучшения вашего просмотра на нашем веб-сайте, чтобы показывать вам персонализированный контент и таргетированную рекламу, анализировать трафик нашего веб-сайта и понимать, откуда приходят наши посетители.","nb_title":"Мы используем куки","pc_fnct_text_1":"Функциональные куки","pc_fnct_text_2":"Файлы куки используются, чтобы предоставить вам более персонализированный опыт на нашем веб-сайте и запомнить выбор, который вы делаете при использовании нашего веб-сайта.","pc_fnct_text_3":"Например, мы можем использовать функциональные файлы куки, чтобы запомнить ваши языковые предпочтения или данные для входа.","pc_minfo_text_1":"Больше информации.","pc_minfo_text_2":"По любым вопросам, касающимся нашей политики в отношении файлов куки и вашего выбора, свяжитесь с нами.","pc_minfo_text_3":"Чтобы узнать больше, посетите наш сайт <a href=\'%s\' target=\'_blank\'>Privacy Policy</a>.","pc_save":"Сохранить мои предпочтения","pc_sncssr_text_1":"Необходимые куки","pc_sncssr_text_2":"Файлы куки необходимы для предоставления вам услуг, доступных через наш веб-сайт, и для того, чтобы вы могли использовать определенные функции нашего веб-сайта.","pc_sncssr_text_3":"Без этих файлов куки мы не можем предоставлять вам определенные функции на нашем веб-сайте.","pc_title":"Центр настроек файлов куки","pc_trck_text_1":"Отслеживание куки","pc_trck_text_2":"Файлы куки используются для сбора информации для анализа трафика на наш веб-сайт и того, как посетители используют наш веб-сайт.","pc_trck_text_3":"Например, эти файлы куки могут отслеживать такие вещи, как время, которое вы проводите на веб-сайте или посещаемые вами страницы, что помогает нам понять, как мы можем улучшить наш веб-сайт для вас.","pc_trck_text_4":"Информация, собранная с помощью файлов куки для отслеживания и производительности, не идентифицирует отдельного посетителя.","pc_trgt_text_1":"Целевые и рекламные файлы куки","pc_trgt_text_2":"Эти файлы куки используются для показа рекламы, которая может быть вам интересна в зависимости от ваших привычек просмотра.","pc_trgt_text_3":"Эти файлы куки, обслуживаемые нашими поставщиками контента и / или рекламы, могут объединять информацию, собранную ими с нашего веб-сайта, с другой информацией, которую они независимо собирали относительно действий вашего браузера в их сети веб-сайтов.","pc_trgt_text_4":"Если вы решите удалить или отключить эти целевые или рекламные файлы куки, вы все равно будете видеть рекламу, но она может не иметь отношения к вам.","pc_yprivacy_text_1":"Ваша конфиденциальность важна для нас","pc_yprivacy_text_2":"Куки - это небольшие текстовые файлы, которые сохраняются на вашем компьютере, когда Вы посещаете веб-сайт. Мы используем куки для различных целей, в том числе для того, чтобы улучшить ваше пребывание на нашем веб-сайте (например, чтобы запомнить данные для входа в вашу учетную запись).","pc_yprivacy_text_3":"Вы можете изменить свои предпочтения и отказаться от сохранения определенных типов файлов cookie на вашем компьютере во время просмотра нашего веб-сайта. Вы также можете удалить любые файлы куки, уже хранящиеся на вашем компьютере, но имейте в виду, что удаление файлов cookie может помешать вам использовать некоторые части нашего веб-сайта.","pc_yprivacy_title":"Ваша конфиденциальность","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Privacy Policy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Aktiv","always_active":"Alltid aktiv","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Inaktiv","nb_agree":"Godta alle","nb_changep":"Endre innstillinger","nb_ok":"OK","nb_reject":"Avvis alle","nb_text":"Vi bruker informasjonskapsler og andre sporingsteknologier for å forbedre din nettleseropplevelse på nettstedet vårt, for å vise deg personlig tilpasset innhold og målrettede annonser, for å analysere nettstedstrafikken vår og for å forstå hvor våre besøkende kommer fra.","nb_title":"Vi bruker informasjonskapsler","pc_fnct_text_1":"Funksjonalitetscookies","pc_fnct_text_2":"Disse informasjonskapslene brukes til å gi deg en mer personlig opplevelse på nettstedet vårt og til å huske valg du tar når du bruker nettstedet vårt.","pc_fnct_text_3":"For eksempel kan vi bruke funksjonalitetscookies for å huske språkinnstillingene dine eller huske påloggingsinformasjonen din.","pc_minfo_text_1":"Mer informasjon","pc_minfo_text_2":"For spørsmål angående våre retningslinjer for informasjonskapsler og dine valg, vennligst kontakt oss.","pc_minfo_text_3":"For å finne ut mer, besøk vår <a href=\'%s\' target=\'_blank\'>personvernpolicy</a>.","pc_save":"Lagre mine preferanser","pc_sncssr_text_1":"Strengt nødvendige informasjonskapsler","pc_sncssr_text_2":"Disse informasjonskapslene er viktige for å gi deg tjenester tilgjengelig via nettstedet vårt og for å gjøre det mulig for deg å bruke visse funksjoner på nettstedet vårt.","pc_sncssr_text_3":"Uten disse informasjonskapslene kan vi ikke tilby deg visse tjenester på nettstedet vårt.","pc_title":"Informasjonssenter for informasjonskapsler","pc_trck_text_1":"Sporings- og ytelses-informasjonskapsler","pc_trck_text_2":"Disse informasjonskapslene brukes til å samle inn informasjon for å analysere trafikken til nettstedet vårt og hvordan besøkende bruker nettstedet vårt","pc_trck_text_3":"Disse informasjonskapslene kan for eksempel spore ting som hvor lang tid du bruker på nettstedet eller sidene du besøker, noe som hjelper oss å forstå hvordan vi kan forbedre nettstedet vårt for deg.","pc_trck_text_4":"Informasjonen som samles inn gjennom disse sporings- og ytelseskapslene, identifiserer ikke noen individuell besøkende.","pc_trgt_text_1":"Målretting og annonsering av informasjonskapsler","pc_trgt_text_2":"Disse informasjonskapslene brukes til å vise reklame som sannsynligvis vil være av interesse for deg basert på nettleservaner.","pc_trgt_text_3":"Disse informasjonskapslene, som serveres av innholds- og / eller reklameleverandører, kan kombinere informasjon de har samlet inn fra nettstedet vårt med annen informasjon de har samlet uavhengig av nettleserens aktiviteter på tvers av nettverket av nettsteder.","pc_trgt_text_4":"Hvis du velger å fjerne eller deaktivere disse målrettings- eller annonseringskapslene, vil du fremdeles se annonser, men de er kanskje ikke relevante for deg.","pc_yprivacy_text_1":"Ditt personvern er viktig for oss","pc_yprivacy_text_2":"Informasjonskapsler er veldig små tekstfiler som lagres på datamaskinen din når du besøker et nettsted. Vi bruker informasjonskapsler for en rekke formål og for å forbedre din online opplevelse på nettstedet vårt (for eksempel for å huske påloggingsinformasjonen din).","pc_yprivacy_text_3":"Du kan endre innstillingene dine og avvise visse typer informasjonskapsler som skal lagres på datamaskinen din mens du surfer på nettstedet vårt. Du kan også fjerne alle informasjonskapsler som allerede er lagret på datamaskinen din, men husk at sletting av informasjonskapsler kan forhindre deg i å bruke deler av nettstedet vårt.","pc_yprivacy_title":"Ditt personvern","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Personvernpolicy</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"В действие са бисквитките","always_active":"Винаги в действие са бисквитките","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Неактивни бисквитки","nb_agree":"Съгласен съм","nb_changep":"Промяна на предпочитанията ми","nb_ok":"Добре","nb_reject":"Аз отказвам","nb_text":"Ние използваме бисквитки и други, проследяващи, технологии, за да подобрим сърфирането ви в нашия сайт, като ви покажем персонализирано съдържание и реклами, да анализираме трафика на нашия сайт и да разберем откъде идват нашите посетители.","nb_title":"Ние използваме бисквитки","pc_fnct_text_1":"Функционални бисквитки","pc_fnct_text_2":"Тези бисквитки се използват, за да ви осигурят още по-персонализирано изживяване на нашия уебсайт и да бъдат запомнени изборите, които сте направили, когато използвахте нашия уебсайт.","pc_fnct_text_3":"Например: може да използваме функционални бисквитки, за да запомним предпочитания ви език или да запомним детайли по влизането ви в уебсайта.","pc_minfo_text_1":"Още информация","pc_minfo_text_2":"За всякакви въпроси във връзка с нашата политика за бисквитките и вашите избори, моля, свържете се с нас.","pc_minfo_text_3":"За да научите повече, моля, посетете нашата <a href=\'%s\' target=\'_blank\'>Страница за поверителност</a>.","pc_save":"Запази предпочитанията ми","pc_sncssr_text_1":"Строго задължителни бисквитки","pc_sncssr_text_2":"Тези бисквитки са съществен елемент, който осигурява услуги, достъпни чрез нашия уебсайт и дават възможност за използване на определени функции на нашия уебсайт.","pc_sncssr_text_3":"Без тези бисквитки не можем да ви доставим определени услуги на нашия уебсайт.","pc_title":"Център за настройка на бисквитки","pc_trck_text_1":"Бисквитки за проследяване и за производителност","pc_trck_text_2":"Тези бисквитки се използват за събиране на информация за анализ на трафика към нашия уебсайт и как посетителите използват нашия уебсайт.","pc_trck_text_3":"Например, тези бисквитки могат да проследяват неща като колко време прекарвате на уебсайта или на посещаваните от вас страници, което ни помага да разберем как можем да подобрим нашия сайт за вас.","pc_trck_text_4":"Информацията, събрана чрез тези бисквитки за проследяване и производителност, не идентифицира всеки отделен посетител.","pc_trgt_text_1":"Насочване и рекламни бисквитки","pc_trgt_text_2":"Тези бисквитки се използват за показване на реклама, която вероятно ще ви заинтересова въз основа на навиците ви за сърфиране.","pc_trgt_text_3":"Тези бисквитки, обслужвани от нашите доставчици на съдържание и / или реклама, могат да комбинират информацията, която са събрали от нашия уебсайт, с друга информация, която са събрали независимо, свързана с дейностите на вашия уеб браузър в тяхната мрежа от уебсайтове.","pc_trgt_text_4":"Ако решите да премахнете или деактивирате тези бисквитки за определени потребителски групи или реклама, пак ще видите реклами, но те може да не са от подходящи за вас.","pc_yprivacy_text_1":"Вашата поверителност е важна за нас","pc_yprivacy_text_2":"Бисквитките са много малки текстови файлове, които се съхраняват на вашия компютър, когато посетите уебсайт. Ние използваме бисквитки за множество от цели и да подобрим сърфирането ви из нашия сайт (например: за да запомним детайлите на вашия акаунт за влизане).","pc_yprivacy_text_3":"Можете да промените предпочитанията си и да откажете определени видове бисквитки, които да се съхраняват на вашия компютър, докато сърфирате в нашия уебсайт. Можете също да премахнете някои бисквитки, които вече са запазени на вашия компютър, но имайте предвид, че изтриването на бисквитки може да ви попречи да използвате части от нашия уебсайт.","pc_yprivacy_title":"Вашата поверителност","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Страница за поверителност</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Ενεργό","always_active":"Πάντα ενεργό","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Ανενεργό","nb_agree":"Συμφωνώ","nb_changep":"Αλλαγή των προτιμήσεών μου","nb_ok":"OK","nb_reject":"Αρνούμαι","nb_text":"Χρησιμ¿ÏÎ¿Î¹Î¿ÏÎ¼Îµ cookies ÎºÎ±Î¹ Î¬Î»Î»ÎµÏ ÏÎµÏÎ½Î¿Î»Î¿Î³Î¯ÎµÏ ÎµÎ½ÏÎ¿ÏÎ¹ÏÎ¼Î¿Ï Î³Î¹Î± ÏÎ·Î½ Î²ÎµÎ»ÏÎ¯ÏÏÎ· ÏÎ·Ï ÎµÎ¼ÏÎµÎ¹ÏÎ¯Î±Ï ÏÎµÏÎ¹Î®Î³Î·ÏÎ·Ï ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï, Î³Î¹Î± ÏÎ·Î½ ÎµÎ¾Î±ÏÎ¿Î¼Î¯ÎºÎµÏÏÎ· ÏÎµÏÎ¹ÎµÏÎ¿Î¼Î­Î½Î¿Ï ÎºÎ±Î¹ Î´Î¹Î±ÏÎ·Î¼Î¯ÏÎµÏÎ½, ÏÎ·Î½ ÏÎ±ÏÎ¿ÏÎ® Î»ÎµÎ¹ÏÎ¿ÏÏÎ³Î¹ÏÎ½ ÎºÎ¿Î¹Î½ÏÎ½Î¹ÎºÏÎ½ Î¼Î­ÏÏÎ½ ÎºÎ±Î¹ ÏÎ·Î½ Î±Î½Î¬Î»ÏÏÎ· ÏÎ·Ï ÎµÏÎ¹ÏÎºÎµÏÎ¹Î¼ÏÏÎ·ÏÎ¬Ï Î¼Î±Ï.","nb_title":"ÎÏÏÎ® Î· Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹ÎµÎ¯ cookies","pc_fnct_text_1":"Cookies ÎÎµÎ¹ÏÎ¿ÏÏÎ³Î¹ÎºÏÏÎ·ÏÎ±Ï","pc_fnct_text_2":"ÎÏÏÎ¬ ÏÎ± cookies ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î¿ÏÎ½ÏÎ±Î¹ Î³Î¹Î± Î½Î± ÏÎ±Ï ÏÎ±ÏÎ­ÏÎ¿ÏÎ½ Î¼Î¯Î± ÏÎ¹Î¿ ÏÏÎ¿ÏÏÏÎ¿ÏÎ¿Î¹Î·Î¼Î­Î½Î· ÎµÎ¼ÏÎµÎ¹ÏÎ¯Î± ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï ÎºÎ±Î¹ Î³Î¹Î± Î½Î± Î¸ÏÎ¼Î¿ÏÎ½ÏÎ±Î¹ ÎµÏÎ¹Î»Î¿Î³Î­Ï ÏÎ¿Ï ÎºÎ¬Î½ÎµÏÎµ ÏÏÎ±Î½ ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹ÎµÎ¯ÏÎµ ÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï.","pc_fnct_text_3":"ÎÎ¹Î± ÏÎ±ÏÎ¬Î´ÎµÎ¹Î³Î¼Î±, Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î®ÏÎ¿ÏÎ¼Îµ cookies Î»ÎµÎ¹ÏÎ¿ÏÏÎ³Î¹ÎºÏÏÎ·ÏÎ±Ï Î³Î¹Î± Î½Î± Î¸ÏÎ¼ÏÎ¼Î±ÏÏÎµ ÏÎ·Î½ ÎµÏÎ¹Î»Î¿Î³Î® Î³Î»ÏÏÏÎ±Ï Î® ÏÎ± ÏÏÎ¿Î¹ÏÎµÎ¯Î± ÎµÎ¹ÏÏÎ´Î¿Ï ÏÎ±Ï.","pc_minfo_text_1":"Î ÎµÏÎ¹ÏÏÏÏÎµÏÎµÏ ÏÎ»Î·ÏÎ¿ÏÎ¿ÏÎ¯ÎµÏ","pc_minfo_text_2":"ÎÎ¹Î± Î¿ÏÎ¿Î¹Î±Î´Î®ÏÎ¿ÏÎµ Î±ÏÎ¿ÏÎ¯Î± ÏÎµ ÏÏÎ­ÏÎ· Î¼Îµ ÏÎ·Î½ ÏÎ¿Î»Î¹ÏÎ¹ÎºÎ® Î¼Î±Ï ÏÏÎµÏÎ¹ÎºÎ¬ Î¼Îµ ÏÎ± cookies ÎºÎ±Î¹ ÏÎ¹Ï ÎµÏÎ¹Î»Î¿Î³Î­Ï ÏÎ±Ï, ÏÎ±ÏÎ±ÎºÎ±Î»Î¿ÏÎ¼Îµ Î½Î± Î­ÏÎ¸ÎµÏÎµ ÏÎµ ÎµÏÎ±ÏÎ® Î¼Î±Î¶Î¯ Î¼Î±Ï.","pc_minfo_text_3":"ÎÎ¹Î± Î½Î± Î¼Î¬Î¸ÎµÏÎµ ÏÎµÏÎ¹ÏÏÏÏÎµÏÎ±, ÏÎ±ÏÎ±ÎºÎ±Î»Î¿ÏÎ¼Îµ ÎµÏÎ¹ÏÎºÎµÏÎ¸ÎµÎ¯ÏÎµ ÏÎ·Î½ ÏÎµÎ»Î¯Î´Î± ÏÎµÏÎ¯ <a href=\'%s\' target=\'_blank\'>Î Î¿Î»Î¹ÏÎ¹ÎºÎ® Î±ÏÎ¿ÏÏÎ®ÏÎ¿Ï</a>.","pc_save":"ÎÏÎ¿Î¸Î®ÎºÎµÏÏÎ· ÏÏÎ½ ÏÏÎ¿ÏÎ¹Î¼Î®ÏÎµÏÎ½ Î¼Î¿Ï","pc_sncssr_text_1":"ÎÎºÏÏÏ Î±ÏÎ±ÏÎ±Î¯ÏÎ·ÏÎ± cookies","pc_sncssr_text_2":"Î¤Î± Î±ÏÎ±ÏÎ±Î¯ÏÎ·ÏÎ± cookies Î²Î¿Î·Î¸Î¿ÏÎ½ ÏÏÎ¿ Î½Î± Î³Î¯Î½ÎµÎ¹ ÏÏÎ·ÏÏÎ¹ÎºÎ® Î¼Î¯Î± Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±, ÎµÏÎ¹ÏÏÎ­ÏÎ¿Î½ÏÎ±Ï Î²Î±ÏÎ¹ÎºÎ­Ï Î»ÎµÎ¹ÏÎ¿ÏÏÎ³Î¯ÎµÏ ÏÏÏÏ ÏÎ·Î½ ÏÎ»Î¿Î®Î³Î·ÏÎ· ÎºÎ±Î¹ ÏÎ·Î½ ÏÏÏÏÎ²Î±ÏÎ· ÏÎµ Î±ÏÏÎ±Î»ÎµÎ¯Ï ÏÎµÏÎ¹Î¿ÏÎ­Ï ÏÎ·Ï Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±Ï.","pc_sncssr_text_3":"Î Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î´ÎµÎ½ Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± Î»ÎµÎ¹ÏÎ¿ÏÏÎ³Î®ÏÎµÎ¹ ÏÏÏÏÎ¬ ÏÏÏÎ¯Ï Î±ÏÏÎ¬ ÏÎ± cookies.","pc_title":"ÎÎ­Î½ÏÏÎ¿ Î ÏÎ¿ÏÎ¹Î¼Î®ÏÎµÏÎ½ Cookies","pc_trck_text_1":"Cookies ÎµÎ½ÏÎ¿ÏÎ¹ÏÎ¼Î¿Ï ÎºÎ±Î¹ Î±ÏÎ¿Î´Î¿ÏÎ¹ÎºÏÏÎ·ÏÎ±Ï","pc_trck_text_2":"ÎÏÏÎ¬ ÏÎ± cookies ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î¿ÏÎ½ÏÎ±Î¹ Î³Î¹Î± Î½Î± ÏÏÎ»Î»Î­Î³Î¿ÏÎ½ ÏÎ»Î·ÏÎ¿ÏÎ¿ÏÎ¯ÎµÏ ÏÏÎµÏÎ¹ÎºÎ­Ï Î¼Îµ ÏÎ·Î½ Î±Î½Î¬Î»ÏÏÎ· ÏÎ·Ï ÎµÏÎ¹ÏÎºÎµÏÎ¹Î¼ÏÏÎ·ÏÎ±Ï ÏÎ·Ï Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±Ï Î¼Î±Ï ÎºÎ±Î¹ Î¼Îµ ÏÎ¿ ÏÏÏ Î¿Î¹ ÏÏÎ®ÏÏÎµÏ ÏÎ·Î½ ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î¿ÏÎ½.","pc_trck_text_3":"ÎÎ¹Î± ÏÎ±ÏÎ¬Î´ÎµÎ¹Î³Î¼Î±, Î±ÏÏÎ¬ ÏÎ± cookies Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± ÎµÎ½ÏÎ¿ÏÎ¯ÏÎ¿ÏÎ½ ÏÏÏÎ¿ ÏÏÏÎ½Î¿ Î±ÏÎ¹ÎµÏÏÎ½ÎµÏÎµ ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï Î® ÏÎ¿Î¹ÎµÏ ÏÎµÎ»Î¯Î´ÎµÏ ÏÎ·Ï ÎµÏÎ¹ÏÎºÎ­ÏÏÎµÏÏÎµ, ÏÏÎ¬Î³Î¼Î± ÏÎ¿Ï Î¼Î±Ï Î²Î¿Î·Î¸Î¬ÎµÎ¹ Î½Î± ÎºÎ±ÏÎ±Î»Î¬Î²Î¿ÏÎ¼Îµ ÏÏÏ Î½Î± Î²ÎµÎ»ÏÎ¹ÏÏÎ¿ÏÎ¼Îµ ÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï.","pc_trck_text_4":"ÎÎ¹ ÏÎ»Î·ÏÎ¿ÏÎ¿ÏÎ¯ÎµÏ ÏÎ¿Ï ÏÏÎ»Î»Î­Î³Î¿Î½ÏÎ±Î¹ Î¼Î­ÏÏ Î±ÏÏÏÎ½ ÏÏÎ½ cookies Î´ÎµÎ½ Î±Î½Î±Î³Î½ÏÏÎ¯Î¶Î¿ÏÎ½ Î¼ÎµÎ¼Î¿Î½ÏÎ¼Î­Î½Î¿ÏÏ ÏÏÎ®ÏÏÎµÏ.","pc_trgt_text_1":"Cookies ÎµÎ¾Î±ÏÎ¿Î¼Î¹ÎºÎµÏÎ¼Î­Î½Î¿Ï ÏÎµÏÎ¹ÎµÏÎ¿Î¼Î­Î½Î¿Ï ÎºÎ±Î¹ Î´Î¹Î±ÏÎ·Î¼Î¯ÏÎµÏÎ½","pc_trgt_text_2":"ÎÏÏÎ¬ ÏÎ± cookies ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î¿ÏÎ½ÏÎ±Î¹ Î³Î¹Î± Î½Î± Î´ÎµÎ¯ÏÎ½Î¿ÏÎ½ Î´Î¹Î±ÏÎ·Î¼Î¯ÏÎµÎ¹Ï ÏÎ¿Ï Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± ÏÎ±Ï ÎµÎ½Î´Î¹Î±ÏÎ­ÏÎ¿ÏÎ½ Î¼Îµ Î²Î¬ÏÎ· ÏÎ¹Ï ÏÏÎ½Î®Î¸ÎµÎ¹ÎµÏ ÏÎµÏÎ¹Î®Î³Î·ÏÎ®Ï ÏÎ±Ï ÏÏÎ¿ ÎÎ¹Î±Î´Î¯ÎºÏÏÎ¿.","pc_trgt_text_3":"ÎÏÏÎ¬ ÏÎ± cookies, ÏÎ±ÏÎ­ÏÎ¿Î½ÏÎ±Î¹ Î±ÏÏ ÏÎ¿ÏÏ ÏÎ±ÏÏÏÎ¿ÏÏ ÏÎµÏÎ¹ÎµÏÎ¿Î¼Î­Î½Î¿Ï Î®/ÎºÎ±Î¹ Î´Î¹Î±ÏÎ·Î¼Î¯ÏÎµÏÎ½, Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± ÏÏÎ½Î´ÏÎ¬Î¶Î¿ÏÎ½ ÏÎ»Î·ÏÎ¿ÏÎ¿ÏÎ¯ÎµÏ ÏÎ¿Ï ÏÏÎ»Î»Î­Î³Î¿ÏÎ½ Î±ÏÏ ÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï Î¼Îµ Î¬Î»Î»ÎµÏ ÏÎ¿Ï Î­ÏÎ¿ÏÎ½ Î±Î½ÎµÎ¾Î¬ÏÏÎ·ÏÎ± ÏÏÎ»Î»Î­Î¾ÎµÎ¹ Î±ÏÏ Î¬Î»Î»Î± Î´Î¯ÎºÏÏÎ± Î® Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´ÎµÏ ÏÏÎµÏÎ¹ÎºÎ¬ Î¼Îµ ÏÎ¹Ï Î´ÏÎ±ÏÏÎ·ÏÎ¹ÏÏÎ·ÏÎ­Ï ÏÎ±Ï ÏÏÎ¿Î½ ÏÏÎ»Î»Î¿Î¼ÎµÏÏÎ·ÏÎ® ÏÎ±Ï.","pc_trgt_text_4":"ÎÎ¬Î½ ÎµÏÎ¹Î»Î­Î¾ÎµÏÎµ Î½Î± Î±ÏÎ±Î¹ÏÎ­ÏÎµÏÎµ Î® Î½Î± Î±ÏÎµÎ½ÎµÏÎ³Î¿ÏÎ¿Î¹Î®ÏÎµÏÎµ Î±ÏÏÎ¬ ÏÎ± cookies, Î¸Î± ÏÏÎ½ÎµÏÎ¯ÏÎµÏÎµ Î½Î± Î²Î»Î­ÏÎµÏÎµ Î´Î¹Î±ÏÎ·Î¼Î¯ÏÎµÎ¹Ï, Î±Î»Î»Î¬ Î±ÏÏÎ­Ï Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± Î¼Î·Î½ ÎµÎ¯Î½Î±Î¹ ÏÎ»Î­Î¿Î½ ÏÏÎµÏÎ¹ÎºÎ­Ï Î¼Îµ ÏÎ± ÎµÎ½Î´Î¹Î±ÏÎ­ÏÎ¿Î½ÏÎ¬ ÏÎ±Ï.","pc_yprivacy_text_1":"Î Î¹Î´Î¹ÏÏÎ¹ÎºÏÏÎ·ÏÎ¬ ÏÎ±Ï ÎµÎ¯Î½Î±Î¹ ÏÎ·Î¼Î±Î½ÏÎ¹ÎºÎ® Î³Î¹Î± ÎµÎ¼Î¬Ï","pc_yprivacy_text_2":"Î¤Î± cookies ÎµÎ¯Î½Î±Î¹ ÏÎ¿Î»Ï Î¼Î¹ÎºÏÎ¬ Î±ÏÏÎµÎ¯Î± ÎºÎµÎ¹Î¼Î­Î½Î¿Ï ÏÎ¿Ï Î±ÏÎ¿Î¸Î·ÎºÎµÏÎ¿Î½ÏÎ±Î¹ ÏÏÎ¿Î½ ÏÏÎ¿Î»Î¿Î³Î¹ÏÏÎ® ÏÎ±Ï ÏÏÎ±Î½ ÎµÏÎ¹ÏÎºÎ­ÏÏÎµÏÏÎµ Î¼Î¹Î± Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±. Î§ÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î¿ÏÎ¼Îµ cookies Î³Î¹Î± Î´Î¹Î¬ÏÎ¿ÏÎ¿ÏÏ Î»ÏÎ³Î¿ÏÏ ÎºÎ±Î¹ Î³Î¹Î± Î½Î± Î²ÎµÎ»ÏÎ¹ÏÏÎ¿ÏÎ¼Îµ ÏÎ·Î½ Î´Î¹Î±Î´Î¹ÎºÏÏÎ±ÎºÎ® ÏÎ±Ï ÎµÎ¼ÏÎµÎ¹ÏÎ¯Î± ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï (Ï.Ï., Î³Î¹Î± ÏÏÎµÎ½Î¸ÏÎ¼Î¹ÏÎ· ÏÏÎ½ ÏÏÎ¿Î¹ÏÎµÎ¯ÏÎ½ ÏÏÏÏÎ²Î±ÏÎ®Ï ÏÎ±Ï ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±).","pc_yprivacy_text_3":"ÎÏÎ¿ÏÎµÎ¯ÏÎµ Î½Î± Î±Î»Î»Î¬Î¾ÎµÏÎµ ÏÎ¹Ï ÏÏÎ¿ÏÎ¹Î¼Î®ÏÎµÎ¹Ï ÏÎ±Ï ÎºÎ±Î¹ Î½Î± Î¼Î·Î½ ÎµÏÎ¹ÏÏÎ­ÏÎµÏÎµ ÏÎµ ÎºÎ¬ÏÎ¿Î¹Î¿ÏÏ ÏÏÏÎ¿ÏÏ cookies Î½Î± Î±ÏÎ¿Î¸Î·ÎºÎµÏÏÎ¿ÏÎ½ ÏÏÎ¿Î½ ÏÏÎ¿Î»Î¿Î³Î¹ÏÏÎ® ÏÎ±Ï ÏÏÎ¿ ÏÎµÏÎ¹Î·Î³ÎµÎ¯ÏÏÎµ ÏÏÎ·Î½ Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î± Î¼Î±Ï. ÎÏÎ¿ÏÎµÎ¯ÏÎµ ÎµÏÎ¯ÏÎ·Ï Î½Î± Î´Î¹Î±Î³ÏÎ¬ÏÎµÏÎµ Î¿ÏÎ¿Î¹Î±Î´Î®ÏÎ¿ÏÎµ cookies ÎµÎ¯Î½Î±Î¹ Î®Î´Î· Î±ÏÎ¿Î¸Î·ÎºÎµÏÎ¼Î­Î½Î± ÏÏÎ¿Î½ ÏÏÎ¿Î»Î¿Î³Î¹ÏÏÎ® ÏÎ±Ï, Î±Î»Î»Î¬ Î½Î± Î­ÏÎµÏÎµ ÏÏÏÏÎ¹Î½ ÏÏÎ¹ Î´Î¹Î±Î³ÏÎ¬ÏÎ¿Î½ÏÎ±Ï cookies Î¼ÏÎ¿ÏÎµÎ¯ Î½Î± ÏÎ±Ï Î±ÏÎ¿ÏÏÎ­ÏÎµÎ¹ Î±ÏÏ ÏÎ¿ Î½Î± ÏÏÎ·ÏÎ¹Î¼Î¿ÏÎ¿Î¹Î®ÏÎµÏÎµ Î¼Î­ÏÎ· ÏÎ·Ï Î¹ÏÏÎ¿ÏÎµÎ»Î¯Î´Î±Ï Î¼Î±Ï.","pc_yprivacy_title":"Î Î¹Î´Î¹ÏÏÎ¹ÎºÏÏÎ·ÏÎ¬ ÏÎ±Ï","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Î Î¿Î»Î¹ÏÎ¹ÎºÎ® Î±ÏÎ¿ÏÏÎ®ÏÎ¿Ï</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"×¤×¢××","always_active":"×ª××× ×¤×¢××","impressum":"<a href=\'%s\' target=\'_blank\'>×¨××©×</a>","inactive":"×× ×¤×¢××","nb_agree":"×× × ××¡×××/×","nb_changep":"×©× × ××ª ×××××¨××ª ×©××","nb_ok":"×××§××","nb_reject":"×× × ××¡×¨×/×ª","nb_text":"×× × ××©×ª××©×× ××¢×××××ª ××××× ×××××××ª ××¢×§× ×××¨××ª ××× ××©×¤×¨ ××ª ×××××ª ×××××©× ×©×× ×××ª×¨ ×××× ××¨× × ×©×× ×, ××× ×××¦×× ×× ×ª××× ×××ª×× ×××©××ª ×××××¢××ª ××××§×××ª, ×× ×ª× ××ª ××ª× ××¢× ×××ª×¨ ×©×× × ×××××× ××××× ××××¢×× ××××§×¨×× ×©×× ×.","nb_title":"×× × ××©×ª××©×× ××¢×××××ª","pc_fnct_text_1":"×¢×××××ª ×¤×× ×§×¦××× ××××ª","pc_fnct_text_2":"×¢×××××ª ××× ××©××©××ª ××× ××¡×¤×§ ×× ××××× ×××ª×××ª ×××©××ª ×××ª×¨ ×××ª×¨ ×××× ××¨× × ×©×× × ×××× ×××××¨ ××××¨××ª ×©××ª× ×¢××©× ××©××ª× ××©×ª××© ×××ª×¨ ×©×× ×.","pc_fnct_text_3":"××××××, ×× × ×¢×©×××× ×××©×ª××© ××¢×××××ª ×¤×× ×§×¦××× ××××ª ××× ×××××¨ ××ª ××¢××¤××ª ××©×¤× ×©×× ×× ×××××¨ ××ª ×¤×¨×× ×××ª×××¨××ª ×©××.","pc_minfo_text_1":"××××¢ × ××¡×£","pc_minfo_text_2":"××× ×©××× ×× ×××¢ ××××× ×××ª ×©×× × ×× ××©× ×§×××¦× ×¢×××××ª ××××××¨××ª ×©××, ×× × ×¦××¨ ×××ª× × ×§×©×¨.","pc_minfo_text_3":"×××××¢ × ××¡×£, ××§×¨ ×<a href=\'%s\' target=\'_blank\'>×××× ×××ª ××¤×¨××××ª</a> ×©×× ×.","pc_save":"×©×××¨ ××ª ×××¢××¤××ª ×©××","pc_sncssr_text_1":"×¢×××××ª × ×××¦××ª ××××","pc_sncssr_text_2":"×¢×××××ª ××× ×××× ×××ª ××× ××¡×¤×§ ×× ×©××¨××ª×× ××××× ×× ××¨× ×××ª×¨ ×©×× × ×××× ×××¤×©×¨ ×× ×××©×ª××© ××ª××× ××ª ××¡×××××ª ×©× ×××ª×¨ ×©×× ×.","pc_sncssr_text_3":"××× ×¢×××××ª ×××, ××× × × ×××××× ××¡×¤×§ ×× ×©××¨××ª×× ××¡××××× ×××ª×¨ ×©×× ×.","pc_title":"××¨×× ××¢××¤××ª ×¢×××××ª","pc_trck_text_1":"×¢×××××ª ××¢×§×","pc_trck_text_2":"×¢×××××ª ××× ××©××©××ª ××××¡××£ ××××¢ ××× ×× ×ª× ××ª ××ª× ××¢× ×××ª×¨ ×©×× × ××××¦× ××××§×¨×× ××©×ª××©×× ×××ª×¨ ×©×× ×.","pc_trck_text_3":"××××××, ×§×××¦× ×¢×××××ª ××× ×¢×©×××× ××¢×§×× ×××¨ ×××¨×× ×××× ××©× ×××× ×©××ª× ×××× ×××ª×¨ ×× ×××¤×× ×©××× ××ª× ×××§×¨, ×× ×©×¢×××¨ ×× × ××××× ×××¦× ×× × ×××××× ××©×¤×¨ ×¢×××¨× ××ª ××ª×¨ ×××× ××¨× × ×©×× ×.","pc_trck_text_4":"×××××¢ ×©× ××¡×£ ××××¦×¢××ª ×¢×××××ª ××¢×§× ××××¦××¢×× ××× ××× × ×××× ××£ ×××§×¨ ××××.","pc_trgt_text_1":"×¢×××××ª ×××§×× ××¤×¨×¡××","pc_trgt_text_2":"×¢×××××ª ××× ××©××©××ª ×××¦××ª ×¤×¨×¡××××ª ×©×¡×××¨ ××× ×× ×©××¢× ××× × ×××ª× ×××ª××¡×¡ ×¢× ××¨××× ×××××©× ×©××.","pc_trgt_text_3":"×§×××¦× ×¢×××××ª ×××, ××¤× ×©×××¦××× ×¢× ××× ×¡×¤×§× ××ª××× ×/×× ××¤×¨×¡×× ×©×× ×, ×¢×©×××× ××©×× ××××¢ ×©×× ××¡×¤× ××××ª×¨ ×©×× × ×¢× ××××¢ ×××¨ ×©×× ××¡×¤× ××××¤× ×¢×¦××× ××§×©××¨ ××¤×¢××××××ª ×©× ××¤××¤× ×××× ××¨× × ×©×× ××¨××× ×¨×©×ª ×××ª×¨×× ×©×××.","pc_trgt_text_4":"×× ×ª×××¨ ×××¡××¨ ×× ×××©×××ª ××ª ×§×××¦× ××××§×× ×× ×§×××¦× ××¤×¨×¡×× ××××, ×¢×××× ×ª×¨×× ×¤×¨×¡××××ª ×× ×××ª×× ×©×× ×× ×××× ×¨×××× ××××ª ×¢×××¨×.","pc_yprivacy_text_1":"××¤×¨××××ª ×©×× ××©××× ×× ×","pc_yprivacy_text_2":"×§×××¦× ×¢×××××ª ×× ×§××¦× ××§×¡× ×§×× ×× ×××× ××××××¡× ×× ××××©× ×©×× ×××©×¨ ××ª× ×××§×¨ ×××ª×¨. ×× × ××©×ª××©×× ××§×××¦× ×¢×××××ª ×××××× ×××¨××ª ×××× ××©×¤×¨ ××ª ×××××× ×××§××× ×ª ×©×× ×××ª×¨ ×××× ××¨× × ×©×× × (××××××, ××× ×××××¨ ××ª ×¤×¨×× ××× ××¡× ×××©××× ×©××).","pc_yprivacy_text_3":"××ª× ×××× ××©× ××ª ××ª ×××¢××¤××ª ×©×× ××××××ª ×¡×××× ××¡××××× ×©× ×¢×××××ª ×©××©××¨× ××××©× ×©×× ×××× ×××××©× ×××ª×¨ ×©×× ×. ××ª× ×××× ×× ×××¡××¨ ×§×××¦× ×¢×××××ª ×©×××¨ ×××××¡× ×× ××××©× ×©××, ×× ××××¨ ×©××××§×ª ×§×××¦× ×¢×××××ª ×¢×××× ××× ××¢ ××× ×××©×ª××© ××××§×× ××××ª×¨ ×©×× ×.","pc_yprivacy_title":"××¤×¨××××ª ×©××","privacy_policy":"<a href=\'%s\' target=\'_blank\'>×××× ×××ª ×¤×¨××××ª</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"ÐÐºÑÐ¸Ð²Ð½Ð¾","always_active":"Ð¡ÐµÐºÐ¾Ð³Ð°Ñ Ð°ÐºÑÐ¸Ð²Ð½Ð¾","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"ÐÐµÐ°ÐºÑÐ¸Ð²Ð½Ð¾","nb_agree":"Ð¡Ðµ ÑÐ¾Ð³Ð»Ð°ÑÑÐ²Ð°Ð¼","nb_changep":"ÐÑÐ¾Ð¼ÐµÐ½Ð¸ Ð³Ð¸ Ð¼Ð¾Ð¸ÑÐµ Ð¿ÑÐµÑÐµÑÐµÐ½ÑÐ¸Ð¸","nb_ok":"Ð¡Ðµ ÑÐ¾Ð³Ð»Ð°ÑÑÐ²Ð°Ð¼","nb_reject":"ÐÐ´Ð±Ð¸Ð²Ð°Ð¼","nb_text":"ÐÐ¸Ðµ ÐºÐ¾ÑÐ¸ÑÑÐ¸Ð¼Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð¸ Ð´ÑÑÐ³Ð¸ ÑÐµÑÐ½Ð¾Ð»Ð¾Ð³Ð¸Ð¸ Ð·Ð° ÑÐ»ÐµÐ´ÐµÑÐµ Ð·Ð° Ð´Ð° Ð³Ð¾ Ð¿Ð¾Ð´Ð¾Ð±ÑÐ¸Ð¼Ðµ Ð²Ð°ÑÐµÑÐ¾ Ð¸ÑÐºÑÑÑÐ²Ð¾ ÑÐ¾ Ð¿ÑÐµÐ»Ð¸ÑÑÑÐ²Ð°ÑÐµÑÐ¾ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°, Ð·Ð° Ð´Ð° Ð²Ð¸ Ð¿ÑÐ¸ÐºÐ°Ð¶ÐµÐ¼Ðµ Ð¿ÐµÑÑÐ¾Ð½Ð°Ð»Ð¸Ð·Ð¸ÑÐ°Ð½Ð° ÑÐ¾Ð´ÑÐ¶Ð¸Ð½Ð° Ð¸ ÑÐ°ÑÐ³ÐµÑÐ¸ÑÐ°Ð½Ð¸ ÑÐµÐºÐ»Ð°Ð¼Ð¸, Ð´Ð° Ð³Ð¾ Ð°Ð½Ð°Ð»Ð¸Ð·Ð¸ÑÐ°Ð¼Ðµ ÑÐ¾Ð¾Ð±ÑÐ°ÑÐ°ÑÐ¾Ñ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð° Ð¸ Ð´Ð° ÑÐ°Ð·Ð±ÐµÑÐµÐ¼Ðµ Ð¾Ð´ ÐºÐ°Ð´Ðµ Ð´Ð¾Ð°ÑÐ°Ð°Ñ Ð½Ð°ÑÐ¸ÑÐµ Ð¿Ð¾ÑÐµÑÐ¸ÑÐµÐ»Ð¸.","nb_title":"ÐÐ¸Ðµ ÐºÐ¾ÑÐ¸ÑÑÐ¸Ð¼Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ°","pc_fnct_text_1":"ÐÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÑÐ½ÐºÑÐ¸Ð¾Ð½Ð°Ð»Ð½Ð¾ÑÑ","pc_fnct_text_2":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° ÑÐµ ÐºÐ¾ÑÐ¸ÑÑÐ°Ñ Ð·Ð° Ð´Ð° Ð²Ð¸ Ð¾Ð²Ð¾Ð·Ð¼Ð¾Ð¶Ð°Ñ Ð¿Ð¾Ð¿ÐµÑÑÐ¾Ð½Ð°Ð»Ð¸Ð·Ð¸ÑÐ°Ð½Ð¾ Ð¸ÑÐºÑÑÑÐ²Ð¾ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð° Ð¸ Ð´Ð° Ð³Ð¸ Ð·Ð°Ð¿Ð¾Ð¼Ð½Ð°Ñ Ð¸Ð·Ð±Ð¾ÑÐ¸ÑÐµ ÑÑÐ¾ Ð³Ð¸ Ð¿ÑÐ°Ð²Ð¸ÑÐµ ÐºÐ¾Ð³Ð° ÑÐ° ÐºÐ¾ÑÐ¸ÑÑÐ¸ÑÐµ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°.","pc_fnct_text_3":"ÐÐ° Ð¿ÑÐ¸Ð¼ÐµÑ, Ð¼Ð¾Ð¶Ðµ Ð´Ð° ÐºÐ¾ÑÐ¸ÑÑÐ¸Ð¼Ðµ ÑÑÐ½ÐºÑÐ¸Ð¾Ð½Ð°Ð»Ð½Ð¸ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° Ð´Ð° Ð³Ð¸ Ð·Ð°Ð¿Ð¾Ð¼Ð½Ð¸Ð¼Ðµ Ð²Ð°ÑÐ¸ÑÐµ ÑÐ°Ð·Ð¸ÑÐ½Ð¸ Ð¿ÑÐµÑÐµÑÐµÐ½ÑÐ¸Ð¸ Ð¸Ð»Ð¸ Ð´Ð° Ð³Ð¸ Ð·Ð°Ð¿Ð¾Ð¼Ð½Ð¸Ð¼Ðµ Ð²Ð°ÑÐ¸ÑÐµ Ð´ÐµÑÐ°Ð»Ð¸ Ð·Ð° Ð½Ð°ÑÐ°Ð²ÑÐ²Ð°ÑÐµ.","pc_minfo_text_1":"ÐÐ¾Ð²ÐµÑÐµ Ð¸Ð½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ð¸","pc_minfo_text_2":"ÐÐ° Ð±Ð¸Ð»Ð¾ ÐºÐ°ÐºÐ²Ð¸ Ð¿ÑÐ°ÑÐ°ÑÐ° Ð²Ð¾ Ð²ÑÑÐºÐ° ÑÐ¾ Ð½Ð°ÑÐ°ÑÐ° Ð¿Ð¾Ð»Ð¸ÑÐ¸ÐºÐ° Ð·Ð° ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð¸ Ð²Ð°ÑÐ¸Ð¾Ñ Ð¸Ð·Ð±Ð¾Ñ, Ð²Ðµ Ð¼Ð¾Ð»Ð¸Ð¼Ðµ ÐºÐ¾Ð½ÑÐ°ÐºÑÐ¸ÑÐ°ÑÑÐµ Ð½Ðµ.","pc_minfo_text_3":"ÐÐ° Ð´Ð° Ð´Ð¾Ð·Ð½Ð°ÐµÑÐµ Ð¿Ð¾Ð²ÐµÑÐµ, Ð²Ðµ Ð¼Ð¾Ð»Ð¸Ð¼Ðµ Ð¿Ð¾ÑÐµÑÐµÑÐµ ÑÐ° Ð½Ð°ÑÐ°ÑÐ° <a href=\'%s\' target=\'_blank\'>ÐÐ¾Ð»Ð¸ÑÐ¸ÐºÐ° Ð·Ð° ÐÑÐ¸Ð²Ð°ÑÐ½Ð¾ÑÑ</a>.","pc_save":"ÐÐ°ÑÑÐ²Ð°Ñ Ð³Ð¸ Ð¼Ð¾Ð¸ÑÐµ Ð¿ÑÐµÑÐµÑÐµÐ½ÑÐ¸Ð¸","pc_sncssr_text_1":"Ð¡ÑÑÐ¾Ð³Ð¾ Ð½ÐµÐ¾Ð¿ÑÐ¾Ð´Ð½Ð¸ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ°","pc_sncssr_text_2":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° ÑÐµ Ð¾Ð´ ÑÑÑÑÐ¸Ð½ÑÐºÐ¾ Ð·Ð½Ð°ÑÐµÑÐµ Ð·Ð° Ð´Ð° Ð²Ð¸ Ð¾Ð²Ð¾Ð·Ð¼Ð¾Ð¶Ð°Ñ ÑÑÐ»ÑÐ³Ð¸ Ð´Ð¾ÑÑÐ°Ð¿Ð½Ð¸ Ð¿ÑÐµÐºÑ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°, Ð¸ Ð´Ð° Ð²Ð¸ Ð¾Ð²Ð¾Ð·Ð¼Ð¾Ð¶Ð°Ñ Ð´Ð° ÐºÐ¾ÑÐ¸ÑÑÐ¸ÑÐµ Ð¾Ð´ÑÐµÐ´ÐµÐ½Ð¸ ÑÑÐ½ÐºÑÐ¸Ð¸ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°.","pc_sncssr_text_3":"ÐÐµÐ· Ð¾Ð²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ°, Ð½Ð¸Ðµ Ð½Ðµ Ð¼Ð¾Ð¶ÐµÐ¼Ðµ Ð´Ð° Ð²Ð¸ Ð¾Ð±ÐµÐ·Ð±ÐµÐ´Ð¸Ð¼Ðµ Ð¾Ð´ÑÐµÐ´ÐµÐ½Ð¸ ÑÑÐ»ÑÐ³Ð¸ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°.","pc_title":"Ð¦ÐµÐ½ÑÐ°Ñ Ð·Ð° Ð¿ÑÐµÑÐµÑÐµÐ½ÑÐ¸ Ð·Ð° ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ°","pc_trck_text_1":"ÐÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÐ»ÐµÐ´ÐµÑÐµ","pc_trck_text_2":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° ÑÐµ ÐºÐ¾ÑÐ¸ÑÑÐ°Ñ Ð·Ð° ÑÐ¾Ð±Ð¸ÑÐ°ÑÐµ Ð¸Ð½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ð¸ Ð·Ð° Ð°Ð½Ð°Ð»Ð¸Ð·Ð° Ð½Ð° ÑÐ¾Ð¾Ð±ÑÐ°ÑÐ°ÑÐ¾Ñ ÐºÐ¾Ð½ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°, Ð¸ Ð·Ð° ÑÐ¾Ð° ÐºÐ°ÐºÐ¾ Ð¿Ð¾ÑÐµÑÐ¸ÑÐµÐ»Ð¸ÑÐµ ÑÐ° ÐºÐ¾ÑÐ¸ÑÑÐ°Ñ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°.","pc_trck_text_3":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð¼Ð¾Ð¶Ðµ Ð´Ð° ÑÐ»ÐµÐ´Ð°Ñ ÑÐ°Ð±Ð¾ÑÐ¸ ÐºÐ°ÐºÐ¾ Ð½Ð° Ð¿ÑÐ¸Ð¼ÐµÑ, ÐºÐ¾Ð»ÐºÑ Ð²ÑÐµÐ¼Ðµ Ð¿Ð¾Ð¼Ð¸Ð½ÑÐ²Ð°ÑÐµ Ð½Ð° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°ÑÐ°, Ð¸Ð»Ð¸ ÑÑÑÐ°Ð½Ð¸ÑÐ¸ÑÐµ ÑÑÐ¾ Ð³Ð¸ Ð¿Ð¾ÑÐµÑÑÐ²Ð°ÑÐµ ÑÑÐ¾ Ð½Ð¸ Ð¿Ð¾Ð¼Ð°Ð³Ð° Ð´Ð° ÑÐ°Ð·Ð±ÐµÑÐµÐ¼Ðµ ÐºÐ°ÐºÐ¾ Ð¼Ð¾Ð¶ÐµÐ¼Ðµ Ð´Ð° ÑÐ° Ð¿Ð¾Ð´Ð¾Ð±ÑÐ¸Ð¼Ðµ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð° Ð·Ð° Ð²Ð°Ñ.","pc_trck_text_4":"ÐÐ½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ð¸ÑÐµ ÑÐ¾Ð±ÑÐ°Ð½Ð¸ Ð¿ÑÐµÐºÑ Ð¾Ð²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÐ»ÐµÐ´ÐµÑÐµ Ð¸ Ð¿ÐµÑÑÐ¾ÑÐ¼Ð°Ð½ÑÐ¸ Ð½Ðµ Ð¸Ð´ÐµÐ½ÑÐ¸ÑÐ¸ÐºÑÐ²Ð°Ð°Ñ Ð¿Ð¾ÐµÐ´Ð¸Ð½ÐµÑÐ½Ð¸ Ð¿Ð¾ÑÐµÑÐ¸ÑÐµÐ»Ð¸.","pc_trgt_text_1":"ÐÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÐ°ÑÐ³ÐµÑÐ¸ÑÐ°ÑÐµ Ð¸ ÑÐµÐºÐ»Ð°Ð¼Ð¸ÑÐ°ÑÐµ","pc_trgt_text_2":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° ÑÐµ ÐºÐ¾ÑÐ¸ÑÑÐ°Ñ Ð·Ð° Ð¿ÑÐ¸ÐºÐ°Ð¶ÑÐ²Ð°ÑÐµ ÑÐµÐºÐ»Ð°Ð¼Ð¸ ÑÑÐ¾ Ð½Ð°ÑÐ²ÐµÑÐ¾ÑÐ°ÑÐ½Ð¾ ÑÐµ Ð²Ðµ Ð¸Ð½ÑÐµÑÐµÑÐ¸ÑÐ°Ð°Ñ Ð²ÑÐ· Ð¾ÑÐ½Ð¾Ð²Ð° Ð½Ð° Ð²Ð°ÑÐ¸ÑÐµ Ð½Ð°Ð²Ð¸ÐºÐ¸ Ð½Ð° Ð¿ÑÐµÐ»Ð¸ÑÑÑÐ²Ð°ÑÐµ.","pc_trgt_text_3":"ÐÐ²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ°, ÑÐµÑÐ²Ð¸ÑÐ°Ð½Ð¸ Ð¾Ð´ Ð½Ð°ÑÐ°ÑÐ° ÑÐ¾Ð´ÑÐ¶Ð¸Ð½Ð° Ð¸/Ð¸Ð»Ð¸ Ð¿ÑÐ¾Ð²Ð°ÑÐ´ÐµÑÐ¸ Ð·Ð° ÑÐµÐºÐ»Ð°Ð¼Ð¸ÑÐ°ÑÐµ, Ð¼Ð¾Ð¶Ðµ Ð´Ð° Ð³Ð¸ ÐºÐ¾Ð¼Ð±Ð¸Ð½Ð¸ÑÐ°Ð°Ñ Ð¸Ð½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ð¸ÑÐµ ÑÑÐ¾ Ð³Ð¸ ÑÐ¾Ð±ÑÐ°Ð»Ðµ Ð¾Ð´ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð° ÑÐ¾ Ð´ÑÑÐ³Ð¸ Ð¸Ð½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ð¸ ÑÑÐ¾ Ð½ÐµÐ·Ð°Ð²Ð¸ÑÐ½Ð¾ Ð³Ð¸ ÑÐ¾Ð±ÑÐ°Ð»Ðµ Ð²Ð¾ Ð²ÑÑÐºÐ° ÑÐ¾ Ð°ÐºÑÐ¸Ð²Ð½Ð¾ÑÑÐ¸ÑÐµ Ð½Ð° Ð²Ð°ÑÐ¸Ð¾Ñ Ð²ÐµÐ±-Ð¿ÑÐµÐ»Ð¸ÑÑÑÐ²Ð°Ñ Ð½Ð¸Ð· Ð½Ð¸Ð²Ð½Ð°ÑÐ° Ð¼ÑÐµÐ¶Ð° Ð½Ð° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð¸.","pc_trgt_text_4":"ÐÐºÐ¾ Ð¸Ð·Ð±ÐµÑÐµÑÐµ Ð´Ð° Ð³Ð¸ Ð¾ÑÑÑÑÐ°Ð½Ð¸ÑÐµ Ð¸Ð»Ð¸ Ð¾Ð½ÐµÐ²Ð¾Ð·Ð¼Ð¾Ð¶Ð¸ÑÐµ Ð¾Ð²Ð¸Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÐ°ÑÐ³ÐµÑÐ¸ÑÐ°ÑÐµ Ð¸Ð»Ð¸ ÑÐµÐºÐ»Ð°Ð¼Ð¸ÑÐ°ÑÐµ, ÑÃ¨ ÑÑÑÐµ ÑÐµ Ð³Ð»ÐµÐ´Ð°ÑÐµ ÑÐµÐºÐ»Ð°Ð¼Ð¸, Ð½Ð¾ ÑÐ¸Ðµ Ð¼Ð¾Ð¶ÐµÐ±Ð¸ Ð½ÐµÐ¼Ð° Ð´Ð° Ð±Ð¸Ð´Ð°Ñ ÑÐµÐ»ÐµÐ²Ð°Ð½ÑÐ½Ð¸ Ð·Ð° Ð²Ð°Ñ.","pc_yprivacy_text_1":"ÐÐ°ÑÐ°ÑÐ° Ð¿ÑÐ¸Ð²Ð°ÑÐ½Ð¾ÑÑ Ðµ Ð²Ð°Ð¶Ð½Ð° Ð·Ð° Ð½Ð°Ñ","pc_yprivacy_text_2":"ÐÐ¾Ð»Ð°ÑÐ¸ÑÐ°ÑÐ° ÑÐµ Ð¼Ð½Ð¾Ð³Ñ Ð¼Ð°Ð»Ð¸ ÑÐµÐºÑÑÑÐ°Ð»Ð½Ð¸ Ð´Ð°ÑÐ¾ÑÐµÐºÐ¸ ÑÑÐ¾ ÑÐµ ÑÐºÐ»Ð°Ð´Ð¸ÑÐ°Ð°Ñ Ð½Ð° Ð²Ð°ÑÐ¸Ð¾Ñ ÐºÐ¾Ð¼Ð¿ÑÑÑÐµÑ ÐºÐ¾Ð³Ð° Ð¿Ð¾ÑÐµÑÑÐ²Ð°ÑÐµ Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°. ÐÐ¸Ðµ ÐºÐ¾ÑÐ¸ÑÑÐ¸Ð¼Ðµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð·Ð° ÑÐ°Ð·Ð»Ð¸ÑÐ½Ð¸ ÑÐµÐ»Ð¸ Ð¸ Ð·Ð° Ð´Ð° Ð³Ð¾ Ð¿Ð¾Ð´Ð¾Ð±ÑÐ¸Ð¼Ðµ Ð²Ð°ÑÐµÑÐ¾ Ð¾Ð½Ð»Ð°ÑÐ½ Ð¸ÑÐºÑÑÑÐ²Ð¾ Ð½Ð° Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð° (Ð½Ð° Ð¿ÑÐ¸Ð¼ÐµÑ, Ð·Ð° Ð´Ð° Ð³Ð¸ Ð·Ð°Ð¿Ð¾Ð¼Ð½Ð¸Ð¼Ðµ Ð´ÐµÑÐ°Ð»Ð¸ÑÐµ Ð·Ð° Ð½Ð°ÑÐ°Ð²ÑÐ²Ð°ÑÐµ Ð½Ð° Ð²Ð°ÑÐ°ÑÐ° ÑÐ¼ÐµÑÐºÐ°).","pc_yprivacy_text_3":"ÐÐ¾Ð¶ÐµÑÐµ Ð´Ð° Ð³Ð¸ Ð¿ÑÐ¾Ð¼ÐµÐ½Ð¸ÑÐµ Ð²Ð°ÑÐ¸ÑÐµ Ð¿Ð°ÑÐ°Ð¼ÐµÑÑÐ¸ Ð¸ Ð´Ð° Ð¾Ð´Ð±Ð¸ÐµÑÐµ Ð¾Ð´ÑÐµÐ´ÐµÐ½Ð¸ Ð²Ð¸Ð´Ð¾Ð²Ð¸ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð´Ð° ÑÐµ ÑÐºÐ»Ð°Ð´Ð¸ÑÐ°Ð°Ñ Ð½Ð° Ð²Ð°ÑÐ¸Ð¾Ñ ÐºÐ¾Ð¼Ð¿ÑÑÑÐµÑ Ð´Ð¾Ð´ÐµÐºÐ° ÑÐ° Ð¿ÑÐµÐ»Ð¸ÑÑÑÐ²Ð°ÑÐµ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°. ÐÐ¾Ð¶ÐµÑÐµ Ð¸ÑÑÐ¾ ÑÐ°ÐºÐ° Ð´Ð° Ð³Ð¸ Ð¾ÑÑÑÑÐ°Ð½Ð¸ÑÐµ ÑÐ¸ÑÐµ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° ÑÑÐ¾ ÑÐµ Ð²ÐµÑÐµ Ð·Ð°ÑÑÐ²Ð°Ð½Ð¸ Ð½Ð° Ð²Ð°ÑÐ¸Ð¾Ñ ÐºÐ¾Ð¼Ð¿ÑÑÑÐµÑ, Ð½Ð¾ Ð¸Ð¼Ð°ÑÑÐµ Ð²Ð¾ Ð¿ÑÐµÐ´Ð²Ð¸Ð´ Ð´ÐµÐºÐ° Ð±ÑÐ¸ÑÐµÑÐµÑÐ¾ ÐºÐ¾Ð»Ð°ÑÐ¸ÑÐ° Ð¼Ð¾Ð¶Ðµ Ð´Ð° Ð²Ðµ ÑÐ¿ÑÐµÑÐ¸ Ð´Ð° ÐºÐ¾ÑÐ¸ÑÑÐ¸ÑÐµ Ð´ÐµÐ»Ð¾Ð²Ð¸ Ð¾Ð´ Ð½Ð°ÑÐ°ÑÐ° Ð²ÐµÐ± ÑÑÑÐ°Ð½Ð°.","pc_yprivacy_title":"ÐÐ°ÑÐ°ÑÐ° Ð¿ÑÐ¸Ð²Ð°ÑÐ½Ð¾ÑÑ","privacy_policy":"<a href=\'%s\' target=\'_blank\'>ÐÐ¾Ð»Ð¸ÑÐ¸ÐºÐ° Ð·Ð° ÐÑÐ¸Ð²Ð°ÑÐ½Ð¾ÑÑ</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Gweithredol","always_active":"Yn weithredol bob tro","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Anweithredol","nb_agree":"Rwy\'n cytuno","nb_changep":"Newid fy newisiadau","nb_ok":"Iawn","nb_reject":"Rwy\'n gwrthod","nb_text":"Rydym yn defnyddio cwcis a thechnolegau tracio eraill i wella eich profiad o bori ar ein gwefan, i ddangos cynnwys wedi ei bersonoli a hysbysebion wedi\'u targedu, i ddadansoddi traffig ar ein gwefan ac i ddeall o ble daw ein hymwelwyr.","nb_title":"Rydym yn defnyddio cwcis","pc_fnct_text_1":"Cwcis swyddogaeth","pc_fnct_text_2":"Mae\'r cwcis yma yn cael eu defnyddio i ddarparu profiad mwy personol ichi ar ein gwefan, ac i gofio dewisiadau a wnewch wrth ddefnyddio ein gwefan.","pc_fnct_text_3":"Er enghraifft, gallem ddefnyddio cwcis swyddogaeth i gofio\'ch dewis iaith neu gofio\'ch manylion mewngofnodi.","pc_minfo_text_1":"Rhagor o wybodaeth","pc_minfo_text_2":"Os oes gennych chi unrhyw ymholiadau yn ymwneud Ã¢\'n polisi cwcis a\'ch dewisiadau, a wnewch chi gysylltu Ã¢ ni.","pc_minfo_text_3":"I ganfod mwy, ewch at ein <a href=\'%s\' target=\'_blank\'>PolasaÃ­ PrÃ­obhÃ¡ideachta</a>.","pc_save":"Cadw fy newisiadau","pc_sncssr_text_1":"Cwcis hollol hanfodol","pc_sncssr_text_2":"Mae\'r cwcis yma yn hanfodol er mwyn ichi dderbyn gwasanaethau drwy ein gwefan a\'ch galluogi i ddefnyddio nodweddion penodol ar ein gwefan.","pc_sncssr_text_3":"Heb y cwcis yma, ni fedrwn ddarparu rhai gwasanaethau penodol ichi ar ein gwefan.","pc_title":"Canolfan Dewisiadau Cwcis","pc_trck_text_1":"Cwcis tracio a pherfformiad","pc_trck_text_2":"Mae\'r cwcis yma yn cael eu defnyddio i gasglu gwybodaeth a dadansoddi traffig i\'n gwefan a sut mae ymwelwyr yn defnyddio\'n gwefan.","pc_trck_text_3":"Er enghraifft, gall y cwcis yma dracio faint o amser rydych yn ei dreulio ar y wefan neu\'r tudalennau rydych yn ymweld Ã¢ hwy a\'n cynorthwyo i ddeall sut y gallwn wella ein gwefan ar eich cyfer.","pc_trck_text_4":"Nid yw\'r wybodaeth a gesglir drwy\'r cwcis tracio a pherfformiad yn adnabod unrhyw ymwelydd unigol.","pc_trgt_text_1":"Cwcis targedu a hysbysebu","pc_trgt_text_2":"Mae\'r cwcis yma yn cael eu defnyddio i ddangos hysbysebion sydd yn debygol o fod o ddiddordeb i chi yn seiliedig ar eich arferion pori.","pc_trgt_text_3":"Gall y cwcis yma, fel y\'u gweinyddir gan ein darparwyr cynnwys a/neu hysbysebion, gyfuno gwybodaeth a gasglwyd ganddynt o\'n gwefan gyda gwybodaeth arall maent wedi ei chasglu\'n annibynnol yn seiliedig ar eich gweithgareddau pori ar y rhyngrwyd ar draws eu rhwydweithiau o wefannau.","pc_trgt_text_4":"Os byddwch yn dewis tynnu neu atal y cwcis targedu neu hysbysebu yma, byddwch yn parhau i weld hysbysebion ond mae\'n bosib na fyddant yn berthnasol i chi.","pc_yprivacy_text_1":"Mae eich preifatrwydd yn bwysig i ni","pc_yprivacy_text_2":"Ffeiliau testun bach eu maint yw cwcis sydd yn cael eu storio ar eich cyfrifiadur wrth ichi ymweld Ã¢ gwefan. Rydym yn defnyddio cwcis i sawl diben ac i wella eich profiad ar-lein ar ein gwefan (er enghraifft, cofio eich manylion mewngofnodi i\'ch cyfrif).","pc_yprivacy_text_3":"Gallwch newid eich dewisiadau ac atal rhai mathau o gwcis rhag cael eu storio ar eich cyfrifiadur. Gallwch hefyd dynnu unrhyw gwcis sydd eisoes wedi eu storio ar eich cyfrifiadur, ond cofiwch y gall.","pc_yprivacy_title":"Eich preifatrwydd","privacy_policy":"<a href=\'%s\' target=\'_blank\'>PolasaÃ­ PrÃ­obhÃ¡ideachta</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"ã¢ã¯ãã£ã","always_active":"å¸¸ã«ã¢ã¯ãã£ã","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"åæ­¢ä¸­","nb_agree":"åæ","nb_changep":"è¨­å®å¤æ´","nb_ok":"æ¿è«¾","nb_reject":"æå¦","nb_text":"è¨ªåèã®å½ã¦ã§ããµã¤ãã®é²è¦§ä½é¨ãåä¸ãããããããã¼ã½ãã©ã¤ãºãããã³ã³ãã³ããã¿ã¼ã²ããåºåãè¡¨ç¤ºãããããå½ã¦ã§ããµã¤ãã®ãã©ãã£ãã¯ãåæãããããããã³å½ã¦ã§ããµã¤ãã¸ã®è¨ªåèãã©ãããæ¥ã¦ããããçè§£ããããã«ãCookieããã³ãã®ä»ã®è¿½è·¡æè¡ãä½¿ç¨ãã¦ãã¾ãã","nb_title":"ã¯ãã­ã¼ã®ä½¿ç¨","pc_fnct_text_1":"æ©è½æ§ã¯ãã­ã¼","pc_fnct_text_2":"ãããã®ã¯ãã­ã¼ã¯ãå½ã¦ã§ããµã¤ãã§ããã«ã¹ã¿ãã¤ãºãããä½é¨ãæä¾ãããããããã³å½ã¦ã§ããµã¤ããå©ç¨ããéã«è¡ã£ãé¸æãè¨æ¶ããããã«ä½¿ç¨ããã¾ãã","pc_fnct_text_3":"ä¾ãã°ãè¨ªåèã®è¨èªè¨­å®ãè¨æ¶ããããã­ã°ã¤ã³æå ±ãè¨æ¶ããããã«ãæ©è½æ§ã¯ãã­ã¼ãä½¿ç¨ãããã¨ãããã¾ãã","pc_minfo_text_1":"è©³ç´°æå ±","pc_minfo_text_2":"ã¯ãã­ã¼ã«é¢ããæ¹éãè¨ªåèã®é¸æã«é¢é£ãããè³ªåã«ã¤ãã¦ã¯ãå½æ¹ã¾ã§ãåãåãããã ããã","pc_minfo_text_3":"è©³ããã¯ã<a href=\'%s\' target=\'_blank\'>ãã©ã¤ãã·ã¼ããªã·ã¼</a> ããè¦§ãã ããã","pc_save":"è¨­å®ãä¿å­","pc_sncssr_text_1":"ã¦ã§ããµã¤ãã®åä½ã«å¿è¦ä¸å¯æ¬ ãªã¯ãã­ã¼","pc_sncssr_text_2":"ãããã®ã¯ãã­ã¼ã¯ãè¨ªåèãå½ã¦ã§ããµã¤ããéãã¦å©ç¨å¯è½ãªãµã¼ãã¹ãæä¾ããããå½ã¦ã§ããµã¤ãã®ç¹å®ã®æ©è½ãå©ç¨ãããããããã«ä¸å¯æ¬ ãªãã®ã§ãã","pc_sncssr_text_3":"ãããã®ã¯ãã­ã¼ããã­ãã¯ããå ´åãå½ã¦ã§ããµã¤ãã§ã®ç¹å®ã®ãµã¼ãã¹ãæä¾ã§ãã¾ããã","pc_title":"ã¯ãã­ã¼è¨­å®ã»ã³ã¿ã¼","pc_trck_text_1":"ãã©ãã­ã³ã°ã¯ãã­ã¼","pc_trck_text_2":"ãããã®ã¯ãã­ã¼ã¯ãå½ã¦ã§ããµã¤ãã¸ã®ãã©ãã£ãã¯ãè¨ªåèãã©ã®ããã«å½ã¦ã§ããµã¤ããå©ç¨ãã¦ããããåæããããã®æå ±ãåéããããã«ä½¿ç¨ããã¾ãã","pc_trck_text_3":"ä¾ãã°ããããã®ã¯ãã­ã¼ã¯ãè¨ªåèãå½ã¦ã§ããµã¤ãã«æ»å¨ããæéãè¨ªåãããã¼ã¸ãªã©ãè¿½è·¡ãããã¨ããããããã¯ãè¨ªåèã®ããã«å½ã¦ã§ããµã¤ãã®å©ä¾¿æ§åä¸ã«å½¹ç«ã¦ã¾ãã","pc_trck_text_4":"ãããã®ãã©ãã­ã³ã°ããã³ããã©ã¼ãã³ã¹ã¯ãã­ã¼ã«ãã£ã¦åéãããæå ±ã¯ãç¹å®ã®åäººãç¹å®ãããã¨ã¯ããã¾ããã","pc_trgt_text_1":"ã¿ã¼ã²ãã£ã³ã°ããã³åºåç¨ã¯ãã­ã¼","pc_trgt_text_2":"ãããã®ã¯ãã­ã¼ã¯ãè¨ªåèã®é²è¦§ç¿æ£ã«åºã¥ãã¦ãè¨ªåèãèå³ãæã¡ãããªåºåãè¡¨ç¤ºããããã«ä½¿ç¨ããã¾ãã","pc_trgt_text_3":"ãããã®ã¯ãã­ã¼ã¯ãã³ã³ãã³ããã­ãã¤ãã¼ããã³/ã¾ãã¯åºåãã­ãã¤ãã¼ã«ãã£ã¦æä¾ãããå½ã¦ã§ããµã¤ãããåéããæå ±ã¨ããã®ãããã¯ã¼ã¯ä¸ã§ã®è¨ªåèã®ã¦ã§ããã©ã¦ã¶ã®æ´»åã«é¢é£ãã¦ç¬èªã«åéããä»ã®æå ±ã¨ãçµã¿åããããã¨ãããã¾ãã","pc_trgt_text_4":"è¨ªåèããããã®ã¿ã¼ã²ãã£ã³ã°ã¯ãã­ã¼ãåºåç¨ã¯ãã­ã¼ãåé¤ã¾ãã¯ç¡å¹ãé¸æããå ´åã§ããåºåã¯è¡¨ç¤ºããã¾ãããè¨ªåèã«é¢é£ãããã®ã§ã¯ãªãå¯è½æ§ãããã¾ãã","pc_yprivacy_text_1":"ãå®¢æ§ã®ãã©ã¤ãã·ã¼ãå°éãã¾ã","pc_yprivacy_text_2":"ã¯ãã­ã¼ã¨ã¯ãè¨ªåèãã¦ã§ããµã¤ãã«ã¢ã¯ã»ã¹ããéã«è¨ªåèã®ã³ã³ãã¥ã¼ã¿ã«ä¿å­ãããéå¸¸ã«å°ããªãã­ã¹ããã¡ã¤ã«ã§ããå½ã¦ã§ããµã¤ãã¯ããã¾ãã¾ãªç®çã§ã¯ãã­ã¼ãä½¿ç¨ããå½ã¦ã§ããµã¤ãã§ã®è¨ªåèã®ãªã³ã©ã¤ã³å©ä¾¿æ§ãåä¸ããã¦ãã¾ããï¼ä¾ãã°ãè¨ªåèã®ã¢ã«ã¦ã³ãã®ã­ã°ã¤ã³æå ±ãè¨æ¶ãããããªã©ãï¼","pc_yprivacy_text_3":"è¨ªåèã¯ãè¨­å®ãå¤æ´ãã¦ãå½ã¦ã§ããµã¤ããé²è¦§ä¸­ã®ã³ã³ãã¥ã¼ã¿ã«ä¿å­ãããç¹å®ã®ç¨®é¡ã®ã¯ãã­ã¼ãæå¦ãããã¨ãã§ãã¾ããã¾ãããã§ã«è¨ªåèã®ã³ã³ãã¥ã¼ã¿ã«ä¿å­ããã¦ããã¯ãã­ã¼ãåé¤ãããã¨ãã§ãã¾ãããã¯ãã­ã¼ãåé¤ããã¨ãå½ã¦ã§ããµã¤ãæ©è½ã®ä¸é¨ãå©ç¨ã§ããªããªãå¯è½æ§ãããã¾ãã®ã§ããæ³¨æãã ããã","pc_yprivacy_title":"ãã©ã¤ãã·ã¼","privacy_policy":"<a href=\'%s\' target=\'_blank\'>ãã©ã¤ãã·ã¼ããªã·ã¼</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"ØªØºÙÙØ± ØªÙØ¶ÙÙØ§ØªÙ","always_active":"ÙÙØ¹Ù Ø¯Ø§Ø¦ÙÙØ§","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"ØºÙØ± ÙÙØ¹Ù","nb_agree":"ÙÙØ§ÙÙ","nb_changep":"ØªØºÙÙØ± ØªÙØ¶ÙÙØ§ØªÙ","nb_ok":"ÙÙÙØª","nb_reject":"Ø£Ø±ÙØ¶","nb_text":"ÙØ­Ù ÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØªÙÙÙØ§Øª Ø§ÙØªØªØ¨Ø¹ Ø§ÙØ£Ø®Ø±Ù ÙØªØ­Ø³ÙÙ ØªØ¬Ø±Ø¨Ø© Ø§ÙØªØµÙØ­ Ø§ÙØ®Ø§ØµØ© Ø¨Ù Ø¹ÙÙ ÙÙÙØ¹ÙØ§ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ Ø ÙÙØ¥Ø¸ÙØ§Ø± Ø§ÙÙØ­ØªÙÙ Ø§ÙÙØ®ØµØµ ÙØ§ÙØ¥Ø¹ÙØ§ÙØ§Øª Ø§ÙÙØ³ØªÙØ¯ÙØ© ÙÙ Ø ÙØªØ­ÙÙÙ Ø­Ø±ÙØ© Ø§ÙÙØ±ÙØ± Ø¹ÙÙ ÙÙÙØ¹ÙØ§ Ø ÙÙÙÙ ÙÙ Ø£ÙÙ ÙØ£ØªÙ Ø²ÙØ§Ø±ÙØ§.","nb_title":"ÙØ­ÙÙ ÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø·","pc_fnct_text_1":"ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙÙØ¸ÙÙÙØ©","pc_fnct_text_2":"ØªÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù ÙØªØ²ÙÙØ¯Ù Ø¨ØªØ¬Ø±Ø¨Ø© Ø£ÙØ«Ø± ØªØ®ØµÙØµÙØ§ Ø¹ÙÙ ÙÙÙØ¹ÙØ§ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ ÙÙØªØ°ÙØ± Ø§ÙØ®ÙØ§Ø±Ø§Øª Ø§ÙØªÙ ØªØªØ®Ø°ÙØ§ Ø¹ÙØ¯ Ø§Ø³ØªØ®Ø¯Ø§ÙÙ ÙÙÙÙØ¹ÙØ§.","pc_fnct_text_3":"Ø¹ÙÙ Ø³Ø¨ÙÙ Ø§ÙÙØ«Ø§Ù Ø ÙØ¯ ÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙÙØ¸ÙÙÙØ© ÙØªØ°ÙØ± ØªÙØ¶ÙÙØ§Øª Ø§ÙÙØºØ© Ø§ÙØ®Ø§ØµØ© Ø¨Ù Ø£Ù ØªØ°ÙØ± ØªÙØ§ØµÙÙ ØªØ³Ø¬ÙÙ Ø§ÙØ¯Ø®ÙÙ Ø§ÙØ®Ø§ØµØ© Ø¨Ù.","pc_minfo_text_1":"ÙØ¹ÙÙÙØ§Øª Ø£ÙØ«Ø±.","pc_minfo_text_2":"ÙØ£Ù Ø§Ø³ØªÙØ³Ø§Ø±Ø§Øª ØªØªØ¹ÙÙ Ø¨Ø³ÙØ§Ø³ØªÙØ§ Ø§ÙØ®Ø§ØµØ© Ø¨ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø ÙØ®ÙØ§Ø±Ø§ØªÙØ  ÙØ±Ø¬Ù Ø§ÙØªÙØ§ØµÙ ÙØ¹ÙØ§.","pc_minfo_text_3":"<a href=\'%s\' target=\'_blank\'>\\nØ§ÙØ®Ø§ØµØ© Ø¨ÙØ§ ÙÙØ¹Ø±ÙØ© Ø§ÙÙØ²ÙØ¯ Ø ÙØ±Ø¬Ù Ø²ÙØ§Ø±Ø©Ø³ÙØ§Ø³Ø© Ø§ÙØ®ØµÙØµÙØ© .\\n</a>","pc_save":"Ø­ÙØ¸ ØªÙØ¶ÙÙØ§ØªÙ","pc_sncssr_text_1":"ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙØ¶Ø±ÙØ±ÙØ© ÙÙØºØ§ÙØ©","pc_sncssr_text_2":"ØªØ¹Ø¯ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù Ø¶Ø±ÙØ±ÙØ© ÙØªØ²ÙÙØ¯Ù Ø¨Ø§ÙØ®Ø¯ÙØ§Øª Ø§ÙÙØªØ§Ø­Ø© Ø¹Ø¨Ø± ÙÙÙØ¹ÙØ§ Ø¹ÙÙ Ø§ÙÙÙØ¨ ÙÙØªÙÙÙÙÙ ÙÙ Ø§Ø³ØªØ®Ø¯Ø§Ù ÙÙØ²Ø§Øª ÙØ¹ÙÙØ© ÙÙ ÙÙÙØ¹ÙØ§ .","pc_sncssr_text_3":"Ø¨Ø¯ÙÙ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù Ø ÙØ§ ÙÙÙÙÙØ§ ØªÙØ¯ÙÙ Ø®Ø¯ÙØ§Øª ÙØ¹ÙÙØ© ÙÙ Ø¹ÙÙ ÙÙÙØ¹ÙØ§.","pc_title":"ÙØ±ÙØ² ØªÙØ¶ÙÙØ§Øª ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø·","pc_trck_text_1":"ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙÙØªØªØ¨Ø¹ ÙØ§ÙØ£Ø¯Ø§Ø¡","pc_trck_text_2":"\\nØªÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù ÙØ¬ÙØ¹ Ø§ÙÙØ¹ÙÙÙØ§Øª ÙØªØ­ÙÙÙ Ø­Ø±ÙØ© Ø§ÙÙØ±ÙØ± Ø¥ÙÙ ÙÙÙØ¹ÙØ§ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ ÙÙÙÙÙØ© Ø§Ø³ØªØ®Ø¯Ø§Ù Ø§ÙØ²ÙØ§Ø± ÙÙÙÙØ¹ÙØ§.","pc_trck_text_3":"\\nØ¹ÙÙ Ø³Ø¨ÙÙ Ø§ÙÙØ«Ø§Ù Ø ÙØ¯ ØªØªØ¹ÙØ¨ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù Ø£Ø´ÙØ§Ø¡ ÙØ«Ù Ø§ÙÙØ¯Ø© Ø§ÙØªÙ ØªÙØ¶ÙÙØ§ Ø¹ÙÙ ÙÙÙØ¹ Ø§ÙÙÙØ¨ Ø£Ù Ø§ÙØµÙØ­Ø§Øª Ø§ÙØªÙ ØªØ²ÙØ±ÙØ§ ÙÙØ§ ÙØ³Ø§Ø¹Ø¯ÙØ§ Ø¹ÙÙ ÙÙÙ ÙÙÙ ÙÙÙÙÙØ§ ØªØ­Ø³ÙÙ ÙÙÙØ¹ÙØ§ Ø¹ÙÙ Ø§ÙÙÙØ¨ ÙÙ Ø£Ø¬ÙÙ.","pc_trck_text_4":"\\nØ§ÙÙØ¹ÙÙÙØ§Øª Ø§ÙØªÙ ÙØªÙ Ø¬ÙØ¹ÙØ§ ÙÙ Ø®ÙØ§Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙØ®Ø§ØµØ© Ø¨Ø§ÙØªØªØ¨Ø¹ ÙØ§ÙØ£Ø¯Ø§Ø¡ ÙØ°Ù ÙØ§ ØªØ­Ø¯Ø¯ Ø£Ù Ø²Ø§Ø¦Ø± ÙØ±Ø¯Ù.\\n","pc_trgt_text_1":"ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙØ®Ø§ØµØ© Ø¨Ø§ÙØ§Ø³ØªÙØ¯Ø§Ù ÙØ§ÙØ¥Ø¹ÙØ§Ù","pc_trgt_text_2":"ØªÙØ³ØªØ®Ø¯Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù ÙØ¥Ø¸ÙØ§Ø± Ø§ÙØ¥Ø¹ÙØ§ÙØ§Øª Ø§ÙØªÙ ÙÙ Ø§ÙÙØ­ØªÙÙ Ø£Ù ØªÙÙÙ Ø¨ÙØ§Ø¡Ù Ø¹ÙÙ Ø¹Ø§Ø¯Ø§ØªÙ ÙÙ Ø§ÙØªØµÙØ­.","pc_trgt_text_3":"\\nÙØ¯ ØªØ¯ÙØ¬ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ°Ù Ø ÙÙØ§ ÙÙØ¯ÙÙØ§ Ø§ÙÙØ­ØªÙÙ Ù / Ø£Ù ÙÙÙØ±Ù Ø§ÙØ¥Ø¹ÙØ§ÙØ§Øª ÙØ¯ÙÙØ§ Ø Ø§ÙÙØ¹ÙÙÙØ§Øª Ø§ÙØªÙ Ø¬ÙØ¹ÙÙØ§ ÙÙ ÙÙÙØ¹ÙØ§ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ ÙØ¹ Ø§ÙÙØ¹ÙÙÙØ§Øª Ø§ÙØ£Ø®Ø±Ù Ø§ÙØªÙ Ø¬ÙØ¹ÙÙØ§ Ø¨Ø´ÙÙ ÙØ³ØªÙÙ ÙÙÙØ§ ÙØªØ¹ÙÙ Ø¨Ø£ÙØ´Ø·Ø© ÙØªØµÙØ­ Ø§ÙÙÙØ¨ Ø§ÙØ®Ø§Øµ Ø¨Ù Ø¹Ø¨Ø± Ø´Ø¨ÙØ© ÙÙØ§ÙØ¹ÙÙ Ø§ÙØ¥ÙÙØªØ±ÙÙÙØ©.\\n","pc_trgt_text_4":"Ø¥Ø°Ø§ Ø§Ø®ØªØ±Øª Ø¥Ø²Ø§ÙØ© Ø£Ù ØªØ¹Ø·ÙÙ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· Ø§ÙØ®Ø§ØµØ© Ø¨Ø§ÙØ§Ø³ØªÙØ¯Ø§Ù Ø£Ù Ø§ÙØ¥Ø¹ÙØ§ÙØ§Øª Ø ÙØ³ØªØ¸Ù ØªØ´Ø§ÙØ¯ Ø¥Ø¹ÙØ§ÙØ§Øª ÙÙÙÙÙØ§ ÙØ¯ ÙØ§ ØªÙÙÙ Ø°Ø§Øª ØµÙØ© Ø¨Ù.","pc_yprivacy_text_1":"Ø®ØµÙØµÙØªÙ ÙÙÙØ© Ø¨Ø§ÙÙØ³Ø¨Ø© ÙÙØ§","pc_yprivacy_text_2":"ÙÙ Ø§ÙØ£ØºØ±Ø§Ø¶ ÙÙØªØ¹Ø²ÙØ² ØªØ¬Ø±Ø¨ØªÙ Ø¹Ø¨Ø± Ø§ÙØ¥ÙØªØ±ÙØª Ø¹ÙÙ ÙÙÙØ¹ÙØ§ (Ø¹ÙÙ Ø³Ø¨ÙÙ Ø§ÙÙØ«Ø§Ù Ø ÙØªØ°ÙØ± ØªÙØ§ØµÙÙ ØªØ³Ø¬ÙÙ Ø§ÙØ¯Ø®ÙÙ Ø¥ÙÙ Ø­Ø³Ø§Ø¨Ù).","pc_yprivacy_text_3":"ÙÙÙÙÙ ØªØºÙÙØ± ØªÙØ¶ÙÙØ§ØªÙ ÙØ±ÙØ¶ Ø£ÙÙØ§Ø¹ ÙØ¹ÙÙØ© ÙÙ ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙÙØªÙ ØªØ®Ø²ÙÙÙØ§ Ø¹ÙÙ Ø¬ÙØ§Ø² Ø§ÙÙÙØ¨ÙÙØªØ± Ø§ÙØ®Ø§Øµ Ø¨Ù Ø£Ø«ÙØ§Ø¡ ØªØµÙØ­ ÙÙÙØ¹ÙØ§ Ø¹ÙÙ Ø§ÙÙÙØ¨.  ÙÙÙÙÙ Ø£ÙØ¶ÙØ§ Ø¥Ø²Ø§ÙØ© Ø£Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§Ø±ØªØ¨Ø§Ø· ÙØ®Ø²ÙØ© Ø¨Ø§ÙÙØ¹Ù Ø¹ÙÙ Ø¬ÙØ§Ø² Ø§ÙÙÙØ¨ÙÙØªØ± Ø§ÙØ®Ø§Øµ Ø¨Ù Ø ÙÙÙÙ Ø¶Ø¹ ÙÙ Ø§Ø¹ØªØ¨Ø§Ø±Ù Ø£Ù Ø­Ø°Ù ÙÙÙØ§Øª ØªØ¹Ø±ÙÙ Ø§ÙØ§Ø±ØªØ¨Ø§Ø· ÙØ¯ ÙÙÙØ¹Ù ÙÙ Ø§Ø³ØªØ®Ø¯Ø§Ù Ø£Ø¬Ø²Ø§Ø¡ ÙÙ ÙÙÙØ¹ÙØ§.","pc_yprivacy_title":"Ø®ØµÙØµÙØªÙ","privacy_policy":"<a href=\'%s\' target=\'_blank\'>\\nØ©Ø³ÙØ§Ø³Ø© Ø§ÙØ®ØµÙØµÙØ©\\n</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Etkin","always_active":"Her zaman etkin","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"Etkin deÄil","nb_agree":"Kabul et","nb_changep":"Tercihleri deÄiÅtir","nb_ok":"Tamam","nb_reject":"Reddet","nb_text":"Web sitemizde gezinme deneyiminizi geliÅtirmek, size kiÅiselleÅtirilmiÅ iÃ§erik ve hedefli reklamlar gÃ¶stermek, web sitesi trafiÄimizi analiz etmek ve ziyaretÃ§ilerimizin nereden geldiÄini anlamak iÃ§in Ã§erezleri ve diÄer izleme teknolojilerini kullanÄ±yoruz.","nb_title":"Ãerezleri kullanÄ±yoruz","pc_fnct_text_1":"Ä°Ålevsellik Ã§erezleri","pc_fnct_text_2":"Bu Ã§erezler, web sitemizde size daha kiÅiselleÅtirilmiÅ bir deneyim saÄlamak ve web sitemizi kullanÄ±rken yaptÄ±ÄÄ±nÄ±z seÃ§imleri hatÄ±rlamak iÃ§in kullanÄ±lÄ±r.","pc_fnct_text_3":"ÃrneÄin, dil tercihlerinizi veya oturum aÃ§ma bilgilerinizi hatÄ±rlamak iÃ§in iÅlevsellik tanÄ±mlama bilgilerini kullanabiliriz.","pc_minfo_text_1":"Daha fazla bilgi","pc_minfo_text_2":"Ãerezlere iliÅkin politikamÄ±z ve seÃ§imlerinizle ilgili herhangi bir sorunuz iÃ§in lÃ¼tfen bizimle iletiÅime geÃ§in","pc_minfo_text_3":"Daha fazlasÄ±nÄ± Ã¶Ärenmek iÃ§in lÃ¼tfen <a href=\'%s\' target=\'_blank\'>Gizlilik PolitikasÄ±</a> ziyaret edin.","pc_save":"Tercihleri Kaydet","pc_sncssr_text_1":"Kesinlikle gerekli Ã§erezler","pc_sncssr_text_2":"Bu Ã§erezler, size web sitemiz aracÄ±lÄ±ÄÄ±yla sunulan hizmetleri saÄlamak ve web sitemizin belirli Ã¶zelliklerini kullanmanÄ±zÄ± saÄlamak iÃ§in gereklidir.","pc_sncssr_text_3":"Bu Ã§erezler olmadan, web sitemizde size belirli hizmetleri saÄlayamayÄ±z.","pc_title":"Ãerez Tercihleri Merkezi","pc_trck_text_1":"Ä°zleme ve performans Ã§erezleri","pc_trck_text_2":"Bu Ã§erezler, web sitemize gelen trafiÄi ve ziyaretÃ§ilerin web sitemizi nasÄ±l kullandÄ±ÄÄ±nÄ± analiz etmek iÃ§in bilgi toplamak amacÄ±yla kullanÄ±lÄ±r.","pc_trck_text_3":"ÃrneÄin, Ã§erezler, web sitesinde ne kadar zaman geÃ§irdiÄiniz veya ziyaret ettiÄiniz sayfalar gibi Åeyleri izleyebilir ve bu da web sitemizi sizin iÃ§in nasÄ±l iyileÅtirebileceÄimizi anlamamÄ±za yardÄ±mcÄ± olur.","pc_trck_text_4":"Bu izleme ve performans Ã§erezleri aracÄ±lÄ±ÄÄ±yla toplanan bilgiler anonim olup herhangi bir bireysel ziyaretÃ§iyi tanÄ±mlamaz.","pc_trgt_text_1":"Hedefleme ve reklam Ã§erezleri","pc_trgt_text_2":"Bu Ã§erezler, arama/gezinme alÄ±ÅkanlÄ±klarÄ±nÄ±za gÃ¶re ilginizi Ã§ekebilecek reklamlarÄ± gÃ¶stermek iÃ§in kullanÄ±lÄ±r.","pc_trgt_text_3":"Bu Ã§erezler, iÃ§erik ve/veya reklam saÄlayÄ±cÄ±larÄ±mÄ±z tarafÄ±ndan, web sitemizden topladÄ±klarÄ± bilgileri, web tarayÄ±cÄ±nÄ±zÄ±n kendi web siteleri aÄlarÄ±ndaki faaliyetleriyle ilgili olarak baÄÄ±msÄ±z olarak topladÄ±klarÄ± diÄer bilgilerle birleÅtirilebilir.","pc_trgt_text_4":"Bu hedefleme veya reklam Ã§erezlerini kaldÄ±rmayÄ± veya devre dÄ±ÅÄ± bÄ±rakmayÄ± seÃ§erseniz, reklamlarÄ± gÃ¶rmeye devam edersiniz, ancak bunlar sizinle alakalÄ± olmayabilir.","pc_yprivacy_text_1":"GizliliÄiniz bizim iÃ§in Ã¶nemlidir","pc_yprivacy_text_2":"Ãerezler, bir web sitesini ziyaret ettiÄinizde bilgisayarÄ±nÄ±zda depolanan Ã§ok kÃ¼Ã§Ã¼k metin dosyalarÄ±dÄ±r. Ãerezleri Ã§eÅitli amaÃ§larla ve web sitemizdeki Ã§evrimiÃ§i deneyiminizi geliÅtirmek iÃ§in (Ã¶rneÄin, hesap giriÅ bilgilerinizi hatÄ±rlamak iÃ§in) kullanÄ±yoruz.","pc_yprivacy_text_3":"Web sitemizde gezinirken tercihlerinizi deÄiÅtirebilir ve bilgisayarÄ±nÄ±zda saklanacak belirli Ã§erez tÃ¼rlerini reddedebilirsiniz. AyrÄ±ca, bilgisayarÄ±nÄ±zda depolanmÄ±Å olan Ã§erezleri de kaldÄ±rabilirsiniz, ancak Ã§erezleri silmenin web sitemizin bÃ¶lÃ¼mlerini kullanmanÄ±zÄ± engelleyebileceÄini unutmayÄ±n.","pc_yprivacy_title":"GizliliÄiniz","privacy_policy":"<a href=\'%s\' target=\'_blank\'>Gizlilik PolitikasÄ±</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"åç¨","always_active":"æ°¸é åç¨","impressum":"<a href=\'%s\' target=\'_blank\'>Impressum</a>","inactive":"åç¨","nb_agree":"æåæ","nb_changep":"æ´æ¹æçåå¥½","nb_ok":"ç¢ºå®","nb_reject":"ææçµ","nb_text":"æåä½¿ç¨cookiesåå¶ä»è¿½è¹¤æè¡ä¾æ¹åæ¨å¨æåç¶²ç«ä¸ççè¦½é«é©ï¼å°æ¨é¡¯ç¤ºåæ§åçå§å®¹åæéå°æ§çå»£åï¼åææåçç¶²ç«æµéï¼ä¸¦äºè§£æåçè¨ªå®¢ä¾èªåªè£¡ã","nb_title":"æåä½¿ç¨cookies","pc_fnct_text_1":"åè½æ§cookies","pc_fnct_text_2":"éäºcookiesç¨æ¼å¨æåçç¶²ç«ä¸çºæ¨æä¾æ´å åäººåçé«é©ï¼ä¸¦è¨ä½æ¨å¨ä½¿ç¨æåç¶²ç«æååºçé¸æã","pc_fnct_text_3":"ä¾å¦ï¼æåå¯è½ä½¿ç¨åè½æ§cookiesä¾è¨ä½æ¨çèªè¨åå¥½æè¨ä½æ¨çç»å¥è³è¨ã","pc_minfo_text_1":"æ´å¤è³è¨","pc_minfo_text_2":"å¦æå°æåçcookiesæ¿ç­ææ¨çé¸ææä»»ä½çåï¼è«è¯ç¹«æåã","pc_minfo_text_3":"æ³äºè§£æ´å¤è³è¨ï¼è«åå¾æåç<a href=\'%s\' target=\'_blank\'>é±ç§æ¬æ¿ç­</a>.","pc_save":"å²å­æçåå¥½","pc_sncssr_text_1":"å¿è¦çcookies","pc_sncssr_text_2":"éäºcookieså°æ¼åæ¨æä¾ééæåç¶²ç«çæåä»¥åä½¿æ¨è½å¤ ä½¿ç¨æåç¶²ç«çæäºåè½æ¯ä¸å¯æç¼ºçã","pc_sncssr_text_3":"æ²æéäºcookiesï¼æåå°±ä¸è½å¨æåçç¶²ç«ä¸çºæ¨æä¾æäºæåã","pc_title":"Cookiesåå¥½ä¸­å¿","pc_trck_text_1":"è¿½è¹¤cookies","pc_trck_text_2":"éäºcookiesç¨æ¼æ¶éè³è¨ï¼ä»¥åææåç¶²ç«çæµéä»¥åè¨ªå®¢å¦ä½ä½¿ç¨æåçç¶²ç«ã","pc_trck_text_3":"ä¾å¦ï¼éäºcookieså¯è½æè·è¿½è¹¤å¦æ¨å¨ç¶²ç«ä¸è±è²»çæéææ¨é è¨ªçé é¢ï¼éæå©æ¼æåäºè§£å¦ä½çºæ¨æ¹é²æåçç¶²ç«ã","pc_trck_text_4":"éééäºè¿½è¹¤åæ§è½cookiesæ¶éçè³è¨ä¸æè­å¥ä»»ä½åäººè¨ªå®¢ã","pc_trgt_text_1":"å®ä½åå»£åcookies","pc_trgt_text_2":"éäºcookiesè¢«ç¨ä¾æ ¹ææ¨ççè¦½ç¿æ£é¡¯ç¤ºæ¨å¯è½æèè¶£çå»£åã","pc_trgt_text_3":"ç±æåçå§å®¹æå»£åä¾æåæä¾çéäºcookiesï¼å¯è½æå°ä»åå¾æåçç¶²ç«ä¸æ¶éçè³è¨åä»åç¨ç«æ¶éçèæ¨ççè¦½å¨å¨å¶ç¶²ç«ä¸­çæ´»åæéçå¶ä»è³è¨çµåèµ·ä¾ã","pc_trgt_text_4":"å¦ææ¨é¸æåªé¤æç¦ç¨éäºå®ä½æå»£åcookiesï¼æ¨ä»ç¶æçå°å»£åï¼ä½å®åå¯è½èæ¨ç¡éã","pc_yprivacy_text_1":"æ¨çé±ç§å°æåå¾éè¦","pc_yprivacy_text_2":"Cookiesæ¯éå¸¸å°çææ¬æä»¶ï¼ç¶æ¨é è¨ªç¶²ç«æå­å²å¨æ¨çè£ç½®ä¸ãæåå°cookiesç¨æ¼åç¨®ç®çï¼ä¸¦æé«æ¨å¨æåç¶²ç«çä½¿ç¨é«é©ï¼ä¾å¦ï¼è¨ä½æ¨å¸³èçç»å¥è³è¨ï¼ã","pc_yprivacy_text_3":"å¨çè¦½æåçç¶²ç«æï¼æ¨å¯ä»¥æ¹è®æ¨çåå¥½ï¼æçµæäºé¡åçcookieså²å­å¨æ¨çè£ç½®ä¸ãæ¨ä¹å¯ä»¥åªé¤å·²ç¶å²å­å¨æ¨è£ç½®ä¸çä»»ä½cookiesï¼ä½è«è¨ä½ï¼åªé¤cookieså¯è½æå°è´æ¨ç¡æ³ä½¿ç¨æåç¶²ç«çé¨åå§å®¹ã","pc_yprivacy_title":"æ¨çé±ç§","privacy_policy":"<a href=\'%s\' target=\'_blank\'>é±ç§æ¬æ¿ç­</a>"}}'
    );
  },
  function (e) {
    e.exports = JSON.parse(
      '{"i18n":{"active":"Activats","always_active":"Totjorn activats","inactive":"Desactivats","nb_agree":"AccÃ¨pti","nb_changep":"Cambiar mas preferÃ©ncias","nb_ok":"D\'acÃ²rdi","nb_reject":"RegÃ¨ti","nb_text":"Utilizam de cookies e dâautras tecnologias de seguiment per melhorar vÃ²stra experiÃ©ncia de navegacion sus nÃ²stre site web, per vos afichar de contenguts personalizats, de publicitats cibladas, per analisar nÃ²stra audiÃ©ncia e per comprendre dâont venon nÃ²stres visitaires.","nb_title":"Utilizam de cookies","pc_fnct_text_1":"Cookies foncionals","pc_fnct_text_2":"Aquestes cookies servisson per vos fornir una experiÃ©ncia mai personalizada sus nÃ²stre site web e per memorizar vÃ²stras causidas quand navegatz sus nÃ²stre site web.","pc_fnct_text_3":"Per exemple, podÃ¨m utilizar de cookies foncionals per memorizar vÃ²stras preferÃ©ncias lingÃ¼isticas o nos remembrar de vÃ²stre identificant de connexion.","pc_minfo_text_1":"Mai d\'informacions","pc_minfo_text_2":"Per quina question que siÃ¡ tocant nÃ²stra politica de cookies e vÃ²stras causidas, contactat-nos.","pc_minfo_text_3":"Per ne saber mai, consultatz nÃ²stra <a href=\'%s\' target=\'_blank\'>Politica de confidencialitat</a>.","pc_save":"Enregistrar mas preferÃ©ncias","pc_sncssr_text_1":"Cookies formalament necessaris","pc_sncssr_text_2":"Aquestes cookies son essencials per vos fornir los servicis disponibles via nÃ²stre site web e per vos permetre dâutilizar dâunas foncionalitats de nÃ²stre site web.","pc_sncssr_text_3":"Sens aquestes cookies podÃ¨m pas vos provesir certans servicis sus nÃ²stre site web.","pc_title":"Centre de preferÃ©ncias dels cookies","pc_trck_text_1":"Cookies de seguiment","pc_trck_text_2":"Aquestes cookies sâemplegan per collectar dâinformacions per analisar lo trafic de nÃ²stre site web e coma los visitaires lâutilizan.","pc_trck_text_3":"Per exemple, aquestes cookies poiriÃ¡n pistar las causas coma quant de temps passatz sus un site web o las paginas que consultatz, Ã§Ã² que nos permet de comprendre coma podÃ¨m melhorar nÃ²stre site web per vos.","pc_trck_text_4":"Las informacions collectadas via aqueles cookies de seguiment e de performÃ ncia identifican pas individualament cap de visitaire.","pc_trgt_text_1":"Cookies de ciblatge e publicitat","pc_trgt_text_2":"Aquestes cookies servisson per afichar de publicitats que vos interessarÃ n probablament basadas sus vÃ²stras costumas de navegacion.","pc_trgt_text_3":"Aquestes cookies, servits per nÃ²stres provesidors de contenguts e/o publicitats, pÃ²don combinar dâinformacions que collÃ¨ctan de nÃ²stre site web amb dâautras informacions quâan collectadas independentament en relacion amb las activitats de vÃ²stre navegador a travÃ¨rs lor malhum de sites web.","pc_trgt_text_4":"Se causissÃ¨tz de suprimir o desactivar aquestes cookies  publicitaris o de ciblatge, veiretz totjorn de reclamas mas serÃ n pas pertinentas per vos.","pc_yprivacy_text_1":"VÃ²stra vida privada nos impÃ²rta","pc_yprivacy_text_2":"Los cookies son de plan pichons fichiÃ¨rs tÃ¨xt que son gardas dins vÃ²stre ordenador quand visitatz un site. Utilizam los cookies per mantuna tÃ²ca e per melhorar vÃ²stra experiÃ©ncia en linha sus nÃ²stre site web (per exemple, per memorizar vÃ²stre identificant de connexion).","pc_yprivacy_text_3":"PodÃ¨tz modificar vÃ²stras preferÃ©ncias e regetar certans tipes de cookies de gardar dins vÃ²stre ordenador en navegant sus nÃ²stre site web. PodÃ¨tz tanben suprimir quin cookie que siÃ¡ ja gardat dins vÃ²stre ordenador, mas tenÃ¨tz a l\'esperit que la supression de cookies pÃ²t empachar dâutilizar nÃ²stre site web.","pc_yprivacy_title":"VÃ²stra confidencialitat"}}'
    );
  },
  function (e, t, i) {
    var n = i(37);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([e.i, "", ""]);
  },
  function (e, t) {
    e.exports = function (e) {
      var t = "undefined" != typeof window && window.location;
      if (!t) throw new Error("fixUrls requires window.location");
      if (!e || "string" != typeof e) return e;
      var i = t.protocol + "//" + t.host,
        n = i + t.pathname.replace(/\/[^\/]*$/, "/");
      return e.replace(
        /url\s*\(((?:[^)(]|\((?:[^)(]+|\([^)(]*\))*\))*)\)/gi,
        function (e, t) {
          var o,
            a = t
              .trim()
              .replace(/^"(.*)"$/, function (e, t) {
                return t;
              })
              .replace(/^'(.*)'$/, function (e, t) {
                return t;
              });
          return /^(#|data:|http:\/\/|https:\/\/|file:\/\/\/|\s*$)/i.test(a)
            ? e
            : ((o =
                0 === a.indexOf("//")
                  ? a
                  : 0 === a.indexOf("/")
                  ? i + a
                  : n + a.replace(/^\.\//, "")),
              "url(" + JSON.stringify(o) + ")");
        }
      );
    };
  },
  function (e, t, i) {
    var n = i(40);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      '.termsfeed-com---reset{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;-ms-overflow-style:scrollbar;-webkit-tap-highlight-color:rgba(0,0,0,0);margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-size:1rem;font-weight:400;line-height:1.5;color:#212529;text-align:left;background-color:#fff}.termsfeed-com---reset *,.termsfeed-com---reset *::before,.termsfeed-com---reset *::after{box-sizing:border-box}.termsfeed-com---reset a,.termsfeed-com---reset li,.termsfeed-com---reset p,.termsfeed-com---reset h1,.termsfeed-com---reset h2,.termsfeed-com---reset input,.termsfeed-com---reset button,.termsfeed-com---reset select{border-style:none;box-shadow:none;margin:0;padding:0;border:0;font-size:100%;font:inherit;vertical-align:baseline;outline:none}@-ms-viewport{.termsfeed-com---reset{width:device-width}}.termsfeed-com---reset [tabindex="-1"]:focus{outline:0 !important}.termsfeed-com---reset h1,.termsfeed-com---reset h2,.termsfeed-com---reset h3,.termsfeed-com---reset h4,.termsfeed-com---reset h5,.termsfeed-com---reset h6{margin-top:0;margin-bottom:0;color:#000}.termsfeed-com---reset p{margin-top:0;margin-bottom:1rem}.termsfeed-com---reset div{display:block}.termsfeed-com---reset ol,.termsfeed-com---reset ul,.termsfeed-com---reset dl{margin-top:0;margin-bottom:1rem}.termsfeed-com---reset ol ol,.termsfeed-com---reset ul ul,.termsfeed-com---reset ol ul,.termsfeed-com---reset ul ol{margin-bottom:0}.termsfeed-com---reset b,.termsfeed-com---reset strong{font-weight:bolder}.termsfeed-com---reset small{font-size:80%}.termsfeed-com---reset a{color:#007bff;text-decoration:none;background-color:rgba(0,0,0,0);-webkit-text-decoration-skip:objects}.termsfeed-com---reset a:hover{color:#0056b3;text-decoration:underline}.termsfeed-com---reset a:not([href]):not([tabindex]){color:inherit;text-decoration:none}.termsfeed-com---reset a:not([href]):not([tabindex]):hover,.termsfeed-com---reset a:not([href]):not([tabindex]):focus{color:inherit;text-decoration:none}.termsfeed-com---reset a:not([href]):not([tabindex]):focus{outline:0}.termsfeed-com---reset label{display:inline-block;margin-bottom:.5rem}.termsfeed-com---reset button{border-radius:2px;padding:.5rem 1rem;outline:none;background:#dcdae5;color:#111;cursor:pointer;border:none;transition:all ease .3s}.termsfeed-com---reset button:focus{outline:none}.termsfeed-com---reset select{border-style:none}.termsfeed-com---reset input,.termsfeed-com---reset button,.termsfeed-com---reset select,.termsfeed-com---reset optgroup,.termsfeed-com---reset textarea{margin:0;font-family:inherit;font-size:inherit;line-height:inherit}.termsfeed-com---reset button,.termsfeed-com---reset input{overflow:visible}.termsfeed-com---reset button,.termsfeed-com---reset select{text-transform:none}.termsfeed-com---reset button,.termsfeed-com---reset html [type=button],.termsfeed-com---reset [type=reset],.termsfeed-com---reset [type=submit]{-webkit-appearance:button}.termsfeed-com---reset button::-moz-focus-inner,.termsfeed-com---reset [type=button]::-moz-focus-inner,.termsfeed-com---reset [type=reset]::-moz-focus-inner,.termsfeed-com---reset [type=submit]::-moz-focus-inner{padding:0;border-style:none}.termsfeed-com---reset input[type=radio],.termsfeed-com---reset input[type=checkbox]{box-sizing:border-box;padding:0}.termsfeed-com---reset [hidden]{display:none !important}',
      "",
    ]);
  },
  function (e, t, i) {
    var n = i(42);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      '.termsfeed-com---nb{overflow:auto;z-index:99999999999;font-size:16px}.termsfeed-com---nb .cc-nb-main-container{padding:3rem}.termsfeed-com---nb .cc-nb-title{font-size:24px;font-weight:600}.termsfeed-com---nb .cc-nb-text{font-size:16px;margin:0 0 1.25rem 0}.termsfeed-com---nb .cc-nb-okagree,.termsfeed-com---nb .cc-nb-reject,.termsfeed-com---nb .cc-nb-changep{font-weight:bold;font-size:14px;margin-right:.25rem !important;margin-bottom:.25rem !important}@media(max-width: 480px){.termsfeed-com---nb .cc-nb-okagree,.termsfeed-com---nb .cc-nb-reject,.termsfeed-com---nb .cc-nb-changep{display:block;width:100%}}.termsfeed-com---nb-headline{right:0;top:auto;bottom:0;left:0;max-width:100%;position:relative}@media(max-width: 320px),(max-height: 480px){.termsfeed-com---nb-headline{overflow:auto;height:200px;max-width:100%;right:0;top:auto;bottom:0;left:auto;position:fixed}}.termsfeed-com---nb-simple{right:0;top:auto;bottom:0;left:auto;max-width:50%;position:fixed}@media screen and (max-width: 600px){.termsfeed-com---nb-simple{max-width:80%}}@media(max-width: 320px),(max-height: 480px){.termsfeed-com---nb-simple{overflow:auto;height:200px;max-width:100%}}.termsfeed-com---nb-interstitial-overlay{position:fixed;top:0;left:0;height:100%;width:100%;background:rgba(0,0,0,.8);z-index:9999999999}.termsfeed-com---nb-interstitial{right:3vw;top:3vh;left:3vw;max-width:100%;position:fixed}@media(max-width: 320px),(max-height: 480px){.termsfeed-com---nb-interstitial{overflow:auto;height:200px;right:0;top:auto;bottom:0;left:auto;position:fixed}}.termsfeed-com---nb-standalone{position:fixed;top:0;left:0;height:100%;width:100%}@media(max-width: 320px),(max-height: 480px){.termsfeed-com---nb-standalone{overflow:auto;height:200px;max-width:100%;right:0;top:auto;bottom:0;left:auto;position:fixed}}.termsfeed-com---pc-overlay{width:100%;height:100%;position:fixed;background:rgba(0,0,0,.5);z-index:999999999999;top:0;left:0;display:none}@media screen and (max-width: 600px){.termsfeed-com---pc-overlay{overflow-y:scroll}}.termsfeed-com---pc-dialog{position:absolute;margin:30px auto;width:750px;max-width:90%;height:auto;left:0;right:0}.termsfeed-com---pc-dialog>div{width:100%}.termsfeed-com---pc-dialog .cc-pc-container{width:100%;display:flex;background:#fff;flex-direction:column}.termsfeed-com---pc-dialog .cc-pc-head{background:#fff;color:#111;display:flex;flex-direction:row;justify-content:space-between}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-pc-head{flex-direction:column}}.termsfeed-com---pc-dialog .cc-pc-head-title{display:flex;padding-left:15px;flex-direction:column;justify-content:center;align-items:baseline}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-pc-head-title{align-items:center;padding:15px 0 0 0}}.termsfeed-com---pc-dialog .cc-pc-head-title-text{font-size:16px;line-height:1.5;margin:0}.termsfeed-com---pc-dialog .cc-pc-head-title-headline{font-size:20px;font-weight:600;margin:0}.termsfeed-com---pc-dialog .cc-pc-head-lang{display:flex;align-items:center;padding-right:15px;min-height:80px;justify-content:center}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-pc-head-lang{padding:15px 0;min-height:20px}}.termsfeed-com---pc-dialog .cc-pc-head-close{display:flex;align-items:center;justify-content:center;margin-left:15px}.termsfeed-com---pc-dialog .cc-cp-body{display:flex;flex-direction:row;align-items:stretch;background:#292929;color:#f5f5f5;border-bottom:none}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-cp-body{flex-direction:column}}.termsfeed-com---pc-dialog .cc-cp-body-tabs{font-family:Arial,sans-serif !important;width:150px;margin:0;padding:0;background:#e6e6e6;min-width:150px}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-cp-body-tabs{width:100%}}.termsfeed-com---pc-dialog .cc-cp-body-tabs-item{margin:0;padding:0;float:left;display:block;width:100%;color:#666;background:#e6e6e6;border-bottom:1px solid #ccc;border-right:1px solid #ccc;transition:all ease .1s;box-sizing:content-box}@media screen and (max-width: 600px){.termsfeed-com---pc-dialog .cc-cp-body-tabs-item{border-right:0}}.termsfeed-com---pc-dialog .cc-cp-body-tabs-item[active=true]{background:#292929;color:#f5f5f5}.termsfeed-com---pc-dialog .cc-cp-body-tabs-item-link{text-decoration:none;color:#666;display:block;padding:10px 5px 10px 10px;font-weight:700;font-size:12px;line-height:19px;position:relative;width:100%;text-align:left;background:none}.termsfeed-com---pc-dialog .cc-cp-body-content{background:#292929;color:#f5f5f5}.termsfeed-com---pc-dialog .cc-cp-body-content-entry{width:100%;display:none;padding:25px;box-sizing:border-box}.termsfeed-com---pc-dialog .cc-cp-body-content-entry[active=true]{display:block}.termsfeed-com---pc-dialog .cc-cp-body-content-entry-title{font-size:24px;font-weight:600}.termsfeed-com---pc-dialog .cc-cp-body-content-entry-text{font-size:16px;line-height:1.5}.termsfeed-com---pc-dialog .cc-cp-foot{background:#f2f2f2;display:flex;flex-direction:row;align-items:center;border-top:1px solid #ccc;justify-content:space-between}.termsfeed-com---pc-dialog .cc-cp-foot-byline{padding:20px 10px;font-size:14px;color:#333;display:block !important}.termsfeed-com---pc-dialog .cc-cp-foot-byline a{color:#999}.termsfeed-com---pc-dialog .cc-cp-foot-save{margin-right:10px;opacity:.9;transition:all ease .3s;font-size:14px;font-weight:bold;height:auto}.termsfeed-com---pc-dialog .cc-cp-foot-save:hover{opacity:1}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox{position:absolute;margin:2px 0 0 16px;cursor:pointer;appearance:none}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox+label{position:relative;padding:4px 0 0 50px;line-height:2em;cursor:pointer;display:inline;font-size:14px}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox+label:before{content:"";position:absolute;display:block;left:0;top:0;width:40px;height:24px;border-radius:16px;background:#fff;border:1px solid #d9d9d9;-webkit-transition:all .3s;transition:all .3s}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox+label:after{content:"";position:absolute;display:block;left:0px;top:0px;width:24px;height:24px;border-radius:16px;background:#fff;border:1px solid #d9d9d9;-webkit-transition:all .3s;transition:all .3s}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox+label:hover:after{box-shadow:0 0 5px rgba(0,0,0,.3)}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox:checked+label:after{margin-left:16px}.termsfeed-com---pc-dialog input[type=checkbox].cc-custom-checkbox:checked+label:before{background:#55d069}',
      "",
    ]);
  },
  function (e, t, i) {
    var n = i(44);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      ".termsfeed-com---palette-dark.termsfeed-com---nb{background-color:#111;color:#fff}.termsfeed-com---palette-dark .cc-nb-title{color:#fff}.termsfeed-com---palette-dark .cc-nb-text{color:#fff}.termsfeed-com---palette-dark .cc-nb-text a{color:#fff;text-decoration:underline}.termsfeed-com---palette-dark .cc-nb-text a:hover{text-decoration:none}.termsfeed-com---palette-dark .cc-nb-text a:focus{box-shadow:0 0 0 2px #3dd000}.termsfeed-com---palette-dark .cc-nb-okagree{color:#000;background-color:#ff0}.termsfeed-com---palette-dark .cc-nb-okagree:focus{box-shadow:0 0 0 2px #3dd000}.termsfeed-com---palette-dark .cc-nb-reject{color:#000;background-color:#ff0}.termsfeed-com---palette-dark .cc-nb-reject:focus{box-shadow:0 0 0 2px #3dd000}.termsfeed-com---palette-dark .cc-nb-changep{background-color:#eaeaea;color:#111}.termsfeed-com---palette-dark .cc-nb-changep:focus{box-shadow:0 0 0 2px #3dd000}.termsfeed-com---palette-dark .cc-pc-container{background:#212121}.termsfeed-com---palette-dark .cc-pc-head{background:#212121;color:#fff;border-bottom:1px solid #111}.termsfeed-com---palette-dark .cc-pc-head-title-headline{color:#fff}.termsfeed-com---palette-dark .cc-pc-head-title-text{color:#fff}.termsfeed-com---palette-dark .cc-pc-head-lang select{color:#212121}.termsfeed-com---palette-dark .cc-pc-head-lang select:focus{box-shadow:0 0 0 2px #ff0}.termsfeed-com---palette-dark .cc-pc-head-close{background:none;color:#e6e6e6}.termsfeed-com---palette-dark .cc-pc-head-close:active,.termsfeed-com---palette-dark .cc-pc-head-close:focus{border:2px solid #ff0}.termsfeed-com---palette-dark .cc-cp-body{background:#292929 !important;color:#f5f5f5}.termsfeed-com---palette-dark .cc-cp-body-tabs{color:#666;background:#e6e6e6}.termsfeed-com---palette-dark .cc-cp-body-tabs-item{border-right-color:#ccc;border-bottom-color:#ccc}.termsfeed-com---palette-dark .cc-cp-body-tabs-item-link{color:#666}.termsfeed-com---palette-dark .cc-cp-body-tabs-item-link:hover{color:#666}.termsfeed-com---palette-dark .cc-cp-body-tabs-item-link:focus{box-shadow:0 0 0 2px #292929}.termsfeed-com---palette-dark .cc-cp-body-tabs-item[active=true]{background:#292929 !important}.termsfeed-com---palette-dark .cc-cp-body-tabs-item[active=true] button{color:#f5f5f5}.termsfeed-com---palette-dark .cc-cp-body-content{background:#292929 !important;color:#f5f5f5}.termsfeed-com---palette-dark .cc-cp-body-content-entry-title{color:#fff}.termsfeed-com---palette-dark .cc-cp-body-content-entry-text{color:#fff}.termsfeed-com---palette-dark .cc-cp-body-content-entry a{color:#fff;text-decoration:underline}.termsfeed-com---palette-dark .cc-cp-body-content-entry a:hover{text-decoration:none}.termsfeed-com---palette-dark .cc-cp-body-content-entry a:focus{box-shadow:0 0 0 2px #ff0}.termsfeed-com---palette-dark .cc-cp-foot{background:#212121;border-top-color:#111}.termsfeed-com---palette-dark .cc-cp-foot-byline{color:#fff}.termsfeed-com---palette-dark .cc-cp-foot-byline a:focus{box-shadow:0 0 0 2px #ff0}.termsfeed-com---palette-dark .cc-cp-foot-save{background:#ff0;color:#000}.termsfeed-com---palette-dark .cc-cp-foot-save:focus{box-shadow:0 0 0 2px #3dd000}",
      "",
    ]);
  },
  function (e, t, i) {
    var n = i(46);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      ".termsfeed-com---palette-light.termsfeed-com---nb{background-color:#f2f2f2;color:#111}.termsfeed-com---palette-light .cc-nb-title{color:#111}.termsfeed-com---palette-light .cc-nb-text{color:#111}.termsfeed-com---palette-light .cc-nb-text a{color:#111;text-decoration:underline}.termsfeed-com---palette-light .cc-nb-text a:hover{text-decoration:none}.termsfeed-com---palette-light .cc-nb-text a:focus{box-shadow:0 0 0 2px #ff8d00}.termsfeed-com---palette-light .cc-nb-okagree{color:#fff;background-color:green}.termsfeed-com---palette-light .cc-nb-okagree:focus{box-shadow:0 0 0 2px #ff8d00}.termsfeed-com---palette-light .cc-nb-reject{color:#fff;background-color:green}.termsfeed-com---palette-light .cc-nb-reject:focus{box-shadow:0 0 0 2px #ff8d00}.termsfeed-com---palette-light .cc-nb-changep{background-color:#eaeaea;color:#111}.termsfeed-com---palette-light .cc-nb-changep:focus{box-shadow:0 0 0 2px #ff8d00}.termsfeed-com---palette-light .cc-pc-container{background:#fff}.termsfeed-com---palette-light .cc-pc-head{background:#fff;color:#111;border-bottom:1px solid #ccc}.termsfeed-com---palette-light .cc-pc-head-title-headline{color:#111}.termsfeed-com---palette-light .cc-pc-head-title-text{color:#111}.termsfeed-com---palette-light .cc-pc-head-lang select{color:#111}.termsfeed-com---palette-light .cc-pc-head-lang select:focus{box-shadow:0 0 0 2px green}.termsfeed-com---palette-light .cc-pc-head-close{background:none;color:#666}.termsfeed-com---palette-light .cc-pc-head-close:active,.termsfeed-com---palette-light .cc-pc-head-close:focus{border:2px solid green}.termsfeed-com---palette-light .cc-cp-body{background:#fbfbfb !important;color:#111}.termsfeed-com---palette-light .cc-cp-body-tabs{color:#666;background:#e6e6e6}.termsfeed-com---palette-light .cc-cp-body-tabs-item{border-right-color:#ccc;border-bottom-color:#ccc}.termsfeed-com---palette-light .cc-cp-body-tabs-item-link{color:#666}.termsfeed-com---palette-light .cc-cp-body-tabs-item-link:hover{color:#666}.termsfeed-com---palette-light .cc-cp-body-tabs-item-link:focus{box-shadow:0 0 0 2px #fbfbfb}.termsfeed-com---palette-light .cc-cp-body-tabs-item[active=true]{background:#fbfbfb !important}.termsfeed-com---palette-light .cc-cp-body-tabs-item[active=true] button{color:#111}.termsfeed-com---palette-light .cc-cp-body-content{background:#fbfbfb !important;color:#111}.termsfeed-com---palette-light .cc-cp-body-content-entry-title{color:#111}.termsfeed-com---palette-light .cc-cp-body-content-entry-text{color:#111}.termsfeed-com---palette-light .cc-cp-body-content-entry a{color:#111;text-decoration:underline}.termsfeed-com---palette-light .cc-cp-body-content-entry a:hover{text-decoration:none}.termsfeed-com---palette-light .cc-cp-body-content-entry a:focus{box-shadow:0 0 0 2px green}.termsfeed-com---palette-light .cc-cp-foot{background:#f2f2f2;border-top-color:#ccc}.termsfeed-com---palette-light .cc-cp-foot-byline{color:#111}.termsfeed-com---palette-light .cc-cp-foot-byline a:focus{box-shadow:0 0 0 2px green}.termsfeed-com---palette-light .cc-cp-foot-save{background:green;color:#fff}.termsfeed-com---palette-light .cc-cp-foot-save:focus{box-shadow:0 0 0 2px #ff8d00}",
      "",
    ]);
  },
  function (e, t, i) {
    var n = i(48);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      ".termsfeed-com---is-hidden{display:none}.termsfeed-com---is-visible{display:block}",
      "",
    ]);
  },
  function (e, t, i) {
    var n = i(50);
    "string" == typeof n && (n = [[e.i, n, ""]]);
    var o = { hmr: !0, transform: void 0, insertInto: void 0 };
    i(1)(n, o);
    n.locals && (e.exports = n.locals);
  },
  function (e, t, i) {
    (e.exports = i(0)(!1)).push([
      e.i,
      ".termsfeed-com---nb.termsfeed-com---lang-ar,.termsfeed-com---pc-overlay.termsfeed-com---lang-ar{text-align:right}",
      "",
    ]);
  },
  function (e, t, i) {
    "use strict";
    i.r(t),
      i.d(t, "run", function () {
        return pe;
      }),
      i.d(t, "cookieConsentObject", function () {
        return o;
      });
    i(36), i(39), i(41), i(43), i(45), i(47), i(49);
    var n,
      o,
      a = (function () {
        function e() {}
        return (
          (e.insertCss = function (e) {
            var t = document.querySelector("head"),
              i = document.createElement("link");
            i.setAttribute("href", e),
              i.setAttribute("rel", "stylesheet"),
              i.setAttribute("type", "text/css"),
              t.appendChild(i);
          }),
          (e.appendChild = function (e, t, i) {
            var n, o;
            return (
              void 0 === i && (i = null),
              (n = "string" == typeof e ? document.querySelector(e) : e),
              (o = "string" == typeof t ? document.querySelector(t) : t),
              "afterbegin" === i
                ? n.insertAdjacentElement("afterbegin", o)
                : n.insertAdjacentElement("beforeend", o),
              !0
            );
          }),
          (e.setCookie = function (e, t, i, n, o) {
            void 0 === o && (o = 62);
            var a = new Date();
            a.setTime(a.getTime() + 24 * o * 60 * 60 * 1e3);
            var r = "; expires=" + a.toUTCString(),
              s = "; domain=" + i,
              c = "";
            return (
              n && (c = "; Secure"),
              (document.cookie = i
                ? e + "=" + (t || "") + s + r + ";path=/; samesite=strict" + c
                : e + "=" + (t || "") + r + ";path=/; samesite=strict" + c),
              !0
            );
          }),
          (e.getCookie = function (e) {
            for (
              var t = e + "=", i = document.cookie.split(";"), n = 0;
              n < i.length;
              n++
            ) {
              for (var o = i[n]; " " === o.charAt(0); )
                o = o.substring(1, o.length);
              if (0 === o.indexOf(t)) return o.substring(t.length, o.length);
            }
            return null;
          }),
          (e.removeCookie = function (e) {
            document.cookie = e + "=; Max-Age=-99999999;";
          }),
          (e.registerEvent = function (e) {
            var t = document.createEvent("Event");
            return t.initEvent(e, !0, !0), t;
          }),
          (e.searchObjectsArray = function (e, t, i) {
            for (var n in e) {
              if (e[n][t] === i) return !0;
            }
            return !1;
          }),
          (e.magicTransform = function (e) {
            return decodeURIComponent(
              atob(e)
                .split("")
                .map(function (e) {
                  return "%" + ("00" + e.charCodeAt(0).toString(16)).slice(-2);
                })
                .join("")
            );
          }),
          (e.isValidUrl = function (e) {
            return new RegExp(
              "^(https?:\\/\\/)((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|((\\d{1,3}\\.){3}\\d{1,3}))(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*(\\?[;&a-z\\d%_.~+=-]*)?(\\#[-a-z\\d_]*)?$",
              "i"
            ).test(e);
          }),
          (e.isBoolean = function (e) {
            return !1 === e || !0 === e;
          }),
          e
        );
      })(),
      r = i(2),
      s = i(3),
      c = i(4),
      l = i(5),
      p = i(6),
      d = i(7),
      u = i(8),
      m = i(9),
      _ = i(10),
      k = i(11),
      v = i(12),
      f = i(13),
      b = i(14),
      h = i(15),
      g = i(16),
      y = i(17),
      x = i(18),
      w = i(19),
      z = i(20),
      j = i(21),
      C = i(22),
      L = i(23),
      A = i(24),
      P = i(25),
      S = i(26),
      E = i(27),
      I = i(28),
      T = i(29),
      O = i(30),
      B = i(31),
      N = i(32),
      U = i(33),
      q = i(34),
      M = i(35),
      D = (function () {
        function e(e) {
          (this.cookieConsent = e),
            (this.userLang = "en"),
            this.initAvailableLanguages(),
            this.initDefaultTranslations(),
            this.detectUserLanguage();
        }
        return (
          (e.prototype.detectUserLanguage = function () {
            var e = "en";
            if (
              void 0 !==
              (e =
                void 0 !== navigator.languages
                  ? navigator.languages[0]
                  : navigator.language)
            ) {
              if (e.indexOf("-") > 0) {
                var t = e.split("-");
                e = t[0];
              }
              this.cookieConsent.log(
                "[i18n] Detected owner website language set as: " + e,
                "info"
              );
            } else e = this.cookieConsent.ownerSiteLanguage;
            var i = e.toLowerCase.toString();
            this.availableTranslations[i]
              ? (this.userLang = i)
              : this.availableTranslations[this.cookieConsent.ownerSiteLanguage]
              ? (this.userLang = this.cookieConsent.ownerSiteLanguage)
              : (this.userLang = "en");
          }),
          (e.prototype.initDefaultTranslations = function () {
            (this.availableTranslations = {
              en: r,
              en_gb: s,
              de: c,
              fr: l,
              es: p,
              ca_es: d,
              it: u,
              sv: m,
              nl: _,
              pt: k,
              fi: v,
              hu: f,
              hr: b,
              cs: h,
              da: g,
              ro: y,
              sk: x,
              sl: w,
              pl: z,
              sr: j,
              lt: C,
              lv: L,
              ru: A,
              no: P,
              bg: S,
              el: E,
              he: I,
              mk: T,
              cy: O,
              ja: B,
              ar: N,
              tr: U,
              zh_tw: q,
              oc: M,
            }),
              this.cookieConsent.log(
                "[i18n] Default translations initialized",
                "info"
              );
          }),
          (e.prototype.initAvailableLanguages = function () {
            (this.availableLanguages = [
              { value: "en", title: "English" },
              { value: "en_gb", title: "English (UK)" },
              { value: "de", title: "German" },
              { value: "fr", title: "French" },
              { value: "es", title: "Spanish" },
              { value: "ca_es", title: "Catalan" },
              { value: "it", title: "Italian" },
              { value: "sv", title: "Swedish" },
              { value: "nl", title: "Dutch" },
              { value: "pt", title: "Portuguese" },
              { value: "fi", title: "Finnish" },
              { value: "hu", title: "Hungarian" },
              { value: "hr", title: "Croatian" },
              { value: "cs", title: "Czech" },
              { value: "da", title: "Danish" },
              { value: "ro", title: "Romanian" },
              { value: "sk", title: "Slovak" },
              { value: "sl", title: "Slovenian" },
              { value: "pl", title: "Polish" },
              { value: "sr", title: "Serbian" },
              { value: "lt", title: "Lithuanian" },
              { value: "lv", title: "Latvian" },
              { value: "ru", title: "Russian" },
              { value: "no", title: "Norwegian" },
              { value: "bg", title: "Bulgarian" },
              { value: "el", title: "Greek" },
              { value: "he", title: "Hebrew" },
              { value: "mk", title: "Macedonian" },
              { value: "cy", title: "Welsh" },
              { value: "ja", title: "Japanese" },
              { value: "ar", title: "Arabic" },
              { value: "tr", title: "Turkish" },
              { value: "zh_tw", title: "Traditional Chinese (zh-TW)" },
              { value: "oc", title: "Occitan" },
            ]),
              this.cookieConsent.log(
                "[i18n] Default languages initialized",
                "info"
              );
          }),
          (e.prototype.$t = function (e, t, i) {
            void 0 === i && (i = null);
            var n = this.availableTranslations[this.userLang][e][t];
            return (
              "string" == typeof i
                ? (n = n.replace("%s", i))
                : Array.isArray(i) &&
                  i.map(function (e, t) {
                    var o = i[t];
                    n = n.replace("%s", o);
                  }),
              n || ""
            );
          }),
          e
        );
      })(),
      J =
        ((n = function (e, t) {
          return (n =
            Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array &&
              function (e, t) {
                e.__proto__ = t;
              }) ||
            function (e, t) {
              for (var i in t) t.hasOwnProperty(i) && (e[i] = t[i]);
            })(e, t);
        }),
        function (e, t) {
          function i() {
            this.constructor = e;
          }
          n(e, t),
            (e.prototype =
              null === t
                ? Object.create(t)
                : ((i.prototype = t.prototype), new i()));
        }),
      W = function (e, t) {
        var i = "function" == typeof Symbol && e[Symbol.iterator];
        if (!i) return e;
        var n,
          o,
          a = i.call(e),
          r = [];
        try {
          for (; (void 0 === t || t-- > 0) && !(n = a.next()).done; )
            r.push(n.value);
        } catch (e) {
          o = { error: e };
        } finally {
          try {
            n && !n.done && (i = a.return) && i.call(a);
          } finally {
            if (o) throw o.error;
          }
        }
        return r;
      },
      F = function () {
        for (var e = [], t = 0; t < arguments.length; t++)
          e = e.concat(W(arguments[t]));
        return e;
      },
      R = function (e) {
        var t = "function" == typeof Symbol && Symbol.iterator,
          i = t && e[t],
          n = 0;
        if (i) return i.call(e);
        if (e && "number" == typeof e.length)
          return {
            next: function () {
              return (
                e && n >= e.length && (e = void 0),
                { value: e && e[n++], done: !e }
              );
            },
          };
        throw new TypeError(
          t ? "Object is not iterable." : "Symbol.iterator is not defined."
        );
      },
      V = (function () {
        function e(e) {
          (this.acceptedLevels = {}),
            (this.userAccepted = !1),
            (this.consentLevelCookieName = "cookie_consent_level"),
            (this.consentAcceptedCookieName = "cookie_consent_user_accepted"),
            (this.cookieConsent = e),
            this.cookieConsent.log("CookieConsent initialized", "info"),
            this.checkIfUserAccepted(),
            this.getUserLevels();
        }
        return (
          (e.prototype.checkIfUserAccepted = function () {
            "true" === a.getCookie(this.consentAcceptedCookieName) &&
              (this.userAccepted = !0);
          }),
          (e.prototype.markUserAccepted = function () {
            (this.userAccepted = !0),
              !1 === this.cookieConsent.isDemo &&
                a.setCookie(
                  this.consentAcceptedCookieName,
                  "true",
                  this.cookieConsent.ownerDomain,
                  this.cookieConsent.cookieSecure
                );
          }),
          (e.prototype.getUserLevels = function () {
            var e = a.getCookie(this.consentLevelCookieName),
              t = {};
            try {
              t = JSON.parse(decodeURIComponent(e));
            } catch (e) {
              t = null;
            }
            if (null === t)
              document.dispatchEvent(this.cookieConsent.events.cc_freshUser),
                (this.acceptedLevels["strictly-necessary"] = !0),
                "implied" === this.cookieConsent.ownerConsentType
                  ? ((this.acceptedLevels.functionality = !0),
                    (this.acceptedLevels.tracking = !0),
                    (this.acceptedLevels.targeting = !0))
                  : "express" === this.cookieConsent.ownerConsentType &&
                    ((this.acceptedLevels.functionality = !1),
                    (this.acceptedLevels.tracking = !1),
                    (this.acceptedLevels.targeting = !1));
            else
              for (var i in this.cookieConsent.cookieLevels.cookieLevels) {
                var n = this.cookieConsent.cookieLevels.cookieLevels[i].id;
                !0 === t[n]
                  ? (this.acceptedLevels[n] = !0)
                  : (this.acceptedLevels[n] = !1),
                  this.saveCookie();
              }
            this.cookieConsent.log(
              "Proposed accepted levels based on consent type are:",
              "info"
            ),
              this.cookieConsent.log(this.acceptedLevels, "info", "table");
          }),
          (e.prototype.acceptAllCookieLevels = function () {
            for (var e in this.cookieConsent.cookieLevels.cookieLevels) {
              var t = this.cookieConsent.cookieLevels.cookieLevels[e].id;
              this.acceptLevel(t);
            }
          }),
          (e.prototype.rejectAllCookieLevels = function () {
            for (var e in this.cookieConsent.cookieLevels.cookieLevels) {
              var t = this.cookieConsent.cookieLevels.cookieLevels[e].id;
              "strictly-necessary" != t
                ? this.rejectLevel(t)
                : "strictly-necessary" == t && this.acceptLevel(t);
            }
          }),
          (e.prototype.loadAcceptedCookies = function () {
            for (var e in this.cookieConsent.cookieLevels.cookieLevels) {
              var t = this.cookieConsent.cookieLevels.cookieLevels[e].id;
              !1 !== this.acceptedLevels[t] &&
                this.cookieConsent.javascriptItems.enableScriptsByLevel(t);
            }
          }),
          (e.prototype.acceptLevel = function (e) {
            return (
              this.cookieConsent.log("Accepted cookie level: " + e, "info"),
              (this.acceptedLevels[e] = !0),
              this.saveCookie()
            );
          }),
          (e.prototype.rejectLevel = function (e) {
            return (
              this.cookieConsent.log("Rejected cookie level: " + e, "info"),
              (this.acceptedLevels[e] = !1),
              this.saveCookie()
            );
          }),
          (e.prototype.saveCookie = function () {
            var e = encodeURIComponent(JSON.stringify(this.acceptedLevels));
            return (
              a.setCookie(
                this.consentLevelCookieName,
                e,
                this.cookieConsent.ownerDomain,
                this.cookieConsent.cookieSecure
              ),
              this.cookieConsent.log(
                "Saved cookie with user consent level",
                "info"
              ),
              !0
            );
          }),
          e
        );
      })(),
      K = function () {
        (this.cc_noticeBannerShown = a.registerEvent("cc_noticeBannerShown")),
          (this.cc_noticeBannerOkOrAgreePressed = a.registerEvent(
            "cc_noticeBannerOkOrAgreePressed"
          )),
          (this.cc_noticeBannerRejectPressed = a.registerEvent(
            "cc_noticeBannerRejectPressed"
          )),
          (this.cc_noticeBannerChangePreferencesPressed = a.registerEvent(
            "cc_noticeBannerChangePreferencesPressed"
          )),
          (this.cc_preferencesCenterClosePressed = a.registerEvent(
            "cc_preferencesCenterClosePressed"
          )),
          (this.cc_preferencesCenterSavePressed = a.registerEvent(
            "cc_preferencesCenterSavePressed"
          )),
          (this.cc_userLanguageChanged = a.registerEvent(
            "cc_userLanguageChanged"
          )),
          (this.cc_freshUser = a.registerEvent("cc_freshUser")),
          (this.cc_userChangedConsent = a.registerEvent(
            "cc_userChangedConsent"
          ));
      },
      $ = (function () {
        function e(e) {
          (this.scripts = {}),
            (this.cookieConsent = e),
            this.cookieConsent.log("Cookie Consent initialized", "info"),
            this.readScripts();
        }
        return (
          (e.prototype.readScripts = function () {
            var e = document.querySelectorAll('script[type="text/plain"]');
            for (var t in e) {
              var i = e[t];
              "object" == typeof i && this._noticeScriptIfValid(i);
            }
          }),
          (e.prototype._noticeScriptIfValid = function (e) {
            var t = e.getAttribute("cookie-consent");
            !0 ===
            a.searchObjectsArray(
              this.cookieConsent.cookieLevels.cookieLevels,
              "id",
              t
            )
              ? (this.cookieConsent.log(
                  "JavaScript script with valid cookie-consent tag found, but not loaded yet:",
                  "info"
                ),
                this.cookieConsent.log(e, "info"),
                void 0 === this.scripts[t] && (this.scripts[t] = []),
                this.scripts[t].push(e))
              : this.cookieConsent.log(
                  "Invalid cookie-consent tag level for JavaScript script: " +
                    t,
                  "warning"
                );
          }),
          (e.prototype.enableScriptsByLevel = function (e) {
            var t = this,
              i = function (i) {
                try {
                  var n = t.scripts[e][i],
                    o = F(n.attributes),
                    r = document.createElement("script");
                  r.setAttribute("type", "text/javascript"),
                    r.setAttribute(
                      "initial-cookie-consent",
                      n.getAttribute("cookie-consent")
                    ),
                    null !== n.getAttribute("src") &&
                      r.setAttribute("src", n.getAttribute("src")),
                    o.reduce(function (e, t) {
                      "cookie-consent" !== t.name &&
                        "type" !== t.name &&
                        r.setAttribute(t.name, t.value);
                    }, {}),
                    (r.text = n.innerHTML),
                    a.appendChild("head", r),
                    n.parentNode.removeChild(n);
                } catch (e) {
                  t.cookieConsent.log(
                    "Error while trying to enable a JavaScript script: " +
                      e.message.toString(),
                    "log"
                  );
                }
                delete t.scripts[e][i];
              };
            for (var n in t.scripts[e]) i(n);
          }),
          e
        );
      })(),
      H = (function () {
        function e(e) {
          (this.cookieConsent = e),
            this.cc_noticeBannerShown(),
            this.cc_noticeBannerOkOrAgreePressed(),
            this.cc_preferencesCenterClosePressed(),
            this.cc_noticeBannerRejectPressed(),
            this.cc_noticeBannerChangePreferencesPressed(),
            this.cc_userLanguageChanged(),
            this.cc_preferencesCenterSavePressed(),
            this.cc_freshUser(),
            this.cc_userChangedConsent();
        }
        return (
          (e.prototype.cc_noticeBannerShown = function () {
            var e = this;
            window.addEventListener("cc_noticeBannerShown", function () {
              e.cookieConsent.log("cc_noticeBannerShown triggered", "event");
            });
          }),
          (e.prototype.cc_noticeBannerOkOrAgreePressed = function () {
            var e = this;
            document.addEventListener(
              "cc_noticeBannerOkOrAgreePressed",
              function () {
                (this.userConsentTokenClass = new ce(e.cookieConsent)),
                  e.cookieConsent.log(
                    "cc_noticeBannerOkOrAgreePressed triggered",
                    "event"
                  ),
                  e.cookieConsent.userConsent.acceptAllCookieLevels(),
                  e.cookieConsent.userConsent.markUserAccepted(),
                  e.cookieConsent.userConsent.loadAcceptedCookies(),
                  e.cookieConsent.noticeBannerContainer.hideNoticeBanner(),
                  e.cookieConsent.pageRefreshConfirmationButtons &&
                    window.location.reload();
              }
            );
          }),
          (e.prototype.cc_noticeBannerRejectPressed = function () {
            var e = this;
            window.addEventListener(
              "cc_noticeBannerRejectPressed",
              function () {
                (this.userTokenClass = new ce(e.cookieConsent)),
                  e.cookieConsent.log(
                    "cc_noticeBannerRejectPressed triggered",
                    "event"
                  ),
                  e.cookieConsent.userConsent.rejectAllCookieLevels(),
                  e.cookieConsent.userConsent.markUserAccepted(),
                  e.cookieConsent.noticeBannerContainer.hideNoticeBanner(),
                  e.cookieConsent.pageRefreshConfirmationButtons &&
                    window.location.reload();
              }
            );
          }),
          (e.prototype.cc_noticeBannerChangePreferencesPressed = function () {
            var e = this;
            window.addEventListener(
              "cc_noticeBannerChangePreferencesPressed",
              function () {
                e.cookieConsent.log(
                  "cc_noticeBannerChangePreferencesPressed triggered",
                  "event"
                ),
                  e.cookieConsent.preferencesCenterContainer.showPreferencesCenter();
              }
            );
          }),
          (e.prototype.cc_userLanguageChanged = function () {
            var e = this;
            window.addEventListener("cc_userLanguageChanged", function () {
              e.cookieConsent.log("cc_userLanguageChanged triggered", "event");
            });
          }),
          (e.prototype.cc_preferencesCenterClosePressed = function () {
            var e = this;
            document.addEventListener(
              "cc_preferencesCenterClosePressed",
              function () {
                e.cookieConsent.log(
                  "cc_preferencesCenterClosePressed triggered",
                  "event"
                ),
                  e.cookieConsent.preferencesCenterContainer.hidePreferencesCenter();
              }
            );
          }),
          (e.prototype.cc_preferencesCenterSavePressed = function () {
            var e = this;
            window.addEventListener(
              "cc_preferencesCenterSavePressed",
              function () {
                (this.userConsentTokenClass = new ce(e.cookieConsent)),
                  e.cookieConsent.log(
                    "cc_preferencesCenterSavePressed triggered",
                    "event"
                  ),
                  e.cookieConsent.userConsent.markUserAccepted(),
                  e.cookieConsent.userConsent.saveCookie(),
                  e.cookieConsent.userConsent.loadAcceptedCookies(),
                  e.cookieConsent.preferencesCenterContainer.hidePreferencesCenter(),
                  e.cookieConsent.noticeBannerContainer.hideNoticeBanner(),
                  e.cookieConsent.pageRefreshConfirmationButtons &&
                    window.location.reload();
              }
            );
          }),
          (e.prototype.cc_freshUser = function () {
            var e = this;
            window.addEventListener("cc_freshUser", function () {
              e.cookieConsent.log("cc_freshUser triggered", "event");
            });
          }),
          (e.prototype.cc_userChangedConsent = function () {
            var e = this;
            window.addEventListener("cc_userChangedConsent", function () {
              e.cookieConsent.log("cc_userChangedConsent triggered", "event");
            });
          }),
          e
        );
      })(),
      G = (function () {
        function e(e) {
          (this.cookieConsent = e), this.initPreferenceItems();
        }
        return (
          (e.prototype.languageChanged = function () {
            this.initPreferenceItems();
          }),
          (e.prototype.initPreferenceItems = function () {
            var e, t;
            (this.preferenceItems = [
              {
                title: this.cookieConsent.i18n.$t("i18n", "pc_yprivacy_title"),
                title_container: "title_your_privacy",
                content_container: "content_your_privacy",
                content:
                  "<p class='cc-cp-body-content-entry-title'>" +
                  this.cookieConsent.i18n.$t("i18n", "pc_yprivacy_text_1") +
                  "</p><p class='cc-cp-body-content-entry-text'>" +
                  this.cookieConsent.i18n.$t("i18n", "pc_yprivacy_text_2") +
                  "</p><p class='cc-cp-body-content-entry-text'>" +
                  this.cookieConsent.i18n.$t("i18n", "pc_yprivacy_text_3") +
                  "</p>",
              },
            ]),
              (this.cookieLevels = [
                {
                  id: "strictly-necessary",
                  title: this.cookieConsent.i18n.$t("i18n", "pc_sncssr_text_1"),
                  content:
                    "<p class='cc-cp-body-content-entry-title'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_sncssr_text_1") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_sncssr_text_2") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_sncssr_text_3") +
                    "</p>",
                },
                {
                  id: "functionality",
                  title: this.cookieConsent.i18n.$t("i18n", "pc_fnct_text_1"),
                  content:
                    "<p class='cc-cp-body-content-entry-title'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_fnct_text_1") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_fnct_text_2") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_fnct_text_3") +
                    "</p>",
                },
                {
                  id: "tracking",
                  title: this.cookieConsent.i18n.$t("i18n", "pc_trck_text_1"),
                  content:
                    "<p class='cc-cp-body-content-entry-title'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trck_text_1") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trck_text_2") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trck_text_3") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trck_text_4") +
                    "</p>",
                },
                {
                  id: "targeting",
                  title: this.cookieConsent.i18n.$t("i18n", "pc_trgt_text_1"),
                  content:
                    "<p class='cc-cp-body-content-entry-title'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trgt_text_1") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trgt_text_2") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trgt_text_3") +
                    "</p><p class='cc-cp-body-content-entry-text'>" +
                    this.cookieConsent.i18n.$t("i18n", "pc_trgt_text_4") +
                    "</p>",
                },
              ]);
            try {
              for (
                var i = R(this.cookieLevels), n = i.next();
                !n.done;
                n = i.next()
              ) {
                var o = n.value;
                this.preferenceItems.push({
                  id: o.id,
                  title: o.title,
                  title_container: "title_" + o.id,
                  content_container: "content_" + o.id,
                  content: o.content,
                });
              }
            } catch (t) {
              e = { error: t };
            } finally {
              try {
                n && !n.done && (t = i.return) && t.call(i);
              } finally {
                if (e) throw e.error;
              }
            }
            this.preferenceItems.push({
              title: this.cookieConsent.i18n.$t("i18n", "pc_minfo_text_1"),
              title_container: "title_more_information",
              content_container: "content_more_information",
              content:
                "<p class='cc-cp-body-content-entry-title'>" +
                this.cookieConsent.i18n.$t("i18n", "pc_minfo_text_1") +
                "</p><p class='cc-cp-body-content-entry-text'>" +
                this.cookieConsent.i18n.$t("i18n", "pc_minfo_text_2") +
                "</p>",
            }),
              null !== this.cookieConsent.ownerWebsitePrivacyPolicyUrl &&
                a.isValidUrl(this.cookieConsent.ownerWebsitePrivacyPolicyUrl) &&
                (this.preferenceItems[this.preferenceItems.length - 1].content =
                  this.preferenceItems[this.preferenceItems.length - 1]
                    .content +
                  "<p class='cc-cp-body-content-entry-text'>" +
                  this.cookieConsent.i18n.$t(
                    "i18n",
                    "pc_minfo_text_3",
                    this.cookieConsent.ownerWebsitePrivacyPolicyUrl
                  ) +
                  "</p>");
          }),
          e
        );
      })(),
      Z = (function () {
        function e(e) {
          (this.preferencesCenterOverlay = null), (this.cookieConsent = e);
        }
        return (
          (e.prototype.listenToUserButtonToOpenPreferences = function (e) {
            var t = this,
              i = document.querySelectorAll(e);
            t.cookieConsent.log("userButton detected:", "info"),
              t.cookieConsent.log(i, "info", "table"),
              i &&
                i.forEach(function (e) {
                  e.addEventListener("click", function () {
                    document.dispatchEvent(
                      t.cookieConsent.events
                        .cc_noticeBannerChangePreferencesPressed
                    ),
                      t.showPreferencesCenter();
                  });
                });
          }),
          (e.prototype.showPreferencesCenter = function () {
            var e,
              t = this;
            null === this.preferencesCenterOverlay &&
              ((this.preferencesCenterOverlay =
                this.createPreferencesCenterOverlayAndDialog()),
              a.appendChild("body", this.preferencesCenterOverlay)),
              this.preferencesCenterOverlay.classList.add(
                "termsfeed-com---is-visible"
              ),
              t.cookieConsent.log("Preferences Center shown", "info"),
              this.preferencesCenterOverlay.setAttribute("role", "dialog"),
              this.preferencesCenterOverlay.setAttribute(
                "aria-labelledby",
                "cc-pc-head-title-headline"
              ),
              this.preferencesCenterOverlay.setAttribute("tabindex", "-1"),
              this.preferencesCenterOverlay.focus();
            var i = document.querySelector(
                "#termsfeed-com---preferences-center"
              ),
              n = i.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
              )[0],
              o = i.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
              ),
              r = o[o.length - 1];
            t.cookieConsent.log(
              "preferencesCenterOverlayModal_firstFocusableElement: " + n,
              "info"
            ),
              t.cookieConsent.log(
                "preferencesCenterOverlayModal_focusableContent: " + o,
                "info"
              ),
              t.cookieConsent.log(
                "preferencesCenterOverlayModal_lastFocusableElement: " + r,
                "info"
              ),
              document.addEventListener("keydown", function (e) {
                var i, o;
                ("Tab" === e.key || 9 === e.keyCode) &&
                  (e.shiftKey
                    ? document.activeElement === n &&
                      (t.cookieConsent.log(
                        "preferencesCenterOverlayModal_lastFocusableElement before focus: " +
                          r,
                        "info"
                      ),
                      null === (i = r) || void 0 === i || i.focus(),
                      e.preventDefault())
                    : document.activeElement === r &&
                      (t.cookieConsent.log(
                        "preferencesCenterOverlayModal_firstFocusableElement before focus: " +
                          n,
                        "info"
                      ),
                      null === (o = n) || void 0 === o || o.focus(),
                      e.preventDefault()));
              }),
              t.cookieConsent.log(
                "preferencesCenterOverlayModal_firstFocusableElement before focus: " +
                  n,
                "info"
              ),
              null === (e = n) || void 0 === e || e.focus(),
              this.preferencesCenterOverlay.classList.add(
                "termsfeed-com---lang-" + t.cookieConsent.i18n.userLang
              );
          }),
          (e.prototype.hidePreferencesCenter = function () {
            this.preferencesCenterOverlay.classList.remove(
              "termsfeed-com---is-visible"
            ),
              this.cookieConsent.log("Preferences Center hidden", "info");
          }),
          (e.prototype.refreshPreferencesCenter = function () {
            if (null !== this.preferencesCenterOverlay)
              return (
                this.preferencesCenterOverlay.parentNode.removeChild(
                  this.preferencesCenterOverlay
                ),
                (this.preferencesCenterOverlay = null),
                this.showPreferencesCenter()
              );
          }),
          (e.prototype.createPreferencesCenterOverlayAndDialog = function () {
            var e = this,
              t = document.createElement("div");
            t.classList.add("termsfeed-com---pc-overlay"),
              t.classList.add(e.cookieConsent.colorPalette.getClass()),
              t.classList.add("termsfeed-com---reset"),
              (t.id = "termsfeed-com---preferences-center"),
              t.setAttribute("id", "termsfeed-com---preferences-center");
            var i = document.createElement("div");
            i.classList.add("termsfeed-com---pc-dialog");
            var n = document.createElement("div");
            n.classList.add("cc-pc-container");
            var o = document.createElement("div");
            o.classList.add("cc-pc-head");
            var r = document.createElement("div");
            if (
              (r.classList.add("cc-pc-head-title"),
              e.cookieConsent.ownerWebsiteName.length > 2)
            ) {
              var s = document.createElement("p");
              s.classList.add("cc-pc-head-title-text"),
                (s.innerText = e.cookieConsent.ownerWebsiteName),
                a.appendChild(r, s);
            }
            var c = document.createElement("p");
            c.classList.add("cc-pc-head-title-headline"),
              c.setAttribute("id", "cc-pc-head-title-headline"),
              (c.innerHTML = e.cookieConsent.i18n.$t("i18n", "pc_title")),
              a.appendChild(r, c);
            var l = document.createElement("div");
            l.classList.add("cc-pc-head-lang");
            var p = this.obtainLanguageSelector();
            a.appendChild(l, p);
            var d = document.createElement("button");
            d.classList.add("cc-pc-head-close"),
              (d.innerHTML = "&#x2715;"),
              d.addEventListener("click", function () {
                document.dispatchEvent(
                  e.cookieConsent.events.cc_preferencesCenterClosePressed
                );
              }),
              a.appendChild(o, r),
              a.appendChild(o, l),
              !1 === e.cookieConsent.ownerPreferencesCenterCloseButtonHide &&
                a.appendChild(l, d, "afterend");
            var u = document.createElement("div");
            u.classList.add("cc-cp-body");
            var m = this.getMenuContainer(),
              _ = this.getContentContainer();
            a.appendChild(u, m), a.appendChild(u, _);
            var k = this.getFooterContainer();
            return (
              a.appendChild(n, o),
              a.appendChild(n, u),
              a.appendChild(n, k),
              a.appendChild(i, n),
              a.appendChild(t, i),
              t
            );
          }),
          (e.prototype.obtainLanguageSelector = function () {
            var e = this,
              t = document.createElement("select");
            return (
              t.classList.add("cc-pc-head-lang-select"),
              [].forEach.call(
                e.cookieConsent.i18n.availableLanguages,
                function (i) {
                  var n = document.createElement("option");
                  (n.text = i.title),
                    (n.value = i.value),
                    e.cookieConsent.i18n.userLang === n.value &&
                      n.setAttribute("selected", "selected"),
                    t.add(n);
                }
              ),
              t.addEventListener("change", function () {
                (e.cookieConsent.i18n.userLang = t.value),
                  e.cookieConsent.cookieLevels.languageChanged(),
                  e.refreshPreferencesCenter(),
                  document.dispatchEvent(
                    e.cookieConsent.events.cc_userLanguageChanged
                  );
              }),
              t
            );
          }),
          (e.prototype.getContentContainer = function () {
            var e = this,
              t = document.createElement("div");
            t.classList.add("cc-cp-body-content");
            var i = 0;
            return (
              e.cookieConsent.cookieLevels.preferenceItems.forEach(function (
                n
              ) {
                var o = document.createElement("div");
                if (
                  (o.classList.add("cc-cp-body-content-entry"),
                  o.setAttribute("id", n.content_container),
                  o.setAttribute("role", "tabpanel"),
                  o.setAttribute("aria-labelledby", n.title_container),
                  o.setAttribute("hidden", ""),
                  o.setAttribute("tabindex", "0"),
                  o.setAttribute("content_layout", n.content_container),
                  o.setAttribute("active", "false"),
                  (o.innerHTML = n.content),
                  0 === i &&
                    (o.setAttribute("active", "true"),
                    o.removeAttribute("hidden")),
                  i++,
                  n.id)
                ) {
                  var r = e._getLevelCheckbox(n);
                  a.appendChild(o, r);
                }
                a.appendChild(t, o);
              }),
              t
            );
          }),
          (e.prototype.getMenuContainer = function () {
            var e = this,
              t = document.createElement("ul");
            t.classList.add("cc-cp-body-tabs"),
              t.setAttribute("role", "tablist"),
              t.setAttribute("aria-label", "Menu");
            var i = 0;
            return (
              e.cookieConsent.cookieLevels.preferenceItems.forEach(function (
                n
              ) {
                var o = document.createElement("li");
                o.classList.add("cc-cp-body-tabs-item");
                var r = document.createElement("button");
                r.classList.add("cc-cp-body-tabs-item-link"),
                  r.setAttribute("id", n.title_container),
                  r.setAttribute("role", "tab"),
                  r.setAttribute("aria-selected", "false"),
                  r.setAttribute("aria-controls", n.content_container),
                  r.setAttribute("tabindex", "-1"),
                  r.setAttribute("t", n.content_container),
                  (r.innerHTML = n.title),
                  0 === i &&
                    (o.setAttribute("active", "true"),
                    r.setAttribute("aria-selected", "true"),
                    r.setAttribute("tabindex", "0")),
                  i++,
                  r.addEventListener("click", function (t) {
                    t.preventDefault(),
                      e.cookieConsent.log(
                        "Preferences Center tab item clicked: " + n.title,
                        "info"
                      );
                    var i = document.querySelectorAll('li[active="true"]');
                    [].forEach.call(i, function (e) {
                      e.setAttribute("active", "false"),
                        e.firstElementChild.setAttribute(
                          "aria-selected",
                          "false"
                        ),
                        e.firstElementChild.setAttribute("tabindex", "-1");
                    }),
                      o.setAttribute("active", "true"),
                      o.firstElementChild.setAttribute("aria-selected", "true"),
                      o.firstElementChild.setAttribute("tabindex", "0");
                    try {
                      var a = document.querySelectorAll("div[content_layout]");
                      [].forEach.call(a, function (e) {
                        e.setAttribute("active", "false"),
                          e.setAttribute("hidden", "");
                      });
                      var r = document.querySelector(
                        'div[content_layout="' + n.content_container + '"]'
                      );
                      r.setAttribute("active", "true"),
                        r.removeAttribute("hidden");
                    } catch (t) {}
                  });
                var s = 0,
                  c = document.getElementsByClassName(
                    "cc-cp-body-tabs-item-link"
                  );
                t.addEventListener("keydown", function (e) {
                  ("ArrowDown" !== e.key &&
                    "ArrowUp" !== e.key &&
                    "ArrowLeft" !== e.key &&
                    "ArrowRight" !== e.key) ||
                    (c[s].setAttribute("tabindex", "-1"),
                    "ArrowDown" === e.key || "ArrowRight" === e.key
                      ? ++s >= c.length && (s = 0)
                      : ("ArrowUp" !== e.key && "ArrowLeft" !== e.key) ||
                        (--s < 0 && (s = c.length - 1)),
                    c[s].setAttribute("tabindex", "0"),
                    c[s].focus());
                }),
                  a.appendChild(o, r),
                  a.appendChild(t, o);
              }),
              t
            );
          }),
          (e.prototype.getFooterContainer = function () {
            var e = this,
              t = document.createElement("div");
            t.classList.add("cc-cp-foot");
            var i = document.createElement("div");
            i.classList.add("cc-cp-foot-byline"),
              (i.innerHTML = a.magicTransform(
                "Q29va2llIENvbnNlbnQgYnkgPGEgaHJlZj0iaHR0cHM6Ly93d3cudGVybXNmZWVkLmNvbS9jb29raWUtY29uc2VudC8iIHRhcmdldD0iX2JsYW5rIj5UZXJtc0ZlZWQ8L2E+"
              ));
            var n = document.createElement("div");
            n.classList.add("cc-cp-foot-button");
            var o = document.createElement("button");
            return (
              o.classList.add("cc-cp-foot-save"),
              (o.innerHTML = e.cookieConsent.i18n.$t("i18n", "pc_save")),
              o.addEventListener("click", function () {
                document.dispatchEvent(
                  e.cookieConsent.events.cc_preferencesCenterSavePressed
                );
              }),
              a.appendChild(n, o),
              a.appendChild(t, i),
              a.appendChild(t, n),
              t
            );
          }),
          (e.prototype._getLevelCheckbox = function (e) {
            var t = this,
              i = document.createElement("div");
            if (
              (i.classList.add("cc-custom-checkbox"),
              "strictly-necessary" !== e.id)
            ) {
              var n = t.cookieConsent.userConsent.acceptedLevels,
                o = document.createElement("input");
              o.setAttribute("cookie_consent_toggler", "true"),
                o.setAttribute("type", "checkbox"),
                o.setAttribute("class", "cc-custom-checkbox"),
                o.setAttribute("id", e.id),
                o.setAttribute("name", e.id),
                o.setAttribute("aria-labelledby", e.id + "_label"),
                (r = document.createElement("label")).setAttribute("for", e.id),
                r.setAttribute("id", e.id + "_label"),
                n[e.id]
                  ? (o.setAttribute("checked", "checked"),
                    o.setAttribute("aria-checked", "true"),
                    r.setAttribute("class", "is-active"),
                    (r.innerHTML = t.cookieConsent.i18n.$t("i18n", "active")))
                  : (o.setAttribute("aria-checked", "false"),
                    r.setAttribute("class", "is-inactive"),
                    (r.innerHTML = t.cookieConsent.i18n.$t(
                      "i18n",
                      "inactive"
                    ))),
                o.addEventListener("change", function () {
                  var i = o.checked,
                    n = e.id,
                    a = document.querySelector('label[for="' + n + '"]');
                  t.cookieConsent.log(
                    "User changed cookie level [" + n + "], new status: " + i,
                    "info"
                  ),
                    document.dispatchEvent(
                      t.cookieConsent.events.cc_userChangedConsent
                    ),
                    !0 === i
                      ? (t.cookieConsent.userConsent.acceptLevel(n),
                        (a.innerHTML = t.cookieConsent.i18n.$t(
                          "i18n",
                          "active"
                        )))
                      : (t.cookieConsent.userConsent.rejectLevel(n),
                        (a.innerHTML = t.cookieConsent.i18n.$t(
                          "i18n",
                          "inactive"
                        )));
                }),
                o.addEventListener("keypress", function (e) {
                  if (" " === e.key || "Spacebar" === e.key)
                    switch (o.getAttribute("aria-checked")) {
                      case "true":
                        o.setAttribute("aria-checked", "false");
                        break;
                      case "false":
                        o.setAttribute("aria-checked", "true");
                    }
                }),
                a.appendChild(i, o),
                a.appendChild(i, r);
            } else {
              var r,
                s = document.createElement("input");
              s.setAttribute("cookie_consent_toggler", "true"),
                s.setAttribute("type", "checkbox"),
                s.setAttribute("checked", "checked"),
                s.setAttribute("aria-checked", "true"),
                s.setAttribute("disabled", "disabled"),
                s.setAttribute("class", "cc-custom-checkbox"),
                s.setAttribute("id", e.id),
                s.setAttribute("name", e.id),
                s.setAttribute("aria-labelledby", e.id + "_label"),
                s.setAttribute("tabindex", "0"),
                (r = document.createElement("label")).setAttribute("for", e.id),
                r.setAttribute("id", e.id + "_label"),
                (r.innerHTML = t.cookieConsent.i18n.$t(
                  "i18n",
                  "always_active"
                )),
                a.appendChild(i, s),
                a.appendChild(i, r);
            }
            return i;
          }),
          e
        );
      })(),
      Y = (function () {
        function e(e) {
          (this.noticeBanner = null),
            (this.noticeBannerOverlay = null),
            (this.noticeBannerExtraCss = []),
            (this.cookieConsent = e),
            this.noticeBannerExtraCss.push(e.colorPalette.getClass());
        }
        return (
          (e.prototype.initNoticeBanner = function () {
            var e, t;
            if (
              (null === this.noticeBanner &&
                (this.noticeBanner = this.createNoticeBanner()),
              (t =
                "afterbegin" ===
                  this.cookieConsent.ownerNoticeBannerAppendContentPosition ||
                "beforeend" ===
                  this.cookieConsent.ownerNoticeBannerAppendContentPosition
                  ? this.cookieConsent.ownerNoticeBannerAppendContentPosition
                  : "afterbegin"),
              a.appendChild("body", this.noticeBanner, t),
              this.cookieConsent.log("Notice Banner shown " + t, "info"),
              document.dispatchEvent(
                this.cookieConsent.events.cc_noticeBannerShown
              ),
              "interstitial" === this.cookieConsent.ownerNoticeBannerType ||
                "standalone" === this.cookieConsent.ownerNoticeBannerType)
            ) {
              var i = document.querySelector("#termsfeed-com---nb"),
                n = i.querySelectorAll(
                  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                )[0],
                o = i.querySelectorAll(
                  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                ),
                r = o[o.length - 1];
              document.addEventListener("keydown", function (e) {
                var t, i;
                ("Tab" === e.key || 9 === e.keyCode) &&
                  (e.shiftKey
                    ? document.activeElement === n &&
                      (null === (t = r) || void 0 === t || t.focus(),
                      e.preventDefault())
                    : document.activeElement === r &&
                      (null === (i = n) || void 0 === i || i.focus(),
                      e.preventDefault()));
              }),
                null === (e = n) || void 0 === e || e.focus();
            }
            return !0;
          }),
          (e.prototype.hideNoticeBanner = function () {
            try {
              this.noticeBanner.classList.add("termsfeed-com---is-hidden"),
                this.cookieConsent.log("Notice Banner hidden", "info");
            } catch (e) {}
          }),
          (e.prototype.createNoticeBanner = function () {
            var e,
              t,
              i = document.createElement("div");
            if (
              (i.classList.add("termsfeed-com---reset"),
              i.classList.add("termsfeed-com---nb"),
              i.setAttribute("id", "termsfeed-com---nb"),
              i.setAttribute("role", "dialog"),
              i.setAttribute("aria-modal", "true"),
              i.setAttribute("aria-labelledby", "cc-nb-title"),
              i.setAttribute("aria-describedby", "cc-nb-text"),
              this.noticeBannerExtraCss.length)
            )
              try {
                for (
                  var n = R(this.noticeBannerExtraCss), o = n.next();
                  !o.done;
                  o = n.next()
                ) {
                  var r = o.value;
                  i.classList.add(r);
                }
              } catch (t) {
                e = { error: t };
              } finally {
                try {
                  o && !o.done && (t = n.return) && t.call(n);
                } finally {
                  if (e) throw e.error;
                }
              }
            if (
              (i.classList.add(
                "termsfeed-com---lang-" + this.cookieConsent.i18n.userLang
              ),
              a.appendChild(i, this.createNoticeBannerContent()),
              "interstitial" === this.cookieConsent.ownerNoticeBannerType)
            ) {
              var s = document.createElement("div");
              return (
                s.classList.add("termsfeed-com---nb-interstitial-overlay"),
                a.appendChild(s, i),
                s
              );
            }
            return i;
          }),
          (e.prototype.createNoticeBannerContent = function () {
            var e = this,
              t = document.createElement("div");
            t.classList.add("cc-nb-main-container");
            var i = document.createElement("div");
            i.classList.add("cc-nb-title-container");
            var n = document.createElement("p");
            n.classList.add("cc-nb-title"),
              n.setAttribute("id", "cc-nb-title"),
              (n.innerText = e.cookieConsent.i18n.$t("i18n", "nb_title")),
              a.appendChild(i, n);
            var o = document.createElement("div");
            o.classList.add("cc-nb-text-container");
            var r = document.createElement("p");
            r.classList.add("cc-nb-text"),
              r.setAttribute("id", "cc-nb-text"),
              (r.innerHTML = e.cookieConsent.i18n.$t("i18n", "nb_text"));
            var s = document.createElement("span");
            s.classList.add("cc-nb-text-urls"), (s.innerHTML = " ");
            var c = document.createElement("span");
            c.classList.add("cc-nb-text-urls-privacy"),
              c.setAttribute("role", "link");
            var l = document.createElement("span");
            l.classList.add("cc-nb-text-urls-impressum"),
              l.setAttribute("role", "link");
            var p = document.createElement("span");
            p.classList.add("cc-nb-text-urls-separator"),
              (p.innerHTML = " | "),
              e.cookieConsent.noticeBannerInsertLegalUrls &&
                (e.cookieConsent.ownerWebsitePrivacyPolicyUrl &&
                e.cookieConsent.ownerWebsiteImpressumUrl
                  ? a.isValidUrl(
                      e.cookieConsent.ownerWebsitePrivacyPolicyUrl
                    ) &&
                    a.isValidUrl(e.cookieConsent.ownerWebsiteImpressumUrl) &&
                    ((c.innerHTML = e.cookieConsent.i18n.$t(
                      "i18n",
                      "privacy_policy",
                      e.cookieConsent.ownerWebsitePrivacyPolicyUrl
                    )),
                    (l.innerHTML = e.cookieConsent.i18n.$t(
                      "i18n",
                      "impressum",
                      e.cookieConsent.ownerWebsiteImpressumUrl
                    )),
                    a.appendChild(s, c),
                    a.appendChild(c, p),
                    a.appendChild(s, l))
                  : e.cookieConsent.ownerWebsitePrivacyPolicyUrl &&
                    a.isValidUrl(e.cookieConsent.ownerWebsitePrivacyPolicyUrl)
                  ? ((c.innerHTML = e.cookieConsent.i18n.$t(
                      "i18n",
                      "privacy_policy",
                      e.cookieConsent.ownerWebsitePrivacyPolicyUrl
                    )),
                    a.appendChild(s, c))
                  : e.cookieConsent.ownerWebsiteImpressumUrl &&
                    a.isValidUrl(e.cookieConsent.ownerWebsiteImpressumUrl) &&
                    ((l.innerHTML = e.cookieConsent.i18n.$t(
                      "i18n",
                      "impressum",
                      e.cookieConsent.ownerWebsiteImpressumUrl
                    )),
                    a.appendChild(s, l)),
                a.appendChild(r, s)),
              a.appendChild(o, r);
            var d = document.createElement("div");
            d.classList.add("cc-nb-buttons-container");
            var u = document.createElement("button");
            u.classList.add("cc-nb-okagree"),
              u.setAttribute("role", "button"),
              "express" == e.cookieConsent.ownerConsentType
                ? (u.innerHTML = e.cookieConsent.i18n.$t("i18n", "nb_agree"))
                : (u.innerHTML = e.cookieConsent.i18n.$t("i18n", "nb_ok")),
              u.addEventListener("click", function () {
                document.dispatchEvent(
                  e.cookieConsent.events.cc_noticeBannerOkOrAgreePressed
                );
              }),
              a.appendChild(d, u);
            var m = document.createElement("button");
            m.classList.add("cc-nb-reject"),
              m.setAttribute("role", "button"),
              (m.innerHTML = e.cookieConsent.i18n.$t("i18n", "nb_reject")),
              m.addEventListener("click", function () {
                document.dispatchEvent(
                  e.cookieConsent.events.cc_noticeBannerRejectPressed
                );
              }),
              "express" == e.cookieConsent.ownerConsentType &&
                !1 === e.cookieConsent.ownerNoticeBannerRejectButtonHide &&
                a.appendChild(d, m);
            var _ = document.createElement("button");
            return (
              _.classList.add("cc-nb-changep"),
              _.setAttribute("role", "button"),
              (_.innerHTML = e.cookieConsent.i18n.$t("i18n", "nb_changep")),
              _.addEventListener("click", function () {
                document.dispatchEvent(
                  e.cookieConsent.events.cc_noticeBannerChangePreferencesPressed
                );
              }),
              a.appendChild(d, _),
              a.appendChild(t, i),
              a.appendChild(t, o),
              a.appendChild(t, d),
              t
            );
          }),
          e
        );
      })(),
      Q = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return i.noticeBannerExtraCss.push("termsfeed-com---nb-simple"), i;
        }
        return J(t, e), t;
      })(Y),
      X = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return i.noticeBannerExtraCss.push("termsfeed-com---nb-headline"), i;
        }
        return J(t, e), t;
      })(Y),
      ee = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (
            i.noticeBannerExtraCss.push("termsfeed-com---nb-interstitial"), i
          );
        }
        return J(t, e), t;
      })(Y),
      te = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (
            i.noticeBannerExtraCss.push("termsfeed-com---nb-standalone"), i
          );
        }
        return J(t, e), t;
      })(Y),
      ie = (function () {
        function e(e) {
          e.log("ConsentType main class initialized", "info");
        }
        return (e.prototype.loadInitialCookiesForNewUser = function () {}), e;
      })(),
      ne = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (i.cookieConsent = t), i;
        }
        return (
          J(t, e),
          (t.prototype.loadInitialCookiesForNewUser = function () {
            this.cookieConsent.log(
              "consentImplied loadInitialCookiesForNewUser triggered",
              "info"
            );
            var e = !1,
              t = !1,
              i = !1;
            if (null !== this.cookieConsent.ownerPageLoadConsentLevels)
              for (var n in this.cookieConsent.ownerPageLoadConsentLevels) {
                var o = this.cookieConsent.ownerPageLoadConsentLevels[n];
                "functionality" == o && (e = !0),
                  "tracking" == o && (t = !0),
                  "targeting" == o && (i = !0);
              }
            else (e = !0), (t = !0), (i = !0);
            this.cookieConsent.javascriptItems.enableScriptsByLevel(
              "strictly-necessary"
            ),
              e
                ? (this.cookieConsent.userConsent.acceptLevel("functionality"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "functionality"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("functionality"),
              t
                ? (this.cookieConsent.userConsent.acceptLevel("tracking"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "tracking"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("tracking"),
              i
                ? (this.cookieConsent.userConsent.acceptLevel("targeting"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "targeting"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("targeting"),
              this.cookieConsent.log(
                "consentImplied loadInitialCookiesForNewUser: strictly-necessary (true), functionality (" +
                  e +
                  "), tracking (" +
                  t +
                  "), targeting (" +
                  i +
                  ")",
                "info"
              );
          }),
          t
        );
      })(ie),
      oe = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (i.cookieConsent = t), i;
        }
        return (
          J(t, e),
          (t.prototype.loadInitialCookiesForNewUser = function () {
            this.cookieConsent.log(
              "consentExpress loadInitialCookiesForNewUser triggered",
              "info"
            );
            var e = !1,
              t = !1,
              i = !1;
            if (null !== this.cookieConsent.ownerPageLoadConsentLevels)
              for (var n in this.cookieConsent.ownerPageLoadConsentLevels) {
                var o = this.cookieConsent.ownerPageLoadConsentLevels[n];
                "functionality" == o && (e = !0),
                  "tracking" == o && (t = !0),
                  "targeting" == o && (i = !0);
              }
            else (e = !1), (t = !1), (i = !1);
            this.cookieConsent.javascriptItems.enableScriptsByLevel(
              "strictly-necessary"
            ),
              e
                ? (this.cookieConsent.userConsent.acceptLevel("functionality"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "functionality"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("functionality"),
              t
                ? (this.cookieConsent.userConsent.acceptLevel("tracking"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "tracking"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("tracking"),
              i
                ? (this.cookieConsent.userConsent.acceptLevel("targeting"),
                  this.cookieConsent.javascriptItems.enableScriptsByLevel(
                    "targeting"
                  ))
                : this.cookieConsent.userConsent.rejectLevel("targeting"),
              this.cookieConsent.log(
                "consentExpress loadInitialCookiesForNewUser: strictly-necessary (true), functionality (" +
                  e +
                  "), tracking (" +
                  t +
                  "), targeting (" +
                  i +
                  ")",
                "info"
              );
          }),
          t
        );
      })(ie),
      ae = (function () {
        function e(e) {
          this.cookieConsent = e;
        }
        return (
          (e.prototype.getClass = function () {
            return "termsfeed-com---palette-light";
          }),
          e
        );
      })(),
      re = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (i.cookieConsent = t), i;
        }
        return (
          J(t, e),
          (t.prototype.getClass = function () {
            return "termsfeed-com---palette-dark";
          }),
          t
        );
      })(ae),
      se = (function (e) {
        function t(t) {
          var i = e.call(this, t) || this;
          return (i.cookieConsent = t), i;
        }
        return (
          J(t, e),
          (t.prototype.getClass = function () {
            return "termsfeed-com---palette-light";
          }),
          t
        );
      })(ae),
      ce = (function () {
        function e(e) {
          (this.USER_TOKEN_COOKIE_NAME = "cookie_consent_user_consent_token"),
            (this.cookieConsent = e),
            this.initUserConsentToken();
        }
        return (
          (e.prototype.initUserConsentToken = function () {
            var e = F("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
              t = F("abcdefghijklmnopqrstuvwxyz"),
              i = F("0123456789"),
              n = F(e, i, t);
            (this.cookieConsent.userConsentToken =
              a.getCookie(this.USER_TOKEN_COOKIE_NAME) ||
              this.cookieConsent.configUserConsentToken ||
              (function (e, t) {
                return F(Array(t))
                  .map(function (t) {
                    return e[(Math.random() * e.length) | 0];
                  })
                  .join("");
              })(n, 12)),
              a.setCookie(
                this.USER_TOKEN_COOKIE_NAME,
                this.cookieConsent.userConsentToken,
                this.cookieConsent.ownerDomain,
                this.cookieConsent.cookieSecure,
                3650
              );
          }),
          e
        );
      })(),
      le = (function () {
        function e(e) {
          switch (
            ((this.configUserConsentToken = void 0),
            (this.userConsentToken = void 0),
            (this.debug = !1),
            (this.ownerConsentType = e.consent_type || "express"),
            (this.ownerWebsiteName = e.website_name || ""),
            (this.ownerWebsitePrivacyPolicyUrl =
              e.website_privacy_policy_url || null),
            (this.ownerColorPalette = e.palette || "light"),
            (this.ownerSiteLanguage = e.language || "en"),
            (this.ownerDomain = e.cookie_domain || ""),
            (this.ownerWebsiteImpressumUrl = e.website_impressum_url || null),
            (this.noticeBannerInsertLegalUrls =
              e.notice_banner_insert_legal_urls || !1),
            (this.cookieSecure = e.cookie_secure || !1),
            (this.ownerPageLoadConsentLevels =
              e.page_load_consent_levels || null),
            (this.ownerNoticeBannerType = e.notice_banner_type || "headline"),
            (this.ownerNoticeBannerRejectButtonHide =
              e.notice_banner_reject_button_hide || !1),
            (this.ownerNoticeBannerAppendContentPosition =
              e.notice_banner_append || "afterbegin"),
            (this.ownerOpenPreferencesCenterSelector =
              e.open_preferences_center_selector || "#open_preferences_center"),
            (this.ownerPreferencesCenterCloseButtonHide =
              e.preferences_center_close_button_hide || !1),
            (this.pageRefreshConfirmationButtons =
              e.page_refresh_confirmation_buttons || !1),
            (this.configUserConsentToken = e.user_consent_token || null),
            (this.isDemo = "true" == e.demo),
            (this.debug = "true" == e.debug),
            this.ownerConsentType)
          ) {
            default:
            case "express":
              this.consentType = new oe(this);
              break;
            case "implied":
              (this.consentType = new ne(this)),
                (this.userConsentTokenClass = new ce(this));
          }
          switch (this.ownerColorPalette) {
            default:
            case "dark":
              this.colorPalette = new re(this);
              break;
            case "light":
              this.colorPalette = new se(this);
          }
          switch (this.ownerNoticeBannerType) {
            default:
            case "simple":
              this.noticeBannerContainer = new Q(this);
              break;
            case "headline":
              this.noticeBannerContainer = new X(this);
              break;
            case "interstitial":
              this.noticeBannerContainer = new ee(this);
              break;
            case "standalone":
              this.noticeBannerContainer = new te(this);
          }
          (this.events = new K()),
            (this.eventsListeners = new H(this)),
            (this.i18n = new D(this)),
            (this.cookieLevels = new G(this)),
            (this.userConsent = new V(this)),
            (this.javascriptItems = new $(this)),
            (this.preferencesCenterContainer = new Z(this)),
            null !== this.ownerOpenPreferencesCenterSelector &&
              this.preferencesCenterContainer.listenToUserButtonToOpenPreferences(
                this.ownerOpenPreferencesCenterSelector
              ),
            !0 === this.userConsent.userAccepted
              ? (this.userConsent.loadAcceptedCookies(),
                !0 === this.isDemo &&
                  this.noticeBannerContainer.initNoticeBanner())
              : (this.noticeBannerContainer.initNoticeBanner(),
                this.consentType.loadInitialCookiesForNewUser());
        }
        return (
          (e.prototype.log = function (e, t, i) {
            void 0 === i && (i = "log"),
              !0 === this.debug &&
                ("log" === i || "table" === i) &&
                console.log("[" + t + "]", e);
          }),
          (e.prototype.openPreferencesCenter = function () {
            this.preferencesCenterContainer.showPreferencesCenter();
          }),
          e
        );
      })(),
      pe = function (e) {
        return (
          (o = new le(e)),
          (window.cookieconsent.openPreferencesCenter = function () {
            o.openPreferencesCenter();
          }),
          o
        );
      };
  },
]);
