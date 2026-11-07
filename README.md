<p align="center"><img src="docs/icono.png" width="110" alt="Favarr"></p>

<h1 align="center">Favarr</h1>

<p align="center">
  <b>Tus usuarios piden películas y series dándole al ❤️.</b><br>
  Sin apps nuevas, sin webs nuevas, sin contraseñas nuevas.
</p>

<p align="center">
  <a href="https://hub.docker.com/r/nemesbak/favarr"><img src="https://img.shields.io/docker/pulls/nemesbak/favarr?label=Docker&logo=docker&color=2496ED" alt="Docker"></a>
  <img src="https://img.shields.io/badge/Jellyfin-✔-AA5CC3?logo=jellyfin&logoColor=white" alt="Jellyfin">
  <img src="https://img.shields.io/badge/Emby-✔-52B54B?logo=emby&logoColor=white" alt="Emby">
  <img src="https://img.shields.io/badge/licencia-MIT-blue" alt="MIT">
</p>

<p align="center"><b>🇪🇸 Español</b> · <a href="README.en.md">🇬🇧 English</a></p>

---

## 🤔 ¿Qué es?

Tienes un servidor de películas en casa (Jellyfin o Emby) y gente que lo usa. Siempre pasa lo mismo:

> *«Oye, ¿puedes poner tal película?»* 📱 por WhatsApp, a las 11 de la noche.

**Favarr lo soluciona.** Pone en tu servidor una biblioteca nueva, **✨ Descubre y pide**, como un escaparate con lo que **está de moda y todavía no tienes**.

Para pedir algo **solo hay que darle al ❤️ (favorito)**, ese botón que todo el mundo ya conoce. Favarr se encarga del resto.

<p align="center"><img src="docs/portada.jpg" width="480" alt="Portada de la biblioteca"></p>

## ✨ Cómo funciona

```mermaid
flowchart LR
    A["📺 Tu usuario ve<br/>✨ Descubre y pide"] --> B["❤️ Le da a favorito"]
    B --> C["🤖 Favarr lo pide<br/>a Seerr en su nombre"]
    C --> D["⬇️ Se descarga"]
    D --> E["🎉 Aparece en<br/>tu biblioteca"]
```

1. **Cada noche** el escaparate se renueva con lo más popular que aún no tienes.
2. Alguien le da al **❤️**.
3. En **2 minutos** Favarr lo pide a Seerr **en nombre de esa persona** y le quita el ❤️.
4. Cuando ya está descargado, **sale del escaparate y aparece en tu biblioteca normal**.
5. Si usas **Telegram**, a esa persona le llegan dos mensajes: *«✅ Pedido»* y, más tarde, *«🎉 Ya está disponible»*.

Si alguien abre un título del escaparate sin darle al ❤️, ve este aviso:

<p align="center"><img src="docs/aviso.png" width="560" alt="Vídeo de aviso"></p>

> 💾 **No ocupa espacio.** Todos los títulos del escaparate son el mismo vídeo de aviso de 32 KB. 150 títulos ocupan **menos de 1 MB**.

---

## 📋 Antes de empezar

Necesitas tener ya funcionando:

| | Qué es | ¿Lo tengo? |
|---|---|---|
| 🎬 **Jellyfin** o **Emby** | Tu servidor de películas (vale con uno o con los dos) | ⬜ |
| 📨 **Seerr**, **Jellyseerr** u **Overseerr** | La web donde se piden películas y que avisa a Radarr/Sonarr | ⬜ |
| 🐳 **Docker** | Lo tienen Unraid, Synology, casi cualquier NAS o un PC | ⬜ |

> ⚠️ **Importante:** tus usuarios tienen que estar **importados en Seerr**. Así se hace en Seerr: ⚙️ Ajustes → Usuarios → **Importar usuarios de Jellyfin/Emby**. Si no, Favarr no sabe a nombre de quién pedir.

---

## 🚀 Instalación en 3 pasos

### Paso 1 · Copia las claves 🔑

Una **clave API** es como una contraseña para que Favarr pueda hablar con tus programas. Cópialas en un bloc de notas:

| Programa | Dónde encontrarla |
|---|---|
| **Seerr** | ⚙️ Ajustes → General → **Clave API** (botón de copiar) |
| **Jellyfin** | ⚙️ Panel de control → Avanzado → **Claves API** → botón **+** → nombre: `Favarr` |
| **Emby** | ⚙️ Ajustes → Avanzado → **Claves API** → **Nueva clave** → nombre: `Favarr` |

### Paso 2 · Elige la carpeta 📁

Favarr necesita una **carpeta nueva y vacía**, en el **mismo disco que tus películas**. No hace falta que la crees tú: Favarr la crea solo.

El truco es que esa carpeta tiene **dos nombres**: uno para tu NAS y otro para Jellyfin/Emby. Mira cómo ve Jellyfin tus películas y copia el mismo patrón:

| | Tus películas | La carpeta de Favarr |
|---|---|---|
| En tu NAS / Unraid | `/mnt/user/media/peliculas` | 👉 `/mnt/user/media/descubre` |
| Dentro de Jellyfin / Emby | `/media/peliculas` | 👉 `/media/descubre` |

> 🔎 **¿Cómo ve Jellyfin mis películas?** Panel de control → **Bibliotecas** → tu biblioteca de películas → mira la ruta que sale en **Carpetas**. En Emby: Ajustes → **Biblioteca** → tu biblioteca → **Carpetas**.

### Paso 3 · Instálalo 📦

<details open>
<summary><b>🟠 En Unraid (lo más fácil)</b></summary>
<br>

1. Abre la **terminal** de Unraid (el icono `>_` arriba a la derecha) y pega esta línea:
   ```bash
   wget -O /boot/config/plugins/dockerMan/templates-user/my-favarr.xml https://raw.githubusercontent.com/nemesbak/favarr/main/unraid/favarr.xml
   ```
2. Ve a la pestaña **Docker** → **Añadir contenedor** → en **Plantilla** elige **favarr**.
3. Rellena los huecos con lo de los pasos 1 y 2:
   - **Carpeta del escaparate:** `/mnt/user/media/descubre`
   - **Seerr URL** y **Seerr API key**
   - **Jellyfin URL**, **Jellyfin API key** y **Jellyfin: carpeta** (`/media/descubre`)
   - **Emby…:** lo mismo, si lo usas. Si no, déjalo vacío.
4. Pulsa **Aplicar**. ✅

</details>

<details>
<summary><b>🐳 Con docker compose (Synology, otros NAS, PC…)</b></summary>
<br>

1. Descarga el archivo [`docker-compose.yml`](docker-compose.yml) y guárdalo en una carpeta nueva llamada `favarr`.
2. Ábrelo con un editor de texto y cambia **solo las líneas marcadas con 👉**.
3. Abre una terminal en esa carpeta y escribe:
   ```bash
   docker compose up -d
   ```

</details>

### ¡Listo! 🎉

En un par de minutos aparece **✨ Descubre y pide** en Jellyfin y en Emby, con portada y carátulas. La ven solos los usuarios que tienen acceso a **todas las bibliotecas**. A los demás dásela desde su ficha en Jellyfin/Emby.

---

## ✅ Comprobar que funciona

Mira el registro del contenedor. En Unraid: Docker → icono de favarr → **Registros**. Con compose: `docker logs favarr`. Tienes que ver algo así:

```
Favarr 1.3.0 · Seerr ✔ · Jellyfin ✔ · Emby ✔
jellyfin: biblioteca «✨ Descubre y pide» creada ✔
Escaparate: 100 películas y 50 series (150 nuevas, 0 quitadas)
```

Cuando alguien pida algo, aparecerá así:

```
jellyfin · ana · Dune: Parte dos → ✅ Pedido: Dune: Parte dos. Te aviso en cuanto esté.
```

---

## 💬 Mensaje para tus usuarios

Puedes copiar y pegar esto en tu grupo:

> 🆕 **Novedad en el servidor: ✨ Descubre y pide**
>
> Ahí salen pelis y series que todavía no tenemos.
> ¿Te apetece alguna? **Dale al ❤️ (favorito)** y se pide sola. Cuando esté lista, aparecerá en el servidor.
>
> Cuentan tus cupos de siempre. De las series se pide la primera temporada.

---

## ❓ Preguntas frecuentes

<details>
<summary><b>¿Y si alguien le da ❤️ a todo? (los límites)</b></summary>

**Los límites los pones en Seerr**, como siempre: cuántas películas y cuántas temporadas puede pedir cada persona, y cada cuántos días. Favarr los respeta:

1. Antes de pedir nada, mira el **cupo que le queda** a esa persona en Seerr.
2. Si no le queda, **no pide nada**: le quita el ❤️ y le avisa. Por ejemplo: *«⏳ Tu cupo es de 1 película cada 30 días y ya lo has usado. Vuelve a darle ❤️ cuando se renueve.»*
3. Si cambias el cupo en Seerr (a todos o a una persona), **Favarr lo aplica al momento**.

Además, de las series se pide solo la **1.ª temporada**, para no gastar el cupo de golpe. Si le gusta, que pida el resto.

Si quieres un freno extra, puedes poner `LIMITE_DIA` y `MAX_PENDIENTES` (ver los ajustes).
</details>

<details>
<summary><b>¿A nombre de quién se pide?</b></summary>

De quien le dio al ❤️. Así cuenta en sus cupos de Seerr y sabes quién pidió qué.
</details>

<details>
<summary><b>¿Y si rechazo una petición en Seerr?</b></summary>

Favarr se da cuenta solo: la olvida y avisa a esa persona con un *«❌ Al final no se ha podido conseguir…»*. Si alguien vuelve a darle ❤️, se pide de nuevo.
</details>

<details>
<summary><b>¿Por qué no salen los estrenos de cine?</b></summary>

Porque todavía no se pueden descargar. Salen solos en cuanto se pueden ver en casa (plataformas o Blu-ray).
</details>

<details>
<summary><b>¿Puedo quitar el escaparate a algún usuario?</b></summary>

Sí. Es una biblioteca normal: en la ficha de ese usuario, en Jellyfin o Emby, desmarca **✨ Descubre y pide**.
</details>

<details>
<summary><b>¿Cómo activo los avisos por Telegram?</b></summary>

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram, escribe `/newbot` y sigue los pasos. Te dará un **token**: ponlo en `TELEGRAM_TOKEN`.
2. Escribe a [@userinfobot](https://t.me/userinfobot) para saber **tu número de chat** y ponlo en `TELEGRAM_ADMIN`. Ahí te llegará cada petición y cada problema.
3. Para avisar a tus usuarios:
   - Cada uno escribe una vez a tu bot y te pasa su número.
   - Tú los apuntas así: `TELEGRAM_USUARIOS=ana=123456,juan=789012`.
   - El nombre es el de su usuario de Jellyfin/Emby.
</details>

<details>
<summary><b>¿Puedo probarlo sin que cambie nada?</b></summary>

Sí. Esto te dice lo que haría, sin hacerlo:
```bash
docker exec favarr python favarr.py prueba
```
</details>

---

## 🛠️ Si algo no va

| Lo que ves | Qué hacer |
|---|---|
| `la clave API no es correcta` | Vuelve a copiar la clave (paso 1). Que no tenga espacios al principio ni al final. |
| `no contesta: revisa la dirección y el puerto` | Usa la **IP** del equipo (`http://192.168.1.10:8096`), no `localhost`. |
| `sin JELLYFIN_CARPETA no creo la biblioteca` | Rellena **Jellyfin: carpeta**, o crea tú la biblioteca (ver abajo). |
| La biblioteca sale **vacía** | La carpeta de Jellyfin/Emby no coincide con la del NAS. Repasa el paso 2. |
| En Emby salen **carpetas** en vez de carátulas | La biblioteca tiene un tipo equivocado. Bórrala y deja que Favarr la cree, o créala como **Contenido mixto**. |
| `tu usuario no está en Seerr` | Importa a esa persona en Seerr (⚙️ Ajustes → Usuarios). |
| `no tiene permiso para pedir en Seerr` | En Seerr → Usuarios → esa persona → **Permisos**: marca **Pedir**. |

<details>
<summary><b>Crear la biblioteca a mano</b> (solo si no rellenas «carpeta»)</summary>
<br>

| | Jellyfin | Emby |
|---|---|---|
| Dónde | Panel de control → Bibliotecas → **Añadir** | Ajustes → Biblioteca → **Nueva biblioteca** |
| Tipo | **Películas y series mezcladas** | **Contenido mixto** |
| Nombre | `✨ Descubre y pide` | `✨ Descubre y pide` |
| Carpeta | la del paso 2 (`/media/descubre`) | la del paso 2 |
| Imágenes | Activa **TheMovieDb** el primero | Activa **TheMovieDb** el primero |

</details>

---

## 🔄 Actualizar y desinstalar

- **Actualizar:**
  - En Unraid: Docker → **Buscar actualizaciones**.
  - Con compose: `docker compose pull && docker compose up -d`.
- **Desinstalar:** borra el contenedor, la biblioteca **✨ Descubre y pide** y la carpeta. Favarr no toca **nada más** de tu servidor: ni tus películas, ni tus usuarios, ni tus otras bibliotecas.

---

## ⚙️ Todos los ajustes

| Ajuste | Para qué sirve | Por defecto |
|---|---|---|
| `SEERR_URL` · `SEERR_API_KEY` | Dirección y clave de Seerr | — |
| `JELLYFIN_URL` · `JELLYFIN_API_KEY` | Dirección y clave de Jellyfin | — |
| `JELLYFIN_CARPETA` | La carpeta vista desde Jellyfin (para crear la biblioteca solo) | — |
| `EMBY_URL` · `EMBY_API_KEY` · `EMBY_CARPETA` | Lo mismo para Emby | — |
| `IDIOMA` | `es` o `en`: títulos, mensajes y nombre de la biblioteca | `es` |
| `NOMBRE_BIBLIOTECA` | Nombre de la biblioteca | `✨ Descubre y pide` |
| `PELICULAS` · `SERIES` | Cuántas enseñar en el escaparate | `100` · `50` |
| `LIMITE_DIA` | Freno extra: peticiones por persona y día (`0` = solo el cupo de Seerr) | `0` |
| `MAX_PENDIENTES` | Freno extra: peticiones esperando a la vez (`0` = solo el cupo de Seerr) | `0` |
| `SOLO_TEMPORADA_1` | Series: pedir solo la 1.ª temporada (`si` / `no`) | `si` |
| `CADA_MINUTOS` | Cada cuánto mira los ❤️ | `2` |
| `HORA_RENOVAR` | A qué hora cambia el escaparate (0-23) | `4` |
| `TELEGRAM_TOKEN` · `TELEGRAM_ADMIN` · `TELEGRAM_USUARIOS` | Avisos por Telegram (opcional) | — |
| `TZ` | Tu zona horaria | `Europe/Madrid` |

---

<p align="center">
  Hecho con ❤️ para servidores caseros.<br>
  ¿Te ha gustado? Dale una ⭐ al proyecto. ¿Algo no va? <a href="https://github.com/nemesbak/favarr/issues">Cuéntamelo aquí</a>.<br>
  <sub>Licencia MIT: úsalo, cámbialo y compártelo.</sub>
</p>
