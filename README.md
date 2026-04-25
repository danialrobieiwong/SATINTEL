# SATINTEL

track satellites from your terminal. real-time positions, pass predictions, orbital data — all from free APIs.

no coding experience needed.

![Banner](assets/banner_menu.svg)

---

## what it does

| | |
|---|---|
| **orbital element data** | look up any satellite's TLE and orbital stats from space-track.org |
| **live position** | real-time lat/lon/altitude and whether it's visible from where you are |
| **pass predictions** | find out exactly when a satellite will fly over your location |
| **TLE parser** | paste or load TLE data and get every parameter decoded |

---

## screenshots

### first-time setup
walks you through getting API keys, saves them so you never have to enter them again

![Setup](assets/setup_wizard.svg)

### orbital data
look up any satellite by NORAD ID

![Orbital Elements](assets/orbital_elements.svg)

### live position
where is it right now

![Live Position](assets/live_position.svg)

### pass predictions
know when to look up

![Pass Predictions](assets/pass_predictions.svg)

### TLE parser

![TLE Parser](assets/tle_parser.svg)

---

## requirements

- python 3.8+ — [python.org/downloads](https://www.python.org/downloads/)
- free [space-track.org](https://www.space-track.org/auth/createAccount) account
- free [n2yo.com](https://www.n2yo.com/) account + API key

everything else installs itself on first run.

---

## how to run it

```bash
git clone https://github.com/danialrobieiwong/SATINTEL
cd SATINTEL
./setup.sh
./run.sh
```

first launch will ask for your API keys and save them to a `.env` file. after that just run `./run.sh`.

---

## getting your API keys

**space-track** — register at [space-track.org/auth/createAccount](https://www.space-track.org/auth/createAccount), your login is just the email and password you sign up with

**n2yo** — register at [n2yo.com](https://www.n2yo.com/), then find your API key on [this page](https://www.n2yo.com/login/edit/) after logging in

---

## useful NORAD IDs

| satellite | ID |
|---|---|
| ISS | 25544 |
| Hubble | 20580 |
| James Webb | 50463 |
| Tiangong | 48274 |

more at [celestrak.org](https://celestrak.org/SOCRATES/)

---

## troubleshooting

**python3 not found** — install from [python.org](https://www.python.org/downloads/)

**permission denied on setup.sh**
```bash
chmod +x setup.sh run.sh
```

**space-track login fails** — double check your email/password at space-track.org

**n2yo returns nothing** — make sure your API key is correct, find it on your n2yo account page

---

## use cases

**spotting satellites with your eyes** — use pass predictions for the ISS or Starlink, set minimum visibility to 300s+ to filter out short passes. go outside 2 mins early and face the direction shown under "start azimuth". best time is 30-90 mins after sunset when the sky is dark but the satellite is still lit up.

**amateur radio** — if you're into ham radio, use the radio pass predictions to plan contact windows with satellites like SO-50 or AO-91. set minimum elevation to around 10-15 degrees.

**OSINT / research** — space-track has the full catalog, over 20,000 objects. you can look up military, government and commercial satellites by NORAD ID and cross-reference their orbital elements to figure out what they're probably doing. high inclination means polar orbit, roughly circular apogee/perigee means it's not doing anything sneaky with its altitude.

**journalism** — verifying whether a satellite was overhead at a specific time and place. pull the orbital period, run a pass prediction around the date in question.

**learning orbital mechanics** — TLE parser is good for this. grab a TLE from celestrak, paste it in, and you get all 19 parameters decoded. eccentricity near 0 = circular orbit. inclination over 80 = polar. the rest you can look up.

---

## tips

- use your actual GPS coordinates, not a rough approximation — it makes a noticeable difference in pass accuracy
- for visual spotting, passes with max elevation above 40-50 degrees are the ones worth going outside for
- new launches get NORAD IDs within a few days, you can track them on celestrak before most apps catch up
- back up your `.env` file if you ever plan to reinstall
