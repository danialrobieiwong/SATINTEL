# SATINTEL

**Satellite OSINT Intelligence Tool** — track any satellite from your terminal.

No coding experience needed. Just run two commands and you're in.

![Banner](assets/banner_menu.svg)

---

## What it does

| Feature | Description |
|---|---|
| **Orbital Elements** | Look up any satellite's TLE data and orbital stats from Space-Track |
| **Live Position** | See a satellite's real-time latitude, longitude, altitude and visibility |
| **Pass Predictions** | Find out exactly when a satellite will fly over your location |
| **TLE Parser** | Decode raw TLE strings or files into plain readable data |

---

## Screenshots

### Setup Wizard
First time? SATINTEL walks you through getting your free API keys step-by-step.

![Setup](assets/setup_wizard.svg)

### Orbital Element Data
Look up any satellite by NORAD ID and see its full orbital profile.

![Orbital Elements](assets/orbital_elements.svg)

### Live Satellite Position
Real-time position, altitude, azimuth and visibility from your location.

![Live Position](assets/live_position.svg)

### Pass Predictions
Know exactly when to look up — date, time, max elevation, direction.

![Pass Predictions](assets/pass_predictions.svg)

### TLE Parser
Paste or load TLE data and get every orbital parameter decoded.

![TLE Parser](assets/tle_parser.svg)

---

## Requirements

- **Python 3.8 or newer** — [Download here](https://www.python.org/downloads/)
- A free [Space-Track](https://www.space-track.org/auth/createAccount) account
- A free [N2YO](https://www.n2yo.com/login/register.php) account + API key

Everything else installs automatically.

---

## Install & Run

**Step 1 — Clone the repo**
```bash
git clone https://github.com/danialrobieiwong/SATINTEL
cd SATINTEL
```

**Step 2 — Run setup (first time only)**
```bash
./setup.sh
```

**Step 3 — Launch**
```bash
./run.sh
```

On first launch, SATINTEL will ask for your API keys and save them. You won't need to enter them again.

---

## Getting your API keys

### Space-Track (free)
1. Register at [space-track.org/auth/createAccount](https://www.space-track.org/auth/createAccount)
2. Your username is your email and the password you set

### N2YO (free)
1. Register at [n2yo.com/login/register.php](https://www.n2yo.com/login/register.php)
2. After logging in, go to [n2yo.com/login](https://www.n2yo.com/login/) to find your API key

---

## Useful NORAD IDs to try

| Satellite | NORAD ID |
|---|---|
| International Space Station | 25544 |
| Hubble Space Telescope | 20580 |
| James Webb Space Telescope | 50463 |
| Tiangong Space Station | 48274 |

Find more at [celestrak.org](https://celestrak.org/SOCRATES/)

---

## Troubleshooting

**`python3: command not found`**
Install Python from [python.org/downloads](https://www.python.org/downloads/)

**`Permission denied: ./setup.sh`**
```bash
chmod +x setup.sh run.sh
./setup.sh
```

**Space-Track login failed**
Double-check your email and password at [space-track.org](https://www.space-track.org)

**N2YO returns no data**
Make sure your API key is correct — find it on your N2YO account page after logging in

---

## Use Cases

### 🔭 Stargazing & Satellite Spotting
Use pass predictions to know exactly when the ISS or a Starlink train will streak across your sky. Set minimum visibility to 300+ seconds to only get the good long passes. Head outside 2 minutes early and look in the direction of the Start Azimuth.

### 📡 Amateur Radio (Ham Radio)
Radio operators use SATINTEL to plan communication windows with amateur radio satellites like SO-50, AO-91, and the ISS's APRS system. Run a radio pass prediction with your grid coordinates and minimum elevation set to 10–15° for reliable contact windows.

### 🛰️ Satellite OSINT & Research
Track military, government, and commercial satellites by NORAD ID. Cross-reference orbital elements (inclination, apogee, perigee) to infer a satellite's mission profile and coverage area. Space-Track has the full catalog — over 20,000 objects.

### 📰 Journalism & Verification
Verify claims about satellite imagery or surveillance by checking whether a particular satellite was actually overhead at a specific time and place. Look up the orbital period and pass predictions to build a precise timeline.

### 🏫 Education & Classroom
A hands-on way to teach orbital mechanics. Look up a satellite's TLE, run it through the parser, and walk through what each parameter means — inclination, eccentricity, mean motion. Real data, no textbook needed.

### 🔐 Security Research
Identify reconnaissance satellites in low Earth orbit passing over sensitive locations. Cross-reference pass timing with known observation windows for threat modelling and physical security planning.

---

## Getting the most out of SATINTEL

**Use precise coordinates**
The more accurate your latitude, longitude, and altitude, the more accurate your pass predictions. Use [latlong.net](https://www.latlong.net) or your phone's GPS app to get exact values.

**Set a realistic minimum elevation**
For visual passes, set minimum elevation to **30°+** — passes below that are often blocked by buildings and trees. For radio, **10°** is usually workable with a directional antenna.

**Check multiple days ahead**
Satellites repeat similar passes roughly every few days. Run predictions for 5–7 days to find a pass with a high maximum elevation (60°+ is excellent) — those are the brightest and longest.

**Use the TLE Parser to understand orbits**
Paste any TLE from [Celestrak](https://celestrak.org) into the parser. An eccentricity near 0 means a circular orbit (e.g. ISS). A high inclination (>80°) means the satellite passes over the poles and can cover the whole Earth. Apogee/perigee difference tells you how elliptical the orbit is.

**Look up new satellites quickly**
New launches get NORAD IDs assigned within days. Check [Celestrak's latest launches](https://celestrak.org/SOCRATES/) and paste the ID straight into SATINTEL to track them before tracking tools update.

**Save your .env file**
Your credentials are stored in `.env` in the SATINTEL folder. Back it up — if you delete the folder you'll need to re-enter them.

**Night passes are brightest**
For visual spotting, the best passes are 30–90 minutes after sunset or before sunrise. The sky is dark but the satellite is still in sunlight, making it visible to the naked eye.
