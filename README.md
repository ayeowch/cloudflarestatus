# Cloudflarestatus
Python package to parse Cloudflare System Status from https://www.cloudflarestatus.com

## Quickstart

### Install

```
$ pip install cloudflarestatus
```

### Command-line usage 1

Get status for a data center:

```
$ cloudflarestatus -d hba
{"HBA": {"code": "HBA", "name": "Hobart, Australia", "status": "partial_outage", "timestamp": 1682596723}}
```

### Command-line usage 2

Pipe to `jq` (a separate program) to format the JSON output:

```
$ cloudflarestatus -d hba syd | jq
{
  "HBA": {
    "code": "HBA",
    "name": "Hobart, Australia",
    "status": "partial_outage",
    "timestamp": 1682596723
  },
  "SYD": {
    "code": "SYD",
    "name": "Sydney, NSW, Australia",
    "status": "operational",
    "timestamp": 1682596723
  }
}
```

### Python usage 1

Get status for all data centers.

```
>>> import cloudflarestatus
>>> cloudflarestatus.dc()
{'ACC': {'code': 'ACC', 'name': 'Accra, Ghana', 'status': 'operational', 'timestamp': 1682596723},
..
'ZRH': {'code': 'ZRH', 'name': 'Zürich, Switzerland', 'status': 'operational', 'timestamp': 1682596723}
```

### Python usage 2

Get status for a data center:

```
>>> import cloudflarestatus
>>> cloudflarestatus.dc('HBA')
{'HBA': {'code': 'HBA', 'name': 'Hobart, Australia', 'status': 'partial_outage', 'timestamp': 1682596723}}
```

### Note

- Internally, `cloudflarestatus` caches response from https://www.cloudflarestatus.com for up to 60 seconds.
- Input for data center code is case-insensitive.

## Package development

### Setup

```
~/.pyenv/versions/3.11.2/bin/python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Test

```
./test.sh
```

### Format

```
./format.sh
```

### Build

```
./build.sh
```
