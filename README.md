# Pídelo ❤️

**Pide películas y series desde Jellyfin o Emby dándole a «favorito».**

Pídelo añade a tu servidor una biblioteca nueva, **«Descubre»**. En ella salen las películas y series de moda que **todavía no tienes**.

Para pedir algo, tus usuarios solo tienen que darle al **❤️**. No necesitan otra app, ni otra web, ni otra contraseña.

![Lo que ve quien abre un título del escaparate](docs/aviso.png)

---

## ¿Cómo funciona?

1. Cada noche Pídelo llena la biblioteca **Descubre** con lo más popular que aún no tienes.
2. Alguien entra y le da **❤️** a algo que le apetece ver.
3. En un par de minutos, Pídelo lo pide **en nombre de esa persona** a Seerr (Jellyseerr u Overseerr) y le quita el ❤️.
4. Cuando ya se ha descargado, desaparece de «Descubre» y aparece en tu biblioteca normal.
5. Si usas Telegram, la persona recibe dos mensajes: «✅ Pedido» y, cuando llega, «🎉 Ya está disponible».

Ocupa casi nada: los títulos del escaparate son un vídeo de aviso de 26 KB. Unos 150 títulos ocupan **menos de 1 MB** en total.

---

## Qué necesitas

- **Jellyfin**, **Emby** o los dos.
- **Seerr**, **Jellyseerr** u **Overseerr**, ya conectado a tu servidor y a Radarr/Sonarr.
- **Docker** (en Unraid, Synology, un NAS, un PC… donde ya tengas lo demás).

---

## Instalación (10 minutos)

### Paso 1 · Consigue las claves

- **Seerr:** *Ajustes → General → Clave API*. Copia la clave.
- **Jellyfin:** *Panel de control → Claves API → ➕*. Ponle de nombre «Pídelo» y copia la clave.
- **Emby:** *Ajustes → Claves API → Nueva clave*. Ponle de nombre «Pídelo» y copia la clave.

### Paso 2 · Crea una carpeta vacía

Crea la carpeta **junto a tus películas** (en el mismo disco o recurso compartido), por ejemplo:

```
/mnt/user/media/descubre
```

### Paso 3 · Prepara los archivos

1. Crea una carpeta llamada `pidelo` donde guardes tus Docker.
2. Copia dentro estos dos archivos de este repositorio:
   - [`docker-compose.yml`](docker-compose.yml)
   - [`config.env.ejemplo`](config.env.ejemplo), con el nombre cambiado a **`config.env`**.
3. Abre `config.env` con cualquier editor de texto. Pega tus direcciones y claves donde pone `pega-aqui…`.
4. Abre `docker-compose.yml` y cambia `/ruta/a/tu/media/descubre` por la carpeta del paso 2.

### Paso 4 · Arráncalo

```
docker compose up -d
```

En un par de minutos la carpeta se llenará de títulos. Para ver qué está haciendo:

```
docker logs pidelo
```

### Paso 5 · Crea la biblioteca en Jellyfin / Emby

1. Crea una biblioteca nueva:
   - En Jellyfin: *Panel de control → Bibliotecas → Añadir biblioteca*.
   - En Emby: *Ajustes → Biblioteca → Nueva biblioteca*.
2. **Tipo de contenido:**
   - En Jellyfin: **Películas y series mezcladas**.
   - En Emby: **Contenido mixto**.
3. **Nombre:** cualquiera que contenga la palabra **Descubre**. Por ejemplo: `✨ Descubre y pide`.
4. **Carpeta:** la del paso 2.
5. Activa **TheMovieDb** en las descargas de imágenes y metadatos, para que salgan las carátulas.
6. Dale acceso a los usuarios que quieras.

¡Listo! 🎉

---

## Preguntas frecuentes

**¿Y si alguien le da ❤️ a 50 cosas?**
Por defecto, cada persona puede pedir **3 al día** y tener **5 esperando** a la vez. Las series se piden solo con la **primera temporada**. Si le gusta, que pida el resto en Seerr. Los administradores no tienen límite. Además, se respetan los cupos que tengas puestos en Seerr. Todo esto se cambia en `config.env`.

**¿A nombre de quién se pide?**
De la persona que le dio al ❤️. Pídelo la busca en Seerr por su usuario de Jellyfin, o por su nombre de usuario si usas Emby. Así cuenta en sus cupos y ves quién pidió qué. Si no la encuentra, no pide nada y avisa al administrador.

**¿Por qué no salen las películas que están en el cine?**
Porque todavía no se pueden conseguir. Solo salen las que ya tienen estreno digital o en disco.

**¿Puedo borrar la biblioteca y olvidarme?**
Sí. Para el Docker, borra la biblioteca y borra la carpeta. Pídelo no toca nada más de tu servidor.

**¿Cómo pruebo sin que cambie nada?**
```
docker compose run --rm pidelo python pidelo.py prueba
```
Te dice lo que haría, sin hacerlo.

**¿Cómo activo los avisos por Telegram?**
1. Crea un bot hablando con [@BotFather](https://t.me/BotFather) y pega su token en `TELEGRAM_TOKEN`.
2. En `TELEGRAM_ADMIN` pon tu número de chat. Ahí recibirás cada petición y cada problema. Para saber tu número, escribe a [@userinfobot](https://t.me/userinfobot).
3. Para que tus usuarios reciban sus avisos, añádelos a `TELEGRAM_USUARIOS`, así: `ana=123456,juan=789012`. Antes, cada persona tiene que haberle escrito una vez al bot.

---

## Todos los ajustes

| Ajuste | Para qué sirve | Por defecto |
|---|---|---|
| `NOMBRE_BIBLIOTECA` | Palabra que debe llevar el nombre de la biblioteca | `Descubre` |
| `PELICULAS` / `SERIES` | Cuántas enseñar en el escaparate | `100` / `50` |
| `IDIOMA` | Idioma de los títulos | `es` |
| `LIMITE_DIA` | Peticiones por persona y día (0 = sin límite) | `3` |
| `MAX_PENDIENTES` | Peticiones esperando a la vez por persona (0 = sin límite) | `5` |
| `SOLO_TEMPORADA_1` | Pedir solo la 1.ª temporada de las series | `si` |
| `CADA_MINUTOS` | Cada cuánto mira los ❤️ | `2` |
| `HORA_RENOVAR` | A qué hora renueva el escaparate | `4` |

---

Hecho con cariño para servidores caseros. Licencia MIT: úsalo, cámbialo y compártelo.
