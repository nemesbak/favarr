#!/usr/bin/env python3
"""Favarr ❤️ — pide películas y series desde Jellyfin o Emby dándole a «favorito».
           Request movies and shows from Jellyfin or Emby by tapping "favourite".

Crea una biblioteca «escaparate» con lo que está de moda y NO tienes. Cuando alguien marca algo como
favorito, Favarr lo pide a Seerr (Jellyseerr / Overseerr) en su nombre, le quita el ❤️ y, si quieres,
le avisa por Telegram. Cuando ya está descargado, le avisa otra vez y lo quita del escaparate.

Uso / usage:
  python favarr.py            → se queda funcionando / keeps running
  python favarr.py renovar    → renueva el escaparate una vez / refresh the showcase once
  python favarr.py vigilar    → mira los ❤️ una vez / check favourites once
  python favarr.py prueba     → todo lo anterior SIN cambiar nada / dry run, changes nothing

Configuración por variables de entorno (README.md). Solo biblioteca estándar de Python.
"""
import base64
import datetime
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.3.0"

try:   # que los emojis no rompan en consolas raras (Windows, NAS antiguos)
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


# ───────────────────────────── configuración ─────────────────────────────
def env(nombre, defecto=""):
    return os.environ.get(nombre, defecto).strip()


def env_int(nombre, defecto):
    try:
        return int(env(nombre, str(defecto)))
    except ValueError:
        return defecto


def env_si(nombre, defecto):
    return env(nombre, defecto).lower() in ("si", "sí", "yes", "true", "1", "on")


SEERR_URL = env("SEERR_URL").rstrip("/")
SEERR_KEY = env("SEERR_API_KEY")
SERVIDORES = {n: (env(f"{n.upper()}_URL").rstrip("/"), env(f"{n.upper()}_API_KEY"), env(f"{n.upper()}_CARPETA"))
              for n in ("jellyfin", "emby") if env(f"{n.upper()}_URL") and env(f"{n.upper()}_API_KEY")}
CATALOGO = env("CATALOGO", "/catalogo")
DATOS = env("DATOS", "/datos")
IDIOMA = env("IDIOMA", "es").lower()[:2]
NOMBRE_BIBLIOTECA = env("NOMBRE_BIBLIOTECA", "✨ Descubre y pide" if IDIOMA == "es" else "✨ Discover & request")
PELICULAS = env_int("PELICULAS", 100)
SERIES = env_int("SERIES", 50)
LIMITE_DIA = env_int("LIMITE_DIA", 0)          # 0 = solo manda el cupo de Seerr
MAX_PENDIENTES = env_int("MAX_PENDIENTES", 0)  # 0 = solo manda el cupo de Seerr
SOLO_TEMPORADA_1 = env_si("SOLO_TEMPORADA_1", "si")
CADA_MINUTOS = max(1, env_int("CADA_MINUTOS", 2))
HORA_RENOVAR = env_int("HORA_RENOVAR", 4)
TG_TOKEN = env("TELEGRAM_TOKEN")
TG_ADMIN = env("TELEGRAM_ADMIN")
TG_USUARIOS = {k.strip().lower(): v.strip() for k, v in
               (p.split("=", 1) for p in env("TELEGRAM_USUARIOS").split(",") if "=" in p)}
# Idiomas con muchísimos títulos locales que casi nadie pide: solo entran si son muy populares
EXOTICOS = ("ja", "ko", "zh", "hi", "th", "ta", "te", "ml", "kn", "tl", "id")

PRUEBA = "prueba" in sys.argv[1:] or "test" in sys.argv[1:] or "dry-run" in sys.argv[1:]
AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(DATOS, "favarr.json")

TEXTOS = {
    "es": {
        "ya_pedido": "👍 {t} ya estaba pedido. Te aviso cuando esté.",
        "limite_dia": "⏳ Hoy ya has pedido {n}. Vuelve a darle ❤️ a {t} mañana.",
        "pendientes": "⏳ Tienes {n} peticiones esperando. Cuando llegue alguna, vuelve a darle ❤️ a {t}.",
        "pedido": "✅ Pedido: {t}{extra}. Te aviso en cuanto esté.",
        "temporada1": " (la primera temporada; si te gusta, pide el resto)",
        "sin_usuario": "⚠️ No he podido pedir {t}: tu usuario no está en Seerr. Avisa al administrador.",
        "cupo": "⏳ Has llegado a tu cupo en Seerr. Vuelve a darle ❤️ a {t} cuando se renueve.",
        "cupo_det": "⏳ Tu cupo es de {n} {que} cada {d} días y ya lo has usado. Vuelve a darle ❤️ a {t} cuando se renueve.",
        "peli": "película", "pelis": "películas", "temp": "temporada", "temps": "temporadas",
        "sin_permiso": "⚠️ Tu usuario no tiene permiso para pedir en Seerr. Avisa al administrador.",
        "error": "⚠️ No he podido pedir {t}. Ya lo sabe el administrador.",
        "luego": "⚠️ No he podido pedir {t} ahora mismo. Inténtalo más tarde.",
        "llego": "🎉 Ya está disponible: {t}. ¡A disfrutarlo!",
        "rechazado": "❌ Al final no se ha podido conseguir {t}.",
        "adm_rechazado": "🗑️ {t} (de {u}) ya no está pedido en Seerr: lo olvido.",
        "adm_pedido": "📥 {u} ha pedido {t} desde {s}.",
        "adm_sin_usuario": "⚠️ {u} ({s}) ha dado ❤️ a {t} pero no tiene usuario en Seerr.",
        "adm_error": "⚠️ Seerr ha dado error {c} al pedir {t} para {u}: {d}",
    },
    "en": {
        "ya_pedido": "👍 {t} was already requested. I'll let you know when it's ready.",
        "limite_dia": "⏳ You've already made {n} requests today. Tap ❤️ on {t} again tomorrow.",
        "pendientes": "⏳ You have {n} requests waiting. When one arrives, tap ❤️ on {t} again.",
        "pedido": "✅ Requested: {t}{extra}. I'll let you know as soon as it's ready.",
        "temporada1": " (first season; if you like it, request the rest)",
        "sin_usuario": "⚠️ I couldn't request {t}: your user isn't in Seerr. Please tell the admin.",
        "cupo": "⏳ You've reached your Seerr quota. Tap ❤️ on {t} again when it resets.",
        "cupo_det": "⏳ Your quota is {n} {que} every {d} days and you've used it. Tap ❤️ on {t} again when it resets.",
        "peli": "movie", "pelis": "movies", "temp": "season", "temps": "seasons",
        "sin_permiso": "⚠️ Your user isn't allowed to request in Seerr. Please tell the admin.",
        "error": "⚠️ I couldn't request {t}. The admin has been told.",
        "luego": "⚠️ I couldn't request {t} right now. Please try again later.",
        "llego": "🎉 Now available: {t}. Enjoy!",
        "rechazado": "❌ {t} couldn't be added in the end.",
        "adm_rechazado": "🗑️ {t} (from {u}) is no longer requested in Seerr: forgetting it.",
        "adm_pedido": "📥 {u} requested {t} from {s}.",
        "adm_sin_usuario": "⚠️ {u} ({s}) tapped ❤️ on {t} but has no Seerr user.",
        "adm_error": "⚠️ Seerr returned error {c} requesting {t} for {u}: {d}",
    },
}


def txt(clave, **kw):
    return TEXTOS.get(IDIOMA, TEXTOS["en"])[clave].format(**kw)


def log(*a):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


# ───────────────────────────── conexiones ─────────────────────────────
def http(metodo, url, cabeceras=None, datos=None, crudo=None, tipo="application/json"):
    cuerpo = crudo if crudo is not None else (json.dumps(datos).encode() if datos is not None else None)
    if cuerpo is None and metodo in ("POST", "DELETE"):
        cuerpo = b""
    req = urllib.request.Request(url, method=metodo, data=cuerpo,
                                 headers={"Content-Type": tipo, "Accept": "application/json", **(cabeceras or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = r.read()
        try:
            return json.loads(res) if res else {}
        except ValueError:
            return {}


def seerr(metodo, ruta, datos=None, usuario=None):
    cab = {"X-Api-Key": SEERR_KEY}
    if usuario:
        cab["X-API-User"] = str(usuario)   # la petición sale a nombre de esa persona (cuenta en sus cupos)
    return http(metodo, f"{SEERR_URL}/api/v1{ruta}", cab, datos)


def servidor(nombre, metodo, ruta, datos=None, **kw):
    url, clave, _ = SERVIDORES[nombre]
    return http(metodo, url + ruta, {"Authorization": f'MediaBrowser Token="{clave}"'}, datos, **kw)


def telegram(chat, texto):
    if not (TG_TOKEN and chat):
        return
    if PRUEBA:
        log("  [telegram]", chat, re.sub("<[^>]+>", "", texto))
        return
    try:
        http("POST", f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
             datos={"chat_id": chat, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": True})
    except Exception as e:
        log("Telegram:", e)


# ───────────────────────────── estado ─────────────────────────────
def leer_estado():
    try:
        with open(ESTADO, encoding="utf-8") as f:
            e = json.load(f)
    except (OSError, ValueError):
        e = {}
    for k in ("pedidos", "cuenta", "conseguible"):
        e.setdefault(k, {})
    return e


def guardar_estado(e):
    if PRUEBA:
        return
    os.makedirs(DATOS, exist_ok=True)
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ESTADO)


# ───────────────────────────── la biblioteca ─────────────────────────────
def bibliotecas(s):
    """Las bibliotecas de Favarr en ese servidor: por nombre o porque apuntan a su carpeta."""
    carpeta = SERVIDORES[s][2].rstrip("/")
    return [b for b in servidor(s, "GET", "/Library/VirtualFolders")
            if b.get("ItemId") and (b.get("Name") == NOMBRE_BIBLIOTECA
                                    or (carpeta and carpeta in [l.rstrip("/") for l in b.get("Locations", [])]))]


def crear_bibliotecas():
    """Si se ha dicho dónde ve cada servidor la carpeta, crea la biblioteca sola (una vez)."""
    for s, (_, _, carpeta) in SERVIDORES.items():
        if not carpeta:
            continue
        try:
            if bibliotecas(s):
                continue
            if PRUEBA:
                log(f"{s}: crearía la biblioteca «{NOMBRE_BIBLIOTECA}» en {carpeta}")
                continue
            q = urllib.parse.quote
            # Mezcla de películas y series. OJO: en Emby «mixto» es SIN tipo; con collectionType=mixed
            # Emby no reconoce nada (todo sale como carpetas).
            tipo = "&collectionType=mixed" if s == "jellyfin" else ""
            servidor(s, "POST", f"/Library/VirtualFolders?name={q(NOMBRE_BIBLIOTECA)}{tipo}"
                                f"&paths={q(carpeta)}&refreshLibrary=false")
            b = bibliotecas(s)[0]
            o = b.get("LibraryOptions") or {}
            o.update({"PreferredMetadataLanguage": IDIOMA, "EnableRealtimeMonitor": True,
                      "AutomaticallyAddToCollection": False, "ImportCollections": False,
                      "EnableChapterImageExtraction": False, "ExtractChapterImagesDuringLibraryScan": False,
                      "EnableTrickplayImageExtraction": False, "EnableEmbeddedTitles": False})
            # Las bibliotecas creadas por API salen sin proveedores de carátulas: se ponen todos, TheMovieDb
            # el primero (las carpetas llevan su id de TMDB).
            disp = servidor(s, "GET", "/Libraries/AvailableOptions?IsNewLibrary=true&LibraryContentType="
                                      + ("mixed" if s == "jellyfin" else ""))
            o["TypeOptions"] = []
            for t in disp.get("TypeOptions", []):
                if t["Type"] not in ("Movie", "Series", "Season", "Episode"):
                    continue
                orden = lambda lista: sorted((f["Name"] for f in lista), key=lambda n: n != "TheMovieDb")
                o["TypeOptions"].append({"Type": t["Type"], "MetadataFetchers": orden(t.get("MetadataFetchers", [])),
                                         "MetadataFetcherOrder": orden(t.get("MetadataFetchers", [])),
                                         "ImageFetchers": orden(t.get("ImageFetchers", [])),
                                         "ImageFetcherOrder": orden(t.get("ImageFetchers", []))})
            servidor(s, "POST", "/Library/VirtualFolders/LibraryOptions", {"Id": b["ItemId"], "LibraryOptions": o})
            with open(os.path.join(AQUI, "portada.jpg"), "rb") as f:
                servidor(s, "POST", f"/Items/{b['ItemId']}/Images/Primary",
                         crudo=base64.b64encode(f.read()), tipo="image/jpeg")
            log(f"{s}: biblioteca «{NOMBRE_BIBLIOTECA}» creada ✔")
        except Exception as e:
            log(f"{s}: no he podido crear la biblioteca ({e}). Créala a mano (README).")


def releer(s):
    for b in bibliotecas(s):
        servidor(s, "POST", f"/Items/{b['ItemId']}/Refresh?Recursive=true&MetadataRefreshMode=Default"
                            "&ImageRefreshMode=Default")


# ───────────────────────────── el escaparate ─────────────────────────────
def limpio(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", s or "").strip().rstrip(".")
    return re.sub(r"\s+", " ", s)


def ya_lo_tenemos(r):
    """Seerr: 1 desconocido · 2 pendiente · 3 descargando · 4 en parte · 5 disponible."""
    return (r.get("mediaInfo") or {}).get("status", 1) >= 2


def conseguible(est, tmdb):
    """Película con estreno digital o en disco ya ocurrido (lo que solo está en cines no se puede conseguir)."""
    k = str(tmdb)
    if est["conseguible"].get(k):
        return True
    hoy = datetime.date.today().isoformat()
    try:
        for pais in (seerr("GET", f"/movie/{tmdb}").get("releases") or {}).get("results", []):
            if any(rd.get("type") in (4, 5) and (rd.get("release_date") or "")[:10] <= hoy
                   for rd in pais.get("release_dates", [])):
                est["conseguible"][k] = True
                return True
    except Exception:
        pass
    return False


def candidatos(est, tipo, cuantos):
    rutas = ["/discover/trending", "/discover/movies" if tipo == "movie" else "/discover/tv"]
    hoy, vistos, salida = datetime.date.today().isoformat(), set(), []
    for ruta in rutas:
        for pagina in range(1, 11):
            if len(salida) >= cuantos:
                return salida
            try:
                res = seerr("GET", f"{ruta}?page={pagina}&language={IDIOMA}").get("results", [])
            except Exception as e:
                log("Seerr:", ruta, e)
                break
            for r in res:
                if r.get("mediaType") != tipo or r["id"] in vistos or r.get("adult") or not r.get("posterPath"):
                    continue
                vistos.add(r["id"])
                fecha = r.get("releaseDate") or r.get("firstAirDate") or ""
                if not fecha or fecha > hoy or ya_lo_tenemos(r):
                    continue
                if r.get("originalLanguage") in EXOTICOS and r.get("voteCount", 0) < 500:
                    continue
                if tipo == "movie" and not conseguible(est, r["id"]):
                    continue
                salida.append(r)
                if len(salida) >= cuantos:
                    return salida
    return salida


def carpeta_de(r):
    titulo = limpio(r.get("title") or r.get("name"))
    año = (r.get("releaseDate") or r.get("firstAirDate") or "")[:4]
    return f"{titulo} ({año}) [tmdbid-{r['id']}]", titulo


def preparar_catalogo():
    oculta = os.path.join(CATALOGO, ".favarr")
    os.makedirs(oculta, exist_ok=True)
    open(os.path.join(oculta, ".ignore"), "a").close()     # Jellyfin y Emby no escanean esta carpeta
    destino = os.path.join(oculta, "aviso.mkv")
    if not os.path.exists(destino) or os.path.getsize(destino) != os.path.getsize(os.path.join(AQUI, "aviso.mkv")):
        shutil.copyfile(os.path.join(AQUI, "aviso.mkv"), destino)


def poner_aviso(destino):
    """Enlace duro del vídeo de aviso: 150 títulos ocupan lo que uno. Si no se puede, copia (≈32 KB)."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base = os.path.join(CATALOGO, ".favarr", "aviso.mkv")
    try:
        os.link(base, destino)
    except OSError:
        shutil.copyfile(base, destino)


def renovar():
    est = leer_estado()
    pelis = candidatos(est, "movie", PELICULAS)
    series = candidatos(est, "tv", SERIES)
    if not pelis and not series:
        log("Seerr no ha devuelto nada: no toco el escaparate.")
        return
    if not PRUEBA:
        preparar_catalogo()
    deseadas = {}
    for tipo, lista in (("movie", pelis), ("tv", series)):
        for r in lista:
            carpeta, titulo = carpeta_de(r)
            deseadas[carpeta] = (tipo, titulo)
    nuevas = quitadas = 0
    for carpeta, (tipo, titulo) in deseadas.items():
        d = os.path.join(CATALOGO, carpeta)
        f = os.path.join(d, f"{carpeta}.mkv") if tipo == "movie" else os.path.join(d, "Season 01", f"{titulo} S01E01.mkv")
        if not os.path.exists(f):
            nuevas += 1
            if not PRUEBA:
                poner_aviso(f)
    pedidos = {k.split(":")[1] for k in est["pedidos"]}
    if os.path.isdir(CATALOGO):
        for c in os.listdir(CATALOGO):
            m = re.search(r"\[tmdbid-(\d+)\]", c)
            if c.startswith(".") or c in deseadas or not m or m.group(1) in pedidos:
                continue                       # lo pedido se queda hasta que llegue; lo ajeno no se toca
            quitadas += 1
            if not PRUEBA:
                shutil.rmtree(os.path.join(CATALOGO, c), ignore_errors=True)
    est["renovado"] = datetime.date.today().isoformat()
    guardar_estado(est)
    log(f"Escaparate: {len(pelis)} películas y {len(series)} series ({nuevas} nuevas, {quitadas} quitadas)"
        + (" — PRUEBA, no se ha cambiado nada" if PRUEBA else ""))
    if not PRUEBA:
        for s in SERVIDORES:
            try:
                releer(s)
            except Exception as e:
                log(f"{s}: no he podido releer la biblioteca:", e)


# ───────────────────────────── los ❤️ ─────────────────────────────
class CupoAgotado(Exception):
    def __init__(self, q):
        super().__init__("cupo")
        self.q = q


def usuario_seerr(usuarios, srv, uid, nombre):
    if srv == "jellyfin":
        for u in usuarios:
            if u.get("jellyfinUserId") == uid:
                return u["id"]
    n = nombre.lower()
    for u in usuarios:
        nombres = {(u.get(k) or "").lower() for k in ("jellyfinUsername", "username", "plexUsername", "displayName")}
        if n in nombres or (u.get("email") or "").lower().split("@")[0] == n:
            return u["id"]
    return None


def vigilar():
    est = leer_estado()
    hoy = datetime.date.today().isoformat()
    try:
        usuarios_seerr = seerr("GET", "/user?take=5000")["results"]
    except Exception as e:
        log("Seerr no responde:", e)
        return
    for s in SERVIDORES:
        try:
            libs = [b["ItemId"] for b in bibliotecas(s)]
            usuarios = servidor(s, "GET", "/Users")
        except Exception as e:
            log(f"{s} no responde:", e)
            continue
        if not libs:
            log(f"{s}: no encuentro la biblioteca «{NOMBRE_BIBLIOTECA}».")
            continue
        for u in usuarios:
            if (u.get("Policy") or {}).get("IsDisabled"):
                continue
            for lib in libs:
                try:
                    favs = servidor(s, "GET", f"/Users/{u['Id']}/Items?ParentId={lib}&Recursive=true"
                                              "&Filters=IsFavorite&IncludeItemTypes=Movie,Series"
                                              "&CollapseBoxSetItems=false&Fields=Path")["Items"]
                except Exception:
                    continue                    # esa persona no tiene acceso a la biblioteca
                for it in favs:
                    atender(est, s, u, it, usuarios_seerr, hoy)
    avisar_llegadas(est)
    limite = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    est["cuenta"] = {d: c for d, c in est["cuenta"].items() if d >= limite}
    guardar_estado(est)


def atender(est, s, u, it, usuarios_seerr, hoy):
    m = re.search(r"\[tmdbid-(\d+)\]", it.get("Path") or "")
    if not m:
        return
    tipo = "movie" if it.get("Type") == "Movie" else "tv"
    tmdb = int(m.group(1))
    clave = f"{tipo}:{tmdb}"
    nombre, quien = it["Name"], u["Name"]
    admin = (u.get("Policy") or {}).get("IsAdministrator", False)
    chat = TG_USUARIOS.get(quien.lower())
    hechas = est["cuenta"].setdefault(hoy, {}).get(quien, 0)
    pendientes = sum(1 for p in est["pedidos"].values() if p.get("usuario") == quien)
    t = f"<b>{nombre}</b>"

    if clave in est["pedidos"]:
        texto = txt("ya_pedido", t=t)
    elif not admin and LIMITE_DIA and hechas >= LIMITE_DIA:
        texto = txt("limite_dia", n=LIMITE_DIA, t=t)
    elif not admin and MAX_PENDIENTES and pendientes >= MAX_PENDIENTES:
        texto = txt("pendientes", n=pendientes, t=t)
    else:
        sid = usuario_seerr(usuarios_seerr, s, u["Id"], quien)
        cuerpo = {"mediaType": tipo, "mediaId": tmdb}
        solo_t1 = tipo == "tv" and SOLO_TEMPORADA_1 and not admin
        if tipo == "tv":
            cuerpo["seasons"] = [1] if solo_t1 else "all"
        try:
            if sid is None:
                raise LookupError
            # Los límites mandan desde Seerr (cupo de cada usuario): se mira ANTES de pedir para no
            # gastar nada y avisar con claridad. limit 0 = sin límite.
            q = (seerr("GET", f"/user/{sid}/quota") or {}).get(tipo) or {}
            if q.get("limit") and q.get("remaining", 0) < 1:
                raise CupoAgotado(q)
            if not PRUEBA:
                seerr("POST", "/request", cuerpo, usuario=sid)
            est["pedidos"][clave] = {"nombre": nombre, "usuario": quien, "chat": chat, "fecha": hoy, "hora": time.time()}
            est["cuenta"][hoy][quien] = hechas + 1
            texto = txt("pedido", t=t, extra=txt("temporada1") if solo_t1 else "")
            telegram(TG_ADMIN, txt("adm_pedido", u=quien, t=t, s=s.capitalize()))
        except CupoAgotado as c:
            n = c.q.get("limit", 0)
            que = txt("peli" if tipo == "movie" else "temp") if n == 1 else txt("pelis" if tipo == "movie" else "temps")
            texto = txt("cupo_det", n=n, que=que, d=c.q.get("days", 0), t=t)
        except LookupError:
            texto = txt("sin_usuario", t=t)
            telegram(TG_ADMIN, txt("adm_sin_usuario", u=quien, s=s, t=t))
        except urllib.error.HTTPError as e:
            detalle = e.read().decode(errors="replace")[:300]
            if e.code == 403 and "uota" in detalle:
                texto = txt("cupo", t=t)
            elif e.code == 403:
                texto = txt("sin_permiso", t=t)
                telegram(TG_ADMIN, txt("adm_error", c=e.code, t=t, u=quien, d=detalle[:150]))
            elif e.code == 409:
                est["pedidos"][clave] = {"nombre": nombre, "usuario": quien, "chat": chat, "fecha": hoy}
                texto = txt("ya_pedido", t=t)
            else:
                texto = txt("error", t=t)
                telegram(TG_ADMIN, txt("adm_error", c=e.code, t=t, u=quien, d=detalle[:150]))
        except Exception as e:
            texto = txt("luego", t=t)
            log("Error:", e)
    log(f"{s} · {quien} · {nombre} → {re.sub('<[^>]+>', '', texto)}")
    if not PRUEBA:
        try:
            servidor(s, "DELETE", f"/Users/{u['Id']}/FavoriteItems/{it['Id']}")   # el ❤️ ya ha hecho su trabajo
        except Exception as e:
            log("No he podido quitar el favorito:", e)
    telegram(chat, texto)


def avisar_llegadas(est):
    for clave, p in list(est["pedidos"].items()):
        tipo, tmdb = clave.split(":")
        try:
            estado = (seerr("GET", f"/{tipo}/{tmdb}").get("mediaInfo") or {}).get("status", 1)
        except Exception:
            continue
        if estado <= 1 and time.time() - p.get("hora", 0) > 600:
            # Seerr vuelve a «desconocido» si la petición se rechaza o se borra: se olvida, sale del
            # escaparate el aviso de «ya pedido» y la persona puede pedir otra cosa.
            log(f"Ya no está pedido en Seerr: {p['nombre']} ({p['usuario']})")
            telegram(p.get("chat"), txt("rechazado", t=f"<b>{p['nombre']}</b>"))
            telegram(TG_ADMIN, txt("adm_rechazado", t=f"<b>{p['nombre']}</b>", u=p["usuario"]))
            if not PRUEBA:
                del est["pedidos"][clave]
            continue
        if estado >= (4 if tipo == "tv" else 5):
            log(f"Ya está: {p['nombre']} ({p['usuario']})")
            telegram(p.get("chat"), txt("llego", t=f"<b>{p['nombre']}</b>"))
            if not PRUEBA:
                del est["pedidos"][clave]
                if os.path.isdir(CATALOGO):     # ya está en la biblioteca de verdad: fuera del escaparate
                    for c in os.listdir(CATALOGO):
                        if f"[tmdbid-{tmdb}]" in c:
                            shutil.rmtree(os.path.join(CATALOGO, c), ignore_errors=True)


# ───────────────────────────── arranque ─────────────────────────────
def explicar(e):
    """Error de conexión en palabras normales."""
    if isinstance(e, urllib.error.HTTPError) and e.code in (401, 403):
        return "la clave API no es correcta / wrong API key"
    if isinstance(e, urllib.error.HTTPError):
        return f"responde con error {e.code} / answers with error {e.code}"
    return "no contesta: revisa la dirección y el puerto / no answer: check address and port"


def comprobar():
    """Comprueba la configuración y explica qué falla. Un servidor mal puesto no para a los demás."""
    for s in list(SERVIDORES):
        if "pega-aqui" in SERVIDORES[s][1]:
            log(f"⚠️  {s}: falta la clave API (pone «pega-aqui…») / API key missing → lo ignoro / skipped")
            del SERVIDORES[s]
    if not SEERR_URL or not SEERR_KEY or "pega-aqui" in SEERR_KEY:
        sys.exit("❌ Falta SEERR_URL o SEERR_API_KEY / missing SEERR_URL or SEERR_API_KEY")
    if not SERVIDORES:
        sys.exit("❌ Falta Jellyfin o Emby (dirección + clave) / Jellyfin or Emby missing (URL + key)")
    try:
        seerr("GET", "/settings/main")
    except Exception as e:
        sys.exit(f"❌ Seerr ({SEERR_URL}): {explicar(e)}")
    for s in list(SERVIDORES):
        try:
            servidor(s, "GET", "/System/Info")
        except Exception as e:
            log(f"⚠️  {s.capitalize()} ({SERVIDORES[s][0]}): {explicar(e)} → lo ignoro / skipped")
            del SERVIDORES[s]
        else:
            if not SERVIDORES[s][2]:
                log(f"ℹ️  {s.capitalize()}: sin {s.upper()}_CARPETA no creo la biblioteca; créala tú (README)")
    if not SERVIDORES:
        sys.exit("❌ Ni Jellyfin ni Emby responden / neither Jellyfin nor Emby answers")
    log(f"Favarr {VERSION} · Seerr ✔ · " + " · ".join(f"{s.capitalize()} ✔" for s in SERVIDORES)
        + (" · Telegram ✔" if TG_TOKEN else ""))


def main():
    orden = (sys.argv[1:] or ["servicio"])[0]
    orden = {"test": "prueba", "dry-run": "prueba", "refresh": "renovar", "watch": "vigilar"}.get(orden, orden)
    comprobar()
    if not PRUEBA:
        preparar_catalogo()     # la carpeta tiene que existir antes de crear la biblioteca
    crear_bibliotecas()
    if orden in ("renovar", "prueba"):
        renovar()
    if orden in ("vigilar", "prueba"):
        vigilar()
    if orden != "servicio":
        return
    if leer_estado().get("renovado") != datetime.date.today().isoformat() or not os.path.isdir(CATALOGO) \
            or len(os.listdir(CATALOGO)) <= 1:
        renovar()
    while True:
        try:
            ahora = datetime.datetime.now()
            if ahora.hour >= HORA_RENOVAR and leer_estado().get("renovado") != ahora.date().isoformat():
                renovar()
            vigilar()
        except Exception as e:
            log("Error (sigo funcionando):", e)
        time.sleep(CADA_MINUTOS * 60)


if __name__ == "__main__":
    main()
