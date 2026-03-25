# LED Controller

A Python application for controlling **Magnimage FW16-C LED Video Controllers** over UDP on a local network.

Supports CLI operation (Phase 1) and a REST API with web frontend (Phase 2).

---

## Project Structure

```
LED_Controller/
├── api/
│   ├── app.py                  # FastAPI application factory
│   ├── schemas.py              # Pydantic request/response models
│   └── routers/
│       └── brightness.py       # API endpoints
├── config/
│   └── ip_groups.py            # IP registry and group resolver
├── services/
│   └── brightness_service.py   # Business logic
├── utils/
│   ├── command_utils.py        # UDP command frame builder
│   ├── network_utils.py        # UDP socket transport
│   └── logger.py               # Logger factory
├── constants.py                # All configuration constants
├── main.py                     # CLI entry point
├── server.py                   # API server entry point
└── requirements.txt
```

---

## Device Groups

Controllers are organised into named groups. Both `main` and `backup` IPs are targeted per group (Example below).

| Group | Description         | Main IPs                              | Backup IPs                            |
|-------|---------------------|---------------------------------------|---------------------------------------|
| `m`   | Main panels         | 10.0.0.101, 10.0.0.103, 10.0.0.105   | 10.0.0.102, 10.0.0.104, 10.0.0.106   |
| `ac`  | AC unit panel       | 10.0.0.107                            | 10.0.0.108                            |
| `b`   | B panel             | 10.0.0.109                            | 10.0.0.110                            |
| `e`   | E panel             | 10.0.0.111                            | 10.0.0.112                            |
| `ctrl`| Controller (local)  | 127.0.0.1                             | —                                     |

---

## Installation

**Requirements:** Python 3.11+

```bash
# Clone the repo
git clone https://github.com/LimWaiLeongJeremy/LED_Controller.git
cd LED_Controller

# Install dependencies
pip install -r requirements.txt
```

---

## Phase 1 — CLI Usage

```bash
python main.py <start_brightness> <end_brightness> <step> <duration> [--groups GROUP ...]
```

### Arguments

| Argument            | Type  | Description                                          |
|---------------------|-------|------------------------------------------------------|
| `start_brightness`  | int   | Starting brightness percentage (0–100)               |
| `end_brightness`    | int   | Ending brightness percentage (0–100)                 |
| `step`              | int   | Brightness increment per step (must be > 0)          |
| `duration`          | float | Delay between steps in seconds (must be >= 0)        |
| `--groups`          | list  | Groups to target (default: all groups)               |

### Examples

```bash
# Ramp all groups from 0% to 100% in steps of 5, 0.5s between each step
python main.py 0 100 5 0.5

# Dim only main and AC panels from 100% to 0%
python main.py 100 0 10 1.0 --groups m ac

# Set all groups to 75% instantly (step=1, duration=0)
python main.py 75 75 1 0
```

---

## Phase 2 — API Server

```bash
python server.py
```

The server starts on `http://0.0.0.0:8000`.

| URL                          | Description                        |
|------------------------------|------------------------------------|
| `http://localhost:8000/docs` | Interactive Swagger UI             |
| `http://localhost:8000/redoc`| ReDoc API documentation            |
| `http://localhost:8000/health`| Health check                      |

### Endpoints

#### `POST /brightness/absolute`
Set one device to an absolute brightness level instantly.

```json
{
  "ip": "10.0.0.101",
  "brightness": 75
}
```

#### `POST /brightness/ramp/device`
Ramp brightness on a single device.

```json
{
  "ip": "10.0.0.101",
  "start_brightness": 0,
  "end_brightness": 100,
  "step": 5,
  "interval_seconds": 0.5
}
```

#### `POST /brightness/ramp/groups`
Ramp brightness across one or more device groups concurrently.

```json
{
  "groups": ["m", "ac"],
  "start_brightness": 100,
  "end_brightness": 0,
  "step": 10,
  "interval_seconds": 1.0
}
```

---

## Logging

Logs are written to `brightness_commands.log` in the project root.
Log files are excluded from version control via `.gitignore`.

---

## Roadmap

| Phase | Status      | Description                                      |
|-------|-------------|--------------------------------------------------|
| 1     | ✅ Complete  | CLI tool — UDP brightness control                |
| 2     | 🔄 In progress | FastAPI backend + React frontend              |
| 3     | 🔜 Planned   | Docker + Cloudflare Tunnel for remote access     |