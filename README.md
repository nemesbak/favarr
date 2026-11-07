<p align="center"><img src="docs/icono.png" width="96"></p>

<h1 align="center">Favarr</h1>
<p align="center"><b>Tus usuarios piden películas y series dándole al ❤️. Nada más.</b></p>
<p align="center"><a href="README.en.md">🇬🇧 English</a></p>

---

## ¿Qué hace?

Te aparece una biblioteca nueva en Jellyfin o Emby: **✨ Descubre y pide**.

Dentro salen las películas y series **de moda que todavía no tienes**.

👉 Alguien le da al **❤️ (favorito)** → Favarr lo **pide solo** → cuando se descarga, **aparece en tu servidor**.

Tus usuarios no tienen que instalar nada ni aprender nada nuevo. Si abren uno de esos títulos sin darle al ❤️, ven este aviso:

<p align="center"><img src="docs/aviso.png" width="560"></p>

---

## Lo que necesitas

✅ **Jellyfin** o **Emby** (o los dos)
✅ **Seerr**, **Jellyseerr** u **Overseerr**, que ya pide tus películas
✅ **Docker** (por ejemplo en Unraid)

---

## Instalación

### 1️⃣ Copia 2 claves (o 3)

Son como contraseñas para que Favarr pueda hablar con tus programas.

| Programa | Dónde está la clave |
|---|---|
| **Seerr** | ⚙️ Ajustes → General → **Clave API** |
| **Jellyfin** | ⚙️ Panel de control → **Claves API** → botón **+** |
| **Emby** | ⚙️ Ajustes → **Claves API** → **Nueva clave** |

### 2️⃣ Instálalo

<details open>
<summary><b>En Unraid</b></summary>

1. Abre la terminal de Unraid (icono `>_` arriba a la derecha) y pega esto:
   ```
   wget -O /boot/config/plugins/dockerMan/templates-user/my-favarr.xml https://raw.githubusercontent.com/nemesbak/favarr/main/unraid/favarr.xml
   ```
2. Ve a **Docker** → **Añadir contenedor** → en *Plantilla* elige **favarr**.
3. Rellena los huecos: las direcciones y las claves del paso 1.
4. Pulsa **Aplicar**.

</details>

<details>
<summary><b>Con docker compose (cualquier otro sistema)</b></summary>

1. Descarga [`docker-compose.yml`](docker-compose.yml).
2. Ábrelo con el Bloc de notas y cambia **solo las líneas con 👉**.
3. En esa carpeta ejecuta: `docker compose up -d`

</details>

### 3️⃣ Ya está 🎉

En un par de minutos aparece **✨ Descubre y pide** en Jellyfin y en Emby, con portada y carátulas.

Si la creas tú, recuerda el tipo:
- En Jellyfin: **Películas y series mezcladas**.
- En Emby: **Contenido mixto**.

---

## La única parte con truco: la carpeta

Favarr necesita **una carpeta nueva y vacía**, en el **mismo disco que tus películas**. Por ejemplo, si tus películas están en `/mnt/user/media/peliculas`, usa `/mnt/user/media/descubre`.

Jellyfin y Emby suelen ver esa carpeta con **otro nombre**. Para saber cuál:

1. Mira cómo ven tus películas. Lo pone en la biblioteca de películas → **Carpetas**.
2. Si allí sale `/media/peliculas`, la tuya será **`/media/descubre`**.

Eso es lo que va en **«Jellyfin: carpeta»** y en **«Emby: carpeta»**.

> 💡 No ocupa nada: los títulos del escaparate son un vídeo de aviso de 32 KB compartido. 150 títulos ocupan menos de 1 MB.

---

## Preguntas

**¿A nombre de quién se pide?**
De quien le dio al ❤️, así que cuenta en sus cupos de Seerr. Si esa persona no tiene usuario en Seerr, no se pide nada.

**¿Y si alguien le da ❤️ a todo?**
Por defecto, cada persona puede:
- pedir **3 al día**;
- tener **5 esperando** a la vez;
- pedir solo la **primera temporada** de las series.

Los administradores no tienen límites. Todo se puede cambiar.

**¿Por qué no salen los estrenos de cine?**
Porque aún no se pueden conseguir. Solo salen cuando ya se pueden ver en casa.

**¿Avisa por Telegram?**
Si quieres, sí:
1. Crea un bot con [@BotFather](https://t.me/BotFather) y pega su clave en `TELEGRAM_TOKEN`.
2. Pon tu número de chat en `TELEGRAM_ADMIN`. Lo sabes escribiendo a [@userinfobot](https://t.me/userinfobot).
3. Para avisar a tus usuarios, ponlos así: `TELEGRAM_USUARIOS=ana=123456,juan=789012`.

**¿Puedo probar sin que cambie nada?**
Sí, con `docker exec favarr python favarr.py prueba`. Te dice lo que haría, sin hacerlo.

**¿Cómo lo quito?**
Borra el contenedor, la biblioteca y la carpeta. Favarr no toca nada más.

---

<details>
<summary>Todos los ajustes</summary>

| Ajuste | Qué hace | Por defecto |
|---|---|---|
| `IDIOMA` | `es` o `en` | `es` |
| `NOMBRE_BIBLIOTECA` | Nombre de la biblioteca | `✨ Descubre y pide` |
| `PELICULAS` / `SERIES` | Cuántas enseñar | `100` / `50` |
| `LIMITE_DIA` | Peticiones por persona y día (0 = sin límite) | `3` |
| `MAX_PENDIENTES` | Esperando a la vez (0 = sin límite) | `5` |
| `SOLO_TEMPORADA_1` | Series: solo la 1.ª temporada | `si` |
| `CADA_MINUTOS` | Cada cuánto mira los ❤️ | `2` |
| `HORA_RENOVAR` | A qué hora cambia el escaparate | `4` |

</details>

<p align="center">Hecho con ❤️ para servidores caseros · Licencia MIT</p>
