<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:120d1c,100:c2531f&height=170&section=header&text=jr-projects&fontColor=ffe7c2&fontSize=42&fontAlignY=40&desc=%F0%9F%8F%8D%EF%B8%8F+the+garage+%C2%B7+python+projects+built+while+learning&descAlignY=62&descSize=14" width="100%" alt="jr-projects" />

  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=18&pause=1200&color=FF8A3D&center=true&vCenter=true&width=560&lines=Built+one+commit+at+a+time;Dark+theme.+Warm+lamp.+Clean+code.;Every+project+starts+with+a+small+script" alt="Typing intro" />

  <br/>

  <img src="https://img.shields.io/github/languages/top/JM-jr-prog/jr-projects?color=D35400&labelColor=0d0b10&style=flat-square" alt="language" />
  <img src="https://img.shields.io/github/last-commit/JM-jr-prog/jr-projects?color=B34700&labelColor=0d0b10&style=flat-square" alt="last commit" />
  <img src="https://img.shields.io/github/stars/JM-jr-prog/jr-projects?color=7a2f10&labelColor=0d0b10&style=flat-square" alt="stars" />
</div>

<br/>

## `> boot --garage`

```text
$ ignite --engine
[  ok  ] loading projects ........ 2 found
[  ok  ] language ................ Python 3.x
[  ok  ] mode .................... night ride
[ ready ] pick a project and ride on
```

A collection of the projects I built while learning software development.
Each project lives in its own folder with a README that explains what it does and how to run it.

<br/>

## `> ls ./garage/Python`

| 🏍️ Project | ⚙️ What it does | 🔧 Stack |
|---|---|---|
| [**EcoByte-Tracker**](Python/EcoByte-Tracker) | Audits local files, estimates the carbon cost of digital storage, and logs clean-up sessions over time | `Python` `os` `JSON` |
| [**MediVault**](Python/MediVault) | Logs medication prescriptions and flags potential drug interactions using a conflict registry | `Python` `GUI` `JSON` |

> ⚠️ MediVault is a learning project and not a substitute for medical advice. Always check medications with a doctor or pharmacist.

<br/>

## `> spec sheet`

### 🌱 EcoByte: Digital Carbon Tracker

```text
engine    : Python + os module
storage   : JSON (settings and clean-up sessions)
output    : terminal visualizations + optimization tips
purpose   : estimate the hidden carbon cost of digital storage
```

- Walks through directories and inspects file metadata
- Saves configurations and clean-up sessions in a JSON storage layer
- Calculates carbon footprint estimates from storage data

### 💊 MediVault: Medication Conflict Registry

```text
engine    : Python (core logic) + GUI
storage   : JSON medication vault
safety    : input validation + interaction registry
purpose   : flag potential adverse drug interactions
```

- Compares active medications against an interaction database
- Validates input so details are recorded correctly
- Keeps core logic and interface in separate modules (`medivault_core.py` and `medivault_gui.py`)

<br/>

## `> start the engine`

You need Python 3.x installed.

```bash
# clone the repo
git clone https://github.com/JM-jr-prog/jr-projects.git
cd jr-projects/Python

# run EcoByte-Tracker
cd EcoByte-Tracker
python main.py

# run MediVault (from the Python folder)
cd ../MediVault
python run_gui.py
```

<br/>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:120d1c,100:c2531f&height=90&section=footer" width="100%" alt="footer" />
</div>
