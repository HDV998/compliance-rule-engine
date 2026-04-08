# Compliance Rule Engine API

A FastAPI backend for defining and evaluating nested logical rules against arbitrary transaction data. Rules are stored in SQLite and evaluated dynamically at runtime — no hardcoding required.

---

## What it does

You define a rule once via the API (e.g. "country is India AND amount > 10000"), save it, and then evaluate any transaction payload against it using the rule's ID. The evaluation engine handles arbitrarily deep nesting of AND, OR, and NOT conditions recursively.

Practical use cases this kind of system maps to: fraud detection pipelines, compliance checks, feature flag logic, policy engines.

---

## Tech stack

- **FastAPI** — REST API layer
- **Pydantic** — request/response validation
- **SQLAlchemy** — ORM
- **SQLite** — persistent rule storage (swappable for Postgres)

---

## Project structure

```
.
├── main.py           # route definitions and app entry point
├── models.py         # SQLAlchemy models
├── database.py       # DB session and connection setup
├── testing.py        # recursive rule evaluation logic
├── requirements.txt
└── rules.db          # auto-generated, not committed to git
```

---

## Running locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger UI available at `http://127.0.0.1:8000/docs` once the server is up.

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rules` | Create a new rule |
| `GET` | `/rules` | Fetch all saved rules |
| `POST` | `/evaluate/{rule_id}` | Evaluate a payload against a rule |
| `PUT` | `/rules/{rule_id}` | Update an existing rule |
| `DELETE` | `/rules/{rule_id}` | Delete a rule |

---

## Example usage

**Creating a rule** — `POST /rules`

```json
{
  "name": "india high amount",
  "rules": {
    "kind": "group",
    "type": "AND",
    "rules": [
      {
        "kind": "rule",
        "field": "country",
        "operator": "==",
        "value": "India"
      },
      {
        "kind": "rule",
        "field": "amount",
        "operator": ">",
        "value": 10000
      }
    ]
  }
}
```

**Evaluating a transaction** — `POST /evaluate/1`

```json
{
  "amount": 12000,
  "country": "India"
}
```

**Response**

```json
{
  "rule_id": 1,
  "result": true
}
```

---

## Supported operators

| Operator | Meaning |
|----------|---------|
| `==` | equals |
| `!=` | not equals |
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal |
| `<=` | less than or equal |

Logical groupings support `AND`, `OR`, and `NOT` and can be nested to any depth.

---

## Planned improvements

- PostgreSQL support for production deployments
- Additional operators: `IN`, `NOT IN`, regex matching
- Rule versioning — keep history of edits
- Auth layer (API key or JWT)
- A basic frontend for building rules without touching the API directly

---

## Notes

- `rules.db` is auto-created on first run and should be added to `.gitignore`
- The evaluation engine in `testing.py` is fully recursive — nested groups of any depth work without any changes to the evaluator
- Swagger UI at `/docs` covers all endpoints with live testing built in