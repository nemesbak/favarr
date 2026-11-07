<p align="center"><img src="docs/icono.png" width="110" alt="Favarr"></p>

<h1 align="center">Favarr</h1>

<p align="center">
  <b>Your users request movies and shows by tapping ❤️.</b><br>
  No new apps, no new websites, no new passwords.
</p>

<p align="center">
  <a href="https://hub.docker.com/r/nemesbak/favarr"><img src="https://img.shields.io/docker/pulls/nemesbak/favarr?label=Docker&logo=docker&color=2496ED" alt="Docker"></a>
  <img src="https://img.shields.io/badge/Jellyfin-✔-AA5CC3?logo=jellyfin&logoColor=white" alt="Jellyfin">
  <img src="https://img.shields.io/badge/Emby-✔-52B54B?logo=emby&logoColor=white" alt="Emby">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT">
</p>

<p align="center"><a href="README.md">🇪🇸 Español</a> · <b>🇬🇧 English</b></p>

---

## 🤔 What is it?

You run a movie server at home (Jellyfin or Emby) and people use it. It always goes the same way:

> *"Hey, can you add that movie?"* 📱 on WhatsApp, at 11 pm.

**Favarr fixes that.** It adds a new library to your server, **✨ Discover & request**: a showcase of what's **trending and you don't have yet**.

To request something, **they just tap ❤️ (favourite)**, the button everyone already knows. Favarr does the rest.

<p align="center"><img src="docs/portada.jpg" width="480" alt="Library cover"></p>

## ✨ How it works

```mermaid
flowchart LR
    A["📺 Your user browses<br/>✨ Discover & request"] --> B["❤️ Taps favourite"]
    B --> C["🤖 Favarr requests it<br/>in Seerr for them"]
    C --> D["⬇️ It downloads"]
    D --> E["🎉 It shows up<br/>in your library"]
```

1. **Every night** the showcase refreshes with the most popular titles you don't have.
2. Someone taps **❤️**.
3. Within **2 minutes** Favarr requests it in Seerr **on that person's behalf** and removes the ❤️.
4. Once downloaded, it **leaves the showcase and appears in your normal library**.
5. If you use **Telegram**, that person gets two messages: *"✅ Requested"* and, later, *"🎉 Now available"*.

If someone opens a showcase title without tapping ❤️, they see this notice:

<p align="center"><img src="docs/aviso.png" width="560" alt="Notice video"></p>

> 💾 **It takes no space.** Every showcase title is the same 32 KB notice video. 150 titles use **less than 1 MB**.

---

## 📋 Before you start

You need these already running:

| | What it is | Got it? |
|---|---|---|
| 🎬 **Jellyfin** or **Emby** | Your movie server (one or both) | ⬜ |
| 📨 **Seerr**, **Jellyseerr** or **Overseerr** | The request website that tells Radarr/Sonarr what to get | ⬜ |
| 🐳 **Docker** | Unraid, Synology, almost any NAS or a PC have it | ⬜ |

> ⚠️ **Important:** your users must be **imported into Seerr**. In Seerr: ⚙️ Settings → Users → **Import Jellyfin/Emby users**. Otherwise Favarr can't tell who it's requesting for.

---

## 🚀 Install in 3 steps

### Step 1 · Copy the keys 🔑

An **API key** is like a password that lets Favarr talk to your apps. Copy them into a notepad:

| App | Where to find it |
|---|---|
| **Seerr** | ⚙️ Settings → General → **API Key** (copy button) |
| **Jellyfin** | ⚙️ Dashboard → Advanced → **API Keys** → **+** button → name: `Favarr` |
| **Emby** | ⚙️ Settings → Advanced → **API Keys** → **New key** → name: `Favarr` |

### Step 2 · Pick the folder 📁

Favarr needs a **new, empty folder** on the **same disk as your movies**. You don't have to create it yourself: Favarr creates it.

The trick is that this folder has **two names**: one for your NAS and one for Jellyfin/Emby. Check how Jellyfin sees your movies and follow the same pattern:

| | Your movies | Favarr's folder |
|---|---|---|
| On your NAS / Unraid | `/mnt/user/media/movies` | 👉 `/mnt/user/media/discover` |
| Inside Jellyfin / Emby | `/media/movies` | 👉 `/media/discover` |

> 🔎 **How does Jellyfin see my movies?** Dashboard → **Libraries** → your movie library → look at the path under **Folders**. In Emby: Settings → **Library** → your library → **Folders**.

### Step 3 · Install it 📦

<details open>
<summary><b>🟠 On Unraid (easiest)</b></summary>
<br>

1. Open the Unraid **terminal** (the `>_` icon, top right) and paste this line:
   ```bash
   wget -O /boot/config/plugins/dockerMan/templates-user/my-favarr.xml https://raw.githubusercontent.com/nemesbak/favarr/main/unraid/favarr.xml
   ```
2. Go to the **Docker** tab → **Add Container** → under **Template** pick **favarr**.
3. Fill in the blanks with what you got in steps 1 and 2:
   - **Showcase folder:** `/mnt/user/media/discover`
   - **Seerr URL** and **Seerr API key**
   - **Jellyfin URL**, **Jellyfin API key** and **Jellyfin: folder** (`/media/discover`)
   - **Emby…:** the same, if you use it. If not, leave it empty.
   - **Language:** `en`
4. Click **Apply**. ✅

</details>

<details>
<summary><b>🐳 With docker compose (Synology, other NAS, PC…)</b></summary>
<br>

1. Download [`docker-compose.yml`](docker-compose.yml) and save it in a new folder called `favarr`.
2. Open it with a text editor and change **only the 👉 lines**. Set `IDIOMA: en` for English.
3. Open a terminal in that folder and run:
   ```bash
   docker compose up -d
   ```

</details>

### Done! 🎉

In a couple of minutes **✨ Discover & request** appears in Jellyfin and in Emby, with its cover and posters. Users who have access to **all libraries** see it straight away. For everyone else, give it to them from their user page in Jellyfin/Emby.

---

## ✅ Check it works

Look at the container log. On Unraid: Docker → favarr icon → **Logs**. With compose: `docker logs favarr`. You should see something like:

```
Favarr 1.2.0 · Seerr ✔ · Jellyfin ✔ · Emby ✔
jellyfin: biblioteca «✨ Discover & request» creada ✔
Escaparate: 100 películas y 50 series (150 nuevas, 0 quitadas)
```

> The log is in Spanish for now; the messages your users get follow `IDIOMA`.

When someone requests something you'll see:

```
jellyfin · ana · Dune: Part Two → ✅ Requested: Dune: Part Two. I'll let you know as soon as it's ready.
```

---

## 💬 Message for your users

Copy and paste this into your group chat:

> 🆕 **New on the server: ✨ Discover & request**
>
> It shows movies and shows we don't have yet.
> Fancy one? **Tap ❤️ (favourite)** and it gets requested automatically. When it's ready, it'll show up on the server.
>
> Your usual request quota applies. For shows, the first season is requested.

---

## ❓ FAQ

<details>
<summary><b>What if someone taps ❤️ on everything? (limits)</b></summary>

**You set the limits in Seerr**, as usual: how many movies and seasons each person can request, and every how many days. Favarr follows them:

1. Before requesting anything, it checks how much **quota** that person has left in Seerr.
2. If there's none left, it **requests nothing**: it removes the ❤️ and tells them. For example: *"⏳ Your quota is 1 movie every 30 days and you've used it. Tap ❤️ again when it resets."*
3. If you change a quota in Seerr (for everyone or for one person), **Favarr follows it straight away**.

Also, only the **first season** of a show is requested, so the quota isn't used up in one go. If they like it, they can request the rest.

Want an extra brake? Set `LIMITE_DIA` and `MAX_PENDIENTES` (see the settings).
</details>

<details>
<summary><b>Who is the request made for?</b></summary>

Whoever tapped ❤️. It counts towards their Seerr quota and you can see who asked for what.
</details>

<details>
<summary><b>Why don't cinema releases show up?</b></summary>

Because they can't be downloaded yet. They appear by themselves once they're out for home viewing (streaming or Blu-ray).
</details>

<details>
<summary><b>Can I hide the showcase from some users?</b></summary>

Yes. It's a normal library: on that user's page in Jellyfin or Emby, untick **✨ Discover & request**.
</details>

<details>
<summary><b>How do I turn on Telegram messages?</b></summary>

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot` and follow the steps. You'll get a **token**: put it in `TELEGRAM_TOKEN`.
2. Message [@userinfobot](https://t.me/userinfobot) to get **your chat number** and put it in `TELEGRAM_ADMIN`. You'll get every request and every problem there.
3. To notify your users:
   - Each one messages your bot once and sends you their number.
   - You list them like this: `TELEGRAM_USUARIOS=ana=123456,john=789012`.
   - The name is their Jellyfin/Emby username.
</details>

<details>
<summary><b>Can I try it without changing anything?</b></summary>

Yes. This tells you what it would do, without doing it:
```bash
docker exec favarr python favarr.py test
```
</details>

---

## 🛠️ If something's wrong

| What you see | What to do |
|---|---|
| `wrong API key` | Copy the key again (step 1). Make sure there are no spaces at the start or the end. |
| `no answer: check address and port` | Use the machine's **IP** (`http://192.168.1.10:8096`), not `localhost`. |
| `sin JELLYFIN_CARPETA…` | Fill in **Jellyfin: folder**, or create the library yourself (see below). |
| The library is **empty** | The Jellyfin/Emby folder doesn't match the NAS one. Go over step 2 again. |
| Emby shows **folders** instead of posters | The library has the wrong type. Delete it and let Favarr create it, or create it as **Mixed content**. |
| `your user isn't in Seerr` | Import that person into Seerr (⚙️ Settings → Users). |
| `isn't allowed to request in Seerr` | Seerr → Users → that person → **Permissions**: tick **Request**. |

<details>
<summary><b>Creating the library by hand</b> (only if you leave "folder" empty)</summary>
<br>

| | Jellyfin | Emby |
|---|---|---|
| Where | Dashboard → Libraries → **Add** | Settings → Library → **New library** |
| Type | **Mixed movies and shows** | **Mixed content** |
| Name | `✨ Discover & request` | `✨ Discover & request` |
| Folder | the one from step 2 (`/media/discover`) | the one from step 2 |
| Images | Tick **TheMovieDb** first | Tick **TheMovieDb** first |

</details>

---

## 🔄 Update and uninstall

- **Update:**
  - On Unraid: Docker → **Check for updates**.
  - With compose: `docker compose pull && docker compose up -d`.
- **Uninstall:** delete the container, the **✨ Discover & request** library and the folder. Favarr touches **nothing else** on your server: not your movies, not your users, not your other libraries.

---

## ⚙️ All settings

| Setting | What it's for | Default |
|---|---|---|
| `SEERR_URL` · `SEERR_API_KEY` | Seerr address and key | — |
| `JELLYFIN_URL` · `JELLYFIN_API_KEY` | Jellyfin address and key | — |
| `JELLYFIN_CARPETA` | The folder as Jellyfin sees it (to create the library automatically) | — |
| `EMBY_URL` · `EMBY_API_KEY` · `EMBY_CARPETA` | The same for Emby | — |
| `IDIOMA` | Language: `es` or `en` (titles, messages and library name) | `es` |
| `NOMBRE_BIBLIOTECA` | Library name | `✨ Discover & request` |
| `PELICULAS` · `SERIES` | How many movies / shows in the showcase | `100` · `50` |
| `LIMITE_DIA` | Extra brake: requests per person per day (`0` = Seerr quota only) | `0` |
| `MAX_PENDIENTES` | Extra brake: requests waiting at once (`0` = Seerr quota only) | `0` |
| `SOLO_TEMPORADA_1` | Shows: request only the first season (`si` / `no`) | `si` |
| `CADA_MINUTOS` | How often it checks the ❤️ | `2` |
| `HORA_RENOVAR` | Hour the showcase refreshes (0-23) | `4` |
| `TELEGRAM_TOKEN` · `TELEGRAM_ADMIN` · `TELEGRAM_USUARIOS` | Telegram messages (optional) | — |
| `TZ` | Your time zone | `Europe/Madrid` |

---

<p align="center">
  Made with ❤️ for home servers.<br>
  Like it? Give the project a ⭐. Something wrong? <a href="https://github.com/nemesbak/favarr/issues">Tell me here</a>.<br>
  <sub>MIT licence: use it, change it, share it.</sub>
</p>
