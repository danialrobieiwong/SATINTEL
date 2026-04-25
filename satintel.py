#!/usr/bin/env python3
# SATINTEL - satellite OSINT tool, runs from your terminal
# needs free API keys from space-track.org and n2yo.com

import os
import sys
import subprocess
from pathlib import Path

# auto-install deps if missing
REQUIRED = {"requests": "requests", "rich": "rich", "dotenv": "python-dotenv"}

def _ensure_packages():
    missing = []
    for import_name, pip_name in REQUIRED.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"\n[SATINTEL] Installing: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + missing)
        print("[SATINTEL] Done. Starting...\n")

_ensure_packages()

import tty
import termios
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich import box
from rich.rule import Rule

load_dotenv()

console = Console()

def masked_input(prompt: str) -> str:
    """password input that shows * for each character typed"""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdout.write(prompt)
        sys.stdout.flush()
        password = ""
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            elif ch == "\x7f":  # backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":  # ctrl+c
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise KeyboardInterrupt
            elif ch >= " ":  # ignore control characters
                password += ch
                sys.stdout.write("*")
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)
    return password

BANNER = r"""
  *    .  .       *    .        .      *    .     .    .  *
.       .   .    .  *  .   .         .   .    .       .
   *  .    .   .          .    .   *      .       *       .

   ███████╗ █████╗ ████████╗██╗███╗   ██╗████████╗███████╗██╗
   ██╔════╝██╔══██╗╚══██╔══╝██║████╗  ██║╚══██╔══╝██╔════╝██║
   ███████╗███████║   ██║   ██║██╔██╗ ██║   ██║   █████╗  ██║
   ╚════██║██╔══██║   ██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║
   ███████║██║  ██║   ██║   ██║██║ ╚████║   ██║   ███████╗███████╗
   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝

.       .   .  *  .        .   .         .     *    .     .   .
  .  *     .      .     .    *    .    .          .    .
   *    .      .    .            .   *    .    .      *    .
"""

SATELLITE_ART = r"""
             *      .   *     .       *    .     .
        .        ___________      .         *
   *       .    |  _______  |          .        .    *
      .         | |       | |    .        .
           *    | | (O)(O)| |        *         .
    .           | |_______| |   .        .           *
         .      |___________|       .         .
              ___|_________|___             *
   *         /   ===========   \     .         .
        .   /  =================  \      *          .
   .       /________________________\        .
          |__________________________| .           *
    *     |__________________________| .    .
     .    .   .  .  .  .  .  .  .  .       *    .
"""

STARS = r"""
  .   *   .    .   *     .    .   .    *    .   .     *    .   .   *
      .       .      *      .      .     .      *    .      .      *
  *      .       .      .       *     .      .      .    *      .
"""

ENV_PATH = Path(__file__).parent / ".env"

def load_creds():
    return {
        "space_track_user": os.getenv("SPACE_TRACK_USERNAME", ""),
        "space_track_pass": os.getenv("SPACE_TRACK_PASSWORD", ""),
        "n2yo_key":         os.getenv("N2YO_API_KEY", ""),
    }

def save_creds(creds: dict):
    lines = [
        f'SPACE_TRACK_USERNAME={creds["space_track_user"]}',
        f'SPACE_TRACK_PASSWORD={creds["space_track_pass"]}',
        f'N2YO_API_KEY={creds["n2yo_key"]}',
    ]
    ENV_PATH.write_text("\n".join(lines) + "\n")
    load_dotenv(override=True)

def creds_ok(creds: dict) -> bool:
    return all(creds.values())

def setup_wizard():
    console.print()
    console.print(Rule("[bold white]FIRST-TIME SETUP[/bold white]", style="white"))
    console.print()
    console.print("[white]SATINTEL needs API keys to pull satellite data.[/white]")
    console.print()
    console.print("[white]Step 1 - Space-Track (free account)[/white]")
    console.print("[dim white]  -> https://www.space-track.org/auth/createAccount[/dim white]")
    console.print()
    console.print("[white]Step 2 - N2YO (free account + API key)[/white]")
    console.print("[dim white]  -> register at: https://www.n2yo.com/[/dim white]")
    console.print("[dim white]  -> get your key at: https://www.n2yo.com/login/edit/[/dim white]")
    console.print()

    creds = load_creds()
    if creds_ok(creds):
        console.print("[white]already got credentials saved[/white]")
        change = Prompt.ask("  change them?", choices=["y", "n"], default="n")
        if change == "n":
            return creds

    console.print()
    user = Prompt.ask("  [white]space-track email[/white]")
    pwd = masked_input("  space-track password: ")
    key  = Prompt.ask("  [white]n2yo api key[/white]")

    new_creds = {"space_track_user": user.strip(), "space_track_pass": pwd.strip(), "n2yo_key": key.strip()}
    save_creds(new_creds)
    console.print()
    console.print("[bold white]saved to .env[/bold white]")
    return new_creds

# space-track API calls
SPACETRACK_BASE = "https://www.space-track.org"

def spacetrack_login(user: str, pwd: str) -> requests.Session:
    session = requests.Session()
    resp = session.post(
        f"{SPACETRACK_BASE}/ajaxauth/login",
        data={"identity": user.strip(), "password": pwd.strip()},
        timeout=15,
    )
    resp.raise_for_status()
    # space-track returns {"Login": "Failed"} on bad credentials
    try:
        result = resp.json()
        if isinstance(result, dict) and str(result.get("Login", "")).lower() == "failed":
            raise ValueError("login failed - check your credentials")
    except ValueError:
        raise
    except Exception:
        pass
    # double-check with a real API call
    test = session.get(
        f"{SPACETRACK_BASE}/basicspacedata/query/class/satcat/limit/1/format/json",
        timeout=15,
    )
    if test.status_code != 200 or "login" in test.url.lower():
        raise ValueError("login failed - check your credentials")
    return session

def fetch_satellite_catalog(session: requests.Session, limit: int = 50):
    url = (
        f"{SPACETRACK_BASE}/basicspacedata/query/class/satcat"
        f"/CURRENT/Y/orderby/LAUNCH desc/limit/{limit}/format/json"
    )
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()

def fetch_tle_by_norad(session: requests.Session, norad_id: str):
    url = (
        f"{SPACETRACK_BASE}/basicspacedata/query/class/gp"
        f"/NORAD_CAT_ID/{norad_id}/orderby/EPOCH desc/limit/1/format/json"
    )
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None

# n2yo API calls
N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite"

def n2yo_get(endpoint: str, api_key: str):
    sep = "&" if "?" in endpoint else "?"
    url = f"{N2YO_BASE}/{endpoint}{sep}apiKey={api_key}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()

def fetch_position(norad_id: str, lat: float, lon: float, alt: float, api_key: str):
    return n2yo_get(f"positions/{norad_id}/{lat}/{lon}/{alt}/1", api_key)

def fetch_visual_passes(norad_id: str, lat: float, lon: float, alt: float,
                        days: int, min_vis: int, api_key: str):
    return n2yo_get(f"visualpasses/{norad_id}/{lat}/{lon}/{alt}/{days}/{min_vis}", api_key)

def fetch_radio_passes(norad_id: str, lat: float, lon: float, alt: float,
                       days: int, min_el: int, api_key: str):
    return n2yo_get(f"radiopasses/{norad_id}/{lat}/{lon}/{alt}/{days}/{min_el}", api_key)

def parse_tle(line1: str, line2: str) -> dict:
    try:
        return {
            "Satellite Number":    line1[2:7].strip(),
            "Classification":      line1[7],
            "Int'l Designator":    line1[9:17].strip(),
            "Epoch Year":          "20" + line1[18:20],
            "Epoch Day":           line1[20:32].strip(),
            "1st Derivative MM":   line1[33:43].strip(),
            "2nd Derivative MM":   line1[44:52].strip(),
            "BSTAR Drag Term":     line1[53:61].strip(),
            "Ephemeris Type":      line1[62],
            "Element Set No.":     line1[64:68].strip(),
            "Inclination (deg)":   line2[8:16].strip(),
            "RAAN (deg)":          line2[17:25].strip(),
            "Eccentricity":        "0." + line2[26:33].strip(),
            "Arg of Perigee (deg)": line2[34:42].strip(),
            "Mean Anomaly (deg)":  line2[43:51].strip(),
            "Mean Motion (rev/d)": line2[52:63].strip(),
            "Revolution No.":      line2[63:68].strip(),
            "Checksum L1":         line1[68],
            "Checksum L2":         line2[68],
        }
    except IndexError as e:
        raise ValueError(f"bad TLE format: {e}")

def display_tle_table(name: str, parsed: dict):
    table = Table(
        title=f"TLE Data - {name}",
        box=box.SIMPLE_HEAVY,
        border_style="white",
        header_style="bold white",
        title_style="bold bright_white",
        show_lines=True,
    )
    table.add_column("Parameter", style="white", min_width=22)
    table.add_column("Value", style="bright_white", min_width=20)
    for k, v in parsed.items():
        table.add_row(k, v)
    console.print(table)

def print_banner():
    console.clear()
    console.print(BANNER, style="bright_white")
    console.print("[dim white]  Satellite OSINT Intelligence Tool[/dim white]")
    console.print(STARS, style="dim white")

def section_header(title: str):
    console.print()
    console.print(Rule(f"[bold white]{title}[/bold white]", style="white"))
    console.print()

def ask_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    while True:
        raw = Prompt.ask(f"  [white]{prompt}[/white]")
        try:
            val = int(raw.strip())
            if min_val is not None and val < min_val:
                console.print(f"  [dim white]needs to be >= {min_val}[/dim white]")
                continue
            if max_val is not None and val > max_val:
                console.print(f"  [dim white]needs to be <= {max_val}[/dim white]")
                continue
            return val
        except ValueError:
            console.print("  [dim white]enter a whole number[/dim white]")

def ask_float(prompt: str) -> float:
    while True:
        raw = Prompt.ask(f"  [white]{prompt}[/white]")
        try:
            return float(raw.strip())
        except ValueError:
            console.print("  [dim white]enter a number (e.g. 3.14)[/dim white]")

def back_or_exit():
    console.print()
    console.print("  [dim white][B] back   [X] exit[/dim white]")
    choice = Prompt.ask("  [white]>[/white]").strip().upper()
    if choice == "X":
        farewell()

def farewell():
    console.print()
    console.print(SATELLITE_ART, style="dim white")
    console.print(Align.center("[bold bright_white]escaping orbit...[/bold bright_white]"))
    console.print()
    sys.exit(0)

def feature_orbital_elements(creds: dict):
    section_header("ORBITAL ELEMENT DATA")
    console.print(
        "  pulls TLE/orbital data from space-track.org\n",
        style="dim white",
    )
    console.print("  [white][1] browse recent satellites (top 20)[/white]")
    console.print("  [white][2] look up a specific NORAD ID[/white]")
    console.print("  [white][B] back[/white]")
    console.print()
    choice = Prompt.ask("  [white]>[/white]").strip().upper()

    if choice == "B":
        return
    if choice not in ("1", "2"):
        console.print("  [dim white]invalid[/dim white]")
        return

    with console.status("[white]connecting to space-track...[/white]", spinner="dots"):
        try:
            session = spacetrack_login(creds["space_track_user"], creds["space_track_pass"])
        except Exception as e:
            console.print(f"\n  [bold white]login failed:[/bold white] {e}")
            back_or_exit()
            return

    if choice == "1":
        with console.status("[white]fetching catalog...[/white]", spinner="dots"):
            try:
                sats = fetch_satellite_catalog(session, limit=20)
            except Exception as e:
                console.print(f"\n  [bold white]error:[/bold white] {e}")
                back_or_exit()
                return

        table = Table(
            title="recent satellites - space-track",
            box=box.SIMPLE_HEAVY,
            border_style="white",
            header_style="bold white",
            title_style="bold bright_white",
        )
        for col in ("NORAD ID", "Name", "Country", "Launch Date", "Object Type", "Status"):
            table.add_column(col, style="white" if col != "NORAD ID" else "bright_white")

        for s in sats:
            table.add_row(
                s.get("NORAD_CAT_ID", "-"),
                s.get("SATNAME", "-"),
                s.get("COUNTRY", "-"),
                s.get("LAUNCH", "-"),
                s.get("OBJECT_TYPE", "-"),
                "ACTIVE" if s.get("CURRENT") == "Y" else "DECAYED",
            )
        console.print()
        console.print(table)

    elif choice == "2":
        console.print("\n  [dim white]find NORAD IDs at celestrak.org[/dim white]\n")
        norad = Prompt.ask("  [white]NORAD ID (e.g. 25544 for ISS)[/white]").strip()
        with console.status("[white]fetching...[/white]", spinner="dots"):
            try:
                data = fetch_tle_by_norad(session, norad)
            except Exception as e:
                console.print(f"\n  [bold white]error:[/bold white] {e}")
                back_or_exit()
                return

        if not data:
            console.print(f"\n  [white]nothing found for NORAD ID {norad}[/white]")
            back_or_exit()
            return

        console.print()
        info_table = Table(box=box.SIMPLE_HEAVY, border_style="white",
                           header_style="bold white", show_header=False, show_lines=True)
        info_table.add_column("Field", style="dim white", min_width=28)
        info_table.add_column("Value", style="bright_white")

        fields = [
            ("Satellite Name",         data.get("OBJECT_NAME",    "-")),
            ("NORAD ID",               data.get("NORAD_CAT_ID",   "-")),
            ("Intl Designator",        data.get("INTLDES",        "-")),
            ("Object Type",            data.get("OBJECT_TYPE",    "-")),
            ("Epoch",                  data.get("EPOCH",          "-")),
            ("Inclination (deg)",      data.get("INCLINATION",    "-")),
            ("Eccentricity",           data.get("ECCENTRICITY",   "-")),
            ("Apogee (km)",            data.get("APOGEE",         "-")),
            ("Perigee (km)",           data.get("PERIGEE",        "-")),
            ("Orbital Period (min)",   data.get("PERIOD",         "-")),
            ("Mean Motion (rev/day)",  data.get("MEAN_MOTION",    "-")),
            ("Revolutions at Epoch",   data.get("REV_AT_EPOCH",   "-")),
            ("Country of Origin",      data.get("COUNTRY_CODE",   "-")),
            ("Launch Date",            data.get("LAUNCH_DATE",    "-")),
            ("Decay Date",             data.get("DECAY_DATE") or "still orbiting"),
            ("RCS Size",               data.get("RCS_SIZE",       "-")),
        ]
        for field, val in fields:
            info_table.add_row(field, str(val))

        console.print(
            Panel(
                info_table,
                title=f"[bold bright_white]{data.get('OBJECT_NAME', norad)}[/bold bright_white]",
                border_style="white",
            )
        )

        tle1 = data.get("TLE_LINE1", "")
        tle2 = data.get("TLE_LINE2", "")
        if tle1 and tle2:
            console.print()
            console.print("  [dim white]TLE:[/dim white]")
            console.print(f"  [white]{tle1}[/white]")
            console.print(f"  [white]{tle2}[/white]")

    back_or_exit()

def feature_satellite_position(creds: dict):
    section_header("SATELLITE POSITION")
    console.print(
        "  real-time position of any satellite right now\n",
        style="dim white",
    )
    console.print("  [dim white]tip: get your lat/lon at latlong.net[/dim white]\n")

    norad = Prompt.ask("  [white]NORAD ID (e.g. 25544 for ISS)[/white]").strip()
    lat   = ask_float("your latitude  (e.g. 3.1390)")
    lon   = ask_float("your longitude (e.g. 101.6869)")
    alt   = ask_float("your altitude in metres (e.g. 50)")

    with console.status("[white]querying n2yo...[/white]", spinner="dots"):
        try:
            data = fetch_position(norad, lat, lon, alt / 1000.0, creds["n2yo_key"])
        except Exception as e:
            console.print(f"\n  [bold white]error:[/bold white] {e}")
            back_or_exit()
            return

    info = data.get("info", {})
    pos  = (data.get("positions") or [{}])[0]

    console.print()
    table = Table(
        title=f"live position - {info.get('satname', norad)}",
        box=box.SIMPLE_HEAVY,
        border_style="white",
        header_style="bold white",
        title_style="bold bright_white",
        show_header=False,
        show_lines=True,
    )
    table.add_column("Parameter", style="dim white", min_width=28)
    table.add_column("Value", style="bright_white")

    from datetime import datetime, timezone
    ts = pos.get("timestamp", 0)
    utc_time = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if ts else "-"

    table.add_row("Satellite Name",      info.get("satname",           "-"))
    table.add_row("NORAD ID",            str(info.get("satid",         "-")))
    table.add_row("Transactions Used",   str(info.get("transactionscount", "-")))
    table.add_row("Latitude (deg)",      str(pos.get("satlatitude",    "-")))
    table.add_row("Longitude (deg)",     str(pos.get("satlongitude",   "-")))
    table.add_row("Altitude (km)",       str(pos.get("sataltitude",    "-")))
    table.add_row("Azimuth (deg)",       str(pos.get("azimuth",        "-")))
    table.add_row("Elevation (deg)",     str(pos.get("elevation",      "-")))
    table.add_row("Right Ascension",     str(pos.get("ra",             "-")))
    table.add_row("Declination",         str(pos.get("dec",            "-")))
    table.add_row("Time (UTC)",          utc_time)

    el = pos.get("elevation", 0)
    vis = "VISIBLE above horizon" if el and el > 0 else "not visible right now"
    table.add_row("Visibility", vis)

    console.print(table)
    back_or_exit()

def feature_orbital_predictions(creds: dict):
    section_header("ORBITAL PASS PREDICTIONS")
    console.print(
        "  when will it fly over you?\n"
        "  visual = see it with your eyes at night\n"
        "  radio  = good windows for radio contact\n",
        style="dim white",
    )
    console.print("  [white][1] visual passes[/white]")
    console.print("  [white][2] radio passes[/white]")
    console.print("  [white][B] back[/white]")
    console.print()
    choice = Prompt.ask("  [white]>[/white]").strip().upper()

    if choice == "B":
        return
    if choice not in ("1", "2"):
        console.print("  [dim white]invalid[/dim white]")
        return

    console.print("\n  [dim white]ISS = 25544  |  Hubble = 20580  |  find more at celestrak.org[/dim white]\n")

    norad = Prompt.ask("  [white]NORAD ID[/white]").strip()
    lat   = ask_float("your latitude  (e.g. 3.1390)")
    lon   = ask_float("your longitude (e.g. 101.6869)")
    alt   = ask_float("your altitude in metres (e.g. 50)")
    days  = ask_int("how many days ahead? (1-10)", min_val=1, max_val=10)

    from datetime import datetime, timezone

    if choice == "1":
        min_vis = ask_int("minimum seconds visible per pass? (e.g. 300)", min_val=0)
        with console.status("[white]calculating...[/white]", spinner="dots"):
            try:
                data = fetch_visual_passes(norad, lat, lon, alt / 1000.0,
                                           days, min_vis, creds["n2yo_key"])
            except Exception as e:
                console.print(f"\n  [bold white]error:[/bold white] {e}")
                back_or_exit()
                return

        info   = data.get("info", {})
        passes = data.get("passes") or []

        console.print()
        if not passes:
            console.print(f"  [white]no passes found for the next {days} day(s)[/white]")
            back_or_exit()
            return

        table = Table(
            title=f"visual passes - {info.get('satname', norad)} ({len(passes)} found)",
            box=box.SIMPLE_HEAVY,
            border_style="white",
            header_style="bold white",
            title_style="bold bright_white",
        )
        for col in ("Start UTC", "Max UTC", "End UTC", "Max El (deg)",
                    "Start Az", "End Az", "Mag", "Duration (s)"):
            table.add_column(col, style="white")

        for p in passes:
            start_utc = datetime.fromtimestamp(
                p.get("startUTC", 0), tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            max_utc = datetime.fromtimestamp(
                p.get("maxUTC", 0), tz=timezone.utc
            ).strftime("%H:%M:%S")
            end_utc = datetime.fromtimestamp(
                p.get("endUTC", 0), tz=timezone.utc
            ).strftime("%H:%M:%S")
            table.add_row(
                start_utc,
                max_utc,
                end_utc,
                str(p.get("maxEl",    "-")),
                str(p.get("startAz",  "-")),
                str(p.get("endAz",    "-")),
                str(p.get("mag",      "-")),
                str(p.get("duration", "-")),
            )
        console.print(table)

    elif choice == "2":
        min_el = ask_int("minimum elevation angle in degrees? (e.g. 40)", min_val=0)
        with console.status("[white]calculating...[/white]", spinner="dots"):
            try:
                data = fetch_radio_passes(norad, lat, lon, alt / 1000.0,
                                          days, min_el, creds["n2yo_key"])
            except Exception as e:
                console.print(f"\n  [bold white]error:[/bold white] {e}")
                back_or_exit()
                return

        info   = data.get("info", {})
        passes = data.get("passes") or []

        console.print()
        if not passes:
            console.print(f"  [white]no radio passes found for the next {days} day(s)[/white]")
            back_or_exit()
            return

        table = Table(
            title=f"radio passes - {info.get('satname', norad)} ({len(passes)} found)",
            box=box.SIMPLE_HEAVY,
            border_style="white",
            header_style="bold white",
            title_style="bold bright_white",
        )
        for col in ("AOS UTC", "LOS UTC", "Max El (deg)", "AOS Az", "LOS Az", "Duration (s)"):
            table.add_column(col, style="white")

        for p in passes:
            aos_utc = datetime.fromtimestamp(
                p.get("startAOS", 0), tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            los_utc = datetime.fromtimestamp(
                p.get("startLOS", 0), tz=timezone.utc
            ).strftime("%H:%M:%S")
            table.add_row(
                aos_utc,
                los_utc,
                str(p.get("maxEl",    "-")),
                str(p.get("startAz",  "-")),
                str(p.get("endAz",    "-")),
                str(p.get("duration", "-")),
            )
        console.print(table)

    back_or_exit()

def feature_tle_parser():
    section_header("TLE PARSER")
    console.print(
        "  paste or load TLE data and it'll decode everything\n",
        style="dim white",
    )
    console.print("  [white][1] paste TLE lines[/white]")
    console.print("  [white][2] load from .txt file[/white]")
    console.print("  [white][B] back[/white]")
    console.print()
    choice = Prompt.ask("  [white]>[/white]").strip().upper()

    if choice == "B":
        return

    if choice == "1":
        console.print(
            "\n  [dim white]format: Name (optional) / Line 1 / Line 2[/dim white]\n"
        )
        name  = Prompt.ask("  [white]satellite name (optional)[/white]", default="UNKNOWN")
        line1 = Prompt.ask("  [white]line 1[/white]").strip()
        line2 = Prompt.ask("  [white]line 2[/white]").strip()

        try:
            parsed = parse_tle(line1, line2)
            console.print()
            display_tle_table(name, parsed)
        except ValueError as e:
            console.print(f"\n  [bold white]parse error:[/bold white] {e}")

    elif choice == "2":
        console.print("\n  [dim white]expects 3 lines per entry: Name / Line1 / Line2[/dim white]\n")
        filepath = Prompt.ask("  [white]path to file[/white]").strip()
        path = Path(filepath).expanduser()
        if not path.exists():
            console.print(f"\n  [white]file not found: {path}[/white]")
            back_or_exit()
            return

        lines = path.read_text().strip().splitlines()
        entries = []
        i = 0
        while i < len(lines):
            l = lines[i].strip()
            if l.startswith("1 "):
                entries.append(("UNKNOWN", l, lines[i + 1].strip() if i + 1 < len(lines) else ""))
                i += 2
            elif not l.startswith("2 ") and i + 2 < len(lines):
                entries.append((l, lines[i + 1].strip(), lines[i + 2].strip()))
                i += 3
            else:
                i += 1

        if not entries:
            console.print("\n  [white]no TLE entries found[/white]")
            back_or_exit()
            return

        console.print(f"\n  [white]found {len(entries)} TLE set(s)[/white]\n")
        for name, line1, line2 in entries:
            try:
                parsed = parse_tle(line1, line2)
                display_tle_table(name, parsed)
                console.print()
            except ValueError as e:
                console.print(f"  [dim white]skipping {name}: {e}[/dim white]")
    else:
        console.print("  [dim white]invalid[/dim white]")

    back_or_exit()

MENU = r"""
  +---------------------------------------------------------+
  |                      SATINTEL                           |
  |                                                         |
  |  [1]  orbital element data  - TLE & catalog lookup      |
  |  [2]  satellite position    - real-time lat/lon/alt     |
  |  [3]  pass predictions      - when will it fly over?    |
  |  [4]  TLE parser            - decode TLE strings/files  |
  |                                                         |
  |  [S]  setup / change API keys                           |
  |  [0]  exit                                              |
  +---------------------------------------------------------+
"""

def main():
    print_banner()

    creds = load_creds()
    if not creds_ok(creds):
        console.print("\n  [white]no credentials found, running setup...[/white]")
        creds = setup_wizard()

    while True:
        console.print(MENU, style="bright_white")
        choice = Prompt.ask("  [white]>[/white]").strip().upper()

        if choice == "0":
            farewell()
        elif choice == "1":
            if not creds.get("space_track_user"):
                console.print("\n  [white]need space-track credentials first[/white]")
                creds = setup_wizard()
            else:
                feature_orbital_elements(creds)
        elif choice == "2":
            if not creds.get("n2yo_key"):
                console.print("\n  [white]need n2yo API key first[/white]")
                creds = setup_wizard()
            else:
                feature_satellite_position(creds)
        elif choice == "3":
            if not creds.get("n2yo_key"):
                console.print("\n  [white]need n2yo API key first[/white]")
                creds = setup_wizard()
            else:
                feature_orbital_predictions(creds)
        elif choice == "4":
            feature_tle_parser()
        elif choice == "S":
            creds = setup_wizard()
            load_dotenv(override=True)
            creds = load_creds()
        else:
            console.print("  [dim white]enter 0-4 or S[/dim white]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n  [dim white]interrupted. escaping orbit...[/dim white]\n")
        sys.exit(0)
