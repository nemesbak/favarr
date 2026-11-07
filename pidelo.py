#!/usr/bin/env python3
"""Pídelo ❤️ — pide películas y series desde Jellyfin o Emby con un simple «favorito».

Crea una biblioteca «escaparate» con lo que está de moda y NO tienes. Cuando alguien marca algo como
favorito, Pídelo lo pide a Seerr (Jellyseerr / Overseerr) en su nombre, le quita el ❤️ y, si quieres,
le avisa por Telegram. Cuando ya está descargado, le avisa otra vez.

Uso:
  python pidelo.py            → se queda funcionando (renueva el escaparate y vigila los ❤️)
  python pidelo.py renovar    → renueva el escaparate una vez
  python pidelo.py vigilar    → mira los ❤️ una vez
  python pidelo.py prueba     → lo mismo que todo lo anterior, pero sin cambiar NADA (solo cuenta lo que haría)

Toda la configuración va en variables de entorno (ver README.md). Solo usa la biblioteca estándar de Python.
"""
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

VERSION = "1.0.0"


# ───────────────────────────── configuración ─────────────────────────────
def env(nombre, defecto=""):
    return os.environ.get(nombre, defecto).strip()


def env_int(nombre, defecto):
    try:
        return int(env(nombre, str(defecto)))
    except ValueError:
        return defecto


SEERR_URL = env("SEERR_URL").rstrip("/")
SEERR_KEY = env("SEERR_API_KEY")
SERVIDORES = {n: (env(f"{n.upper()}_URL").rstrip("/"), env(f"{n.upper()}_API_KEY"))
              for n in ("jellyfin", "emby") if env(f"{n.upper()}_URL") and env(f"{n.upper()}_API_KEY")}
CATALOGO = env("CATALOGO", "/catalogo")
DATOS = env("DATOS", "/datos")
NOMBRE_BIBLIOTECA = env("NOMBRE_BIBLIOTECA", "Descubre")
IDIOMA = env("IDIOMA", "es")
PELICULAS = env_int("PELICULAS", 100)
SERIES = env_int("SERIES", 50)
LIMITE_DIA = env_int("LIMITE_DIA", 3)
MAX_PENDIENTES = env_int("MAX_PENDIENTES", 5)
SOLO_TEMPORADA_1 = env("SOLO_TEMPORADA_1", "si").lower() in ("si", "sí", "yes", "true", "1")
CADA_MINUTOS = max(1, env_int("CADA_MINUTOS", 2))
HORA_RENOVAR = env_int("HORA_RENOVAR", 4)
TG_TOKEN = env("TELEGRAM_TOKEN")
TG_ADMIN = env("TELEGRAM_ADMIN")
TG_USUARIOS = {k.strip().lower(): v.strip() for k, v in
               (p.split("=", 1) for p in env("TELEGRAM_USUARIOS").split(",") if "=" in p)}

PRUEBA = "prueba" in sys.argv[1:]
AVISO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aviso.mkv")
ESTADO = os.path.join(DATOS, "pidelo.json")


def log(*a):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


# ───────────────────────────── conexiones ─────────────────────────────
def http(metodo, url, cabeceras=None, datos=None):
    req = urllib.request.Request(url, method=metodo,
                                 headers={"Content-Type": "application/json", "Accept": "application/json",
                                          **(cabeceras or {})},
                                 data=json.dumps(datos).encode() if datos is not None else None)
    with urllib.request.urlopen(req, timeout=60) as r:
        cuerpo = r.read()
        return json.loads(cuerpo) if cuerpo else {}


def seerr(metodo, ruta, datos=None, usuario=None):
    cab = {"X-Api-Key": SEERR_KEY}
    if usuario:
        cab["X-API-User"] = str(usuario)   # la petición sale a nombre de esa persona (cuenta en sus cupos)
    return http(metodo, f"{SEERR_URL}/api/v1{ruta}", cab, datos)


def servidor(nombre, metodo, ruta, datos=None):
    url, clave = SERVIDORES[nombre]
    return http(metodo, url + ruta, {"Authorization": f'MediaBrowser Token="{clave}"'}, datos)


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
        log("Telegram no ha podido enviar el mensaje:", e)


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


# ───────────────────────────── el escaparate ─────────────────────────────
def limpio(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", s or "").strip().rstrip(".")
    return re.sub(r"\s+", " ", s)


def ya_lo_tenemos(r):
    """1 = desconocido; 2 pendiente, 3 descargando, 4 en parte, 5 disponible → ya está o ya viene."""
    return (r.get("mediaInfo") or {}).get("status", 1) >= 2


def conseguible(est, tmdb):
    """Película con estreno digital o en disco ya ocurrido: se puede conseguir (lo de cines aún no)."""
    k = str(tmdb)
    if k in est["conseguible"]:
        return est["conseguible"][k]
    hoy, ok = datetime.date.today().isoformat(), False
    try:
        for pais in (seerr("GET", f"/movie/{tmdb}").get("releases") or {}).get("results", []):
            if any(rd.get("type") in (4, 5) and (rd.get("release_date") or "")[:10] <= hoy
                   for rd in pais.get("release_dates", [])):
                ok = True
                break
    except Exception:
        return False
    if ok:   # lo «sí» no cambia; lo «no» se vuelve a mirar otro día
        est["conseguible"][k] = True
    return ok


def candidatos(est, tipo, cuantos):
    rutas = (["/discover/trending", "/discover/movies"] if tipo == "movie"
             else ["/discover/trending", "/discover/tv"])
    hoy, vistos, salida = datetime.date.today().isoformat(), set(), []
    for ruta in rutas:
        for pagina in range(1, 11):
            if len(salida) >= cuantos:
                return salida
            try:
                res = seerr("GET", f"{ruta}?page={pagina}&language={IDIOMA}").get("results", [])
            except Exception as e:
                log("Seerr no responde a", ruta, e)
                break
            for r in res:
                if r.get("mediaType") != tipo or r["id"] in vistos or r.get("adult") or not r.get("posterPath"):
                    continue
                vistos.add(r["id"])
                fecha = r.get("releaseDate") or r.get("firstAirDate") or ""
                if not fecha or fecha > hoy or ya_lo_tenemos(r):
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


def poner_aviso(destino):
    """Enlace duro del vídeo de aviso: 150 títulos ocupan lo mismo que uno. Si no se puede, copia (≈26 KB)."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base = os.path.join(CATALOGO, ".pidelo", "aviso.mkv")
    try:
        os.link(base, destino)
    except OSError:
        shutil.copyfile(base, destino)


def preparar_catalogo():
    oculta = os.path.join(CATALOGO, ".pidelo")
    os.makedirs(oculta, exist_ok=True)
    open(os.path.join(oculta, ".ignore"), "a").close()     # Jellyfin y Emby no escanean esta carpeta
    destino = os.path.join(oculta, "aviso.mkv")
    if not os.path.exists(destino):
        shutil.copyfile(AVISO, destino)


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
            if c.startswith(".") or c in deseadas:
                continue
            m = re.search(r"\[tmdbid-(\d+)\]", c)
            if not m:
                continue                       # no es nuestra: no se toca
            if m.group(1) in pedidos:
                continue                       # alguien lo pidió: se queda hasta que llegue
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
                for b in servidor(s, "GET", "/Library/VirtualFolders"):
                    if NOMBRE_BIBLIOTECA.lower() in b.get("Name", "").lower() and b.get("ItemId"):
                        servidor(s, "POST", f"/Items/{b['ItemId']}/Refresh?Recursive=true&MetadataRefreshMode=Default")
            except Exception as e:
                log(f"No he podido pedir a {s} que relea la biblioteca:", e)


# ───────────────────────────── los ❤️ ─────────────────────────────
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
    if not SERVIDORES:
        log("Falta configurar Jellyfin o Emby.")
        return
    est = leer_estado()
    hoy = datetime.date.today().isoformat()
    try:
        usuarios_seerr = seerr("GET", "/user?take=5000")["results"]
    except Exception as e:
        log("Seerr no responde:", e)
        return
    for s in SERVIDORES:
        try:
            libs = [b["ItemId"] for b in servidor(s, "GET", "/Library/VirtualFolders")
                    if NOMBRE_BIBLIOTECA.lower() in b.get("Name", "").lower() and b.get("ItemId")]
            usuarios = servidor(s, "GET", "/Users")
        except Exception as e:
            log(f"{s} no responde:", e)
            continue
        if not libs:
            log(f"{s}: no encuentro ninguna biblioteca con «{NOMBRE_BIBLIOTECA}» en el nombre.")
            continue
        for u in usuarios:
            for lib in libs:
                try:
                    favs = servidor(s, "GET", f"/Users/{u['Id']}/Items?ParentId={lib}&Recursive=true"
                                              f"&Filters=IsFavorite&IncludeItemTypes=Movie,Series&Fields=Path")["Items"]
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
    titulo = f"<b>{nombre}</b>"

    if clave in est["pedidos"]:
        texto = f"👍 {titulo} ya estaba pedido. Te aviso cuando esté."
    elif not admin and LIMITE_DIA and hechas >= LIMITE_DIA:
        texto = f"⏳ Hoy ya has pedido {LIMITE_DIA}. Vuelve a darle ❤️ a {titulo} mañana."
    elif not admin and MAX_PENDIENTES and pendientes >= MAX_PENDIENTES:
        texto = f"⏳ Tienes {pendientes} peticiones esperando. Cuando llegue alguna, vuelve a darle ❤️ a {titulo}."
    else:
        sid = usuario_seerr(usuarios_seerr, s, u["Id"], quien)
        cuerpo = {"mediaType": tipo, "mediaId": tmdb}
        if tipo == "tv":
            cuerpo["seasons"] = [1] if (SOLO_TEMPORADA_1 and not admin) else "all"
        try:
            if sid is None:
                raise LookupError("sin usuario en Seerr")
            if not PRUEBA:
                seerr("POST", "/request", cuerpo, usuario=sid)
            est["pedidos"][clave] = {"nombre": nombre, "usuario": quien, "chat": chat, "fecha": hoy}
            est["cuenta"][hoy][quien] = hechas + 1
            extra = " (la primera temporada; si te gusta, pide el resto)" if tipo == "tv" and "seasons" in cuerpo \
                and cuerpo["seasons"] == [1] else ""
            texto = f"✅ Pedido: {titulo}{extra}. Te aviso en cuanto esté."
            telegram(TG_ADMIN, f"📥 {quien} ha pedido {titulo} desde {s.capitalize()}.")
        except LookupError:
            texto = f"⚠️ No he podido pedir {titulo}: tu usuario no está en Seerr. Avisa al administrador."
            telegram(TG_ADMIN, f"⚠️ {quien} ({s}) ha dado ❤️ a {titulo} pero no tiene usuario en Seerr.")
        except urllib.error.HTTPError as e:
            detalle = e.read().decode(errors="replace")[:300]
            if e.code == 403 and "uota" in detalle:
                texto = f"⏳ Has llegado a tu cupo en Seerr. Vuelve a darle ❤️ a {titulo} cuando se renueve."
            elif e.code == 409:
                est["pedidos"][clave] = {"nombre": nombre, "usuario": quien, "chat": chat, "fecha": hoy}
                texto = f"👍 {titulo} ya estaba pedido. Te aviso cuando esté."
            else:
                texto = f"⚠️ No he podido pedir {titulo}. Ya lo sabe el administrador."
                telegram(TG_ADMIN, f"⚠️ Seerr ha dado error {e.code} al pedir {titulo} para {quien}: {detalle[:150]}")
        except Exception as e:
            texto = f"⚠️ No he podido pedir {titulo} ahora mismo. Inténtalo más tarde."
            log("Error al pedir:", e)
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
        if estado >= (4 if tipo == "tv" else 5):
            log(f"Ya está: {p['nombre']} (lo pidió {p['usuario']})")
            telegram(p.get("chat"), f"🎉 Ya está disponible: <b>{p['nombre']}</b>. ¡A disfrutarlo!")
            if not PRUEBA:
                del est["pedidos"][clave]
                carpeta = next((c for c in os.listdir(CATALOGO) if f"[tmdbid-{tmdb}]" in c), None) \
                    if os.path.isdir(CATALOGO) else None
                if carpeta:   # ya está en la biblioteca de verdad: fuera del escaparate
                    shutil.rmtree(os.path.join(CATALOGO, carpeta), ignore_errors=True)


# ───────────────────────────── arranque ─────────────────────────────
def comprobar():
    faltan = [n for n, v in (("SEERR_URL", SEERR_URL), ("SEERR_API_KEY", SEERR_KEY)) if not v]
    if not SERVIDORES:
        faltan.append("JELLYFIN_URL + JELLYFIN_API_KEY o EMBY_URL + EMBY_API_KEY")
    if faltan:
        sys.exit("Falta configurar: " + ", ".join(faltan))
    try:
        seerr("GET", "/status")
    except Exception as e:
        sys.exit(f"No llego a Seerr en {SEERR_URL}: {e}")
    for s in SERVIDORES:
        try:
            servidor(s, "GET", "/System/Info")
        except Exception as e:
            sys.exit(f"No llego a {s} en {SERVIDORES[s][0]}: {e}")
    log(f"Pídelo {VERSION} · Seerr OK · {', '.join(s.capitalize() for s in SERVIDORES)} OK"
        + (" · Telegram activado" if TG_TOKEN else ""))


def main():
    orden = (sys.argv[1:] or ["servicio"])[0]
    comprobar()
    if orden in ("renovar", "prueba"):
        renovar()
    if orden in ("vigilar", "prueba"):
        vigilar()
    if orden != "servicio":
        return
    est = leer_estado()
    hoy = datetime.date.today().isoformat()
    if est.get("renovado") != hoy or not os.path.isdir(CATALOGO) or len(os.listdir(CATALOGO)) <= 1:
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
