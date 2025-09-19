
Fitness Tools - Full pack
Includes:
- Protein calculator (exhaustive Indian food DB)
- BMI, Sleep, Sugar calculators
- HTML forms + JSON API endpoints (/api/*) for programmatic use
How to run:
- python -m venv venv
- source venv/bin/activate  (Windows: venv\Scripts\activate)
- pip install -r requirements.txt
- python app.py
APIs:
POST /api/protein  JSON body: { "food": "Paneer (100g)", "qty": 200 }
POST /api/macros   JSON body: { "weight": 70, "goal": "loss", "activity": "moderate" }
POST /api/sleep    JSON body: { "avg": 6.5 }
POST /api/sugar    JSON body: { "sugar": 40 }
