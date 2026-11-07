<p align="center"><img src="docs/icono.png" width="96"></p>

<h1 align="center">Favarr</h1>
<p align="center"><b>Your users request movies and shows by tapping ❤️. That's it.</b></p>
<p align="center"><a href="README.md">🇪🇸 Español</a></p>

---

## What does it do?

A new library appears in Jellyfin or Emby: **✨ Discover & request**.

It shows the **trending movies and shows you don't have yet**.

👉 Someone taps **❤️ (favourite)** → Favarr **requests it for them** → once downloaded, **it shows up on your server**.

Your users don't install anything or learn anything new. If they open one of those titles without tapping ❤️, they see this notice:

<p align="center"><img src="docs/aviso.png" width="560"></p>

---

## What you need

✅ **Jellyfin** or **Emby** (or both)
✅ **Seerr**, **Jellyseerr** or **Overseerr**, already requesting your movies
✅ **Docker** (for example on Unraid)

---

## Install

### 1️⃣ Copy 2 keys (or 3)

They're like passwords so Favarr can talk to your apps.

| App | Where the key is |
|---|---|
| **Seerr** | ⚙️ Settings → General → **API Key** |
| **Jellyfin** | ⚙️ Dashboard → **API Keys** → **+** button |
| **Emby** | ⚙️ Settings → **API Keys** → **New key** |

### 2️⃣ Install it

<details open>
<summary><b>On Unraid</b></summary>

1. Open the Unraid terminal (the `>_` icon, top right) and paste this:
   ```
   wget -O /boot/config/plugins/dockerMan/templates-user/my-favarr.xml https://raw.githubusercontent.com/nemesbak/favarr/main/unraid/favarr.xml
   ```
2. Go to **Docker** → **Add Container** → under *Template* pick **favarr**.
3. Fill in the blanks: the addresses and the keys from step 1.
4. Click **Apply**.

</details>

<details>
<summary><b>With docker compose (any other system)</b></summary>

1. Download [`docker-compose.yml`](docker-compose.yml).
2. Open it with Notepad and change **only the 👉 lines**. Also set `IDIOMA: en`.
3. In that folder run: `docker compose up -d`

</details>

### 3️⃣ Done 🎉

In a couple of minutes **✨ Discover & request** appears in Jellyfin and in Emby, with its cover and posters.

If you create the library yourself, pick the right type:
- In Jellyfin: **Mixed movies and shows**.
- In Emby: **Mixed content**.

---

## The only tricky bit: the folder

Favarr needs **a new, empty folder** on the **same disk as your movies**. For example, if your movies are in `/mnt/user/media/movies`, use `/mnt/user/media/discover`.

Jellyfin and Emby usually see that folder under **a different name**. To find it:

1. Check how they see your movies. It's in your movie library → **Folders**.
2. If it shows `/media/movies`, yours will be **`/media/discover`**.

That's what goes in **"Jellyfin: folder"** and **"Emby: folder"**.

> 💡 It takes no space: every showcase title is the same shared 32 KB notice video. 150 titles use less than 1 MB.

---

## Questions

**Who is the request made for?**
The person who tapped ❤️, so it counts towards their Seerr quota. If that person has no Seerr user, nothing is requested.

**What if someone taps ❤️ on everything?**
By default, each person can:
- make **3 requests a day**;
- have **5 waiting** at once;
- request only the **first season** of a show.

Admins have no limits. You can change all of this.

**Why don't cinema releases show up?**
Because they can't be downloaded yet. They appear once they're out for home viewing.

**Does it send Telegram messages?**
If you want:
1. Create a bot with [@BotFather](https://t.me/BotFather) and paste its token in `TELEGRAM_TOKEN`.
2. Put your chat number in `TELEGRAM_ADMIN`. Message [@userinfobot](https://t.me/userinfobot) to get it.
3. To notify your users, list them like this: `TELEGRAM_USUARIOS=ana=123456,john=789012`.

**Can I try it without changing anything?**
Yes, with `docker exec favarr python favarr.py test`. It tells you what it would do, without doing it.

**How do I remove it?**
Delete the container, the library and the folder. Favarr touches nothing else.

---

<details>
<summary>All settings</summary>

| Setting | What it does | Default |
|---|---|---|
| `IDIOMA` | Language: `es` or `en` | `es` |
| `NOMBRE_BIBLIOTECA` | Library name | `✨ Discover & request` |
| `PELICULAS` / `SERIES` | How many movies / shows | `100` / `50` |
| `LIMITE_DIA` | Requests per person per day (0 = unlimited) | `3` |
| `MAX_PENDIENTES` | Waiting at once (0 = unlimited) | `5` |
| `SOLO_TEMPORADA_1` | Shows: first season only (`si` / `no`) | `si` |
| `CADA_MINUTOS` | How often it checks the ❤️ | `2` |
| `HORA_RENOVAR` | Hour the showcase refreshes | `4` |

</details>

<p align="center">Made with ❤️ for home servers · MIT licence</p>
