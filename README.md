
# CanvasPulse

Terminal tool that lists **upcoming** and **recently overdue** Canvas assignments in the console.

## Features

* Uses a Canvas Personal Access Token
* Sections: Overdue (last 7 days) and Upcoming
* Skips submitted and blacklisted assignment IDs
* Color‑coded due dates
* Follows API pagination

## Project Layout

```
.
├── api_client.py
├── canvas_service.py
├── config.py
├── main.py
├── models.py
├── presenter.py
├── printify.sh
├── README.md
└── requirements.txt
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv/Scripts/activate
pip install -r requirements.txt
```

## Configure

Create `.env` in the project root:

```dotenv
CANVAS_TOKEN=your_canvas_token
```

Edit `config.py` if needed:

```python
CANVAS_BASE_URL = "https://reykjavik.instructure.com/"
COURSE_IDS = [9424, 9425, 9411, 9419]
AVOID_ASSIGNMENT_IDS = [98301, 96732, 98019]
OVERDUE_WINDOW_DAYS = 7
```

## Run

```bash
python main.py
```

## Notes

* Only course IDs in `COURSE_IDS` are fetched.
* Submitted states hidden: `submitted`, `graded`, `pending_review`, or `submitted_at` present.
* Timestamps parsed as UTC.

## Troubleshooting

* 401/403: token invalid or expired.
* No/missing results: check `COURSE_IDS` and token scope.
* Wrong host: set `CANVAS_BASE_URL` to your institution (url that you use to access canvas).
