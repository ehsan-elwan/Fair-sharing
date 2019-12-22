# Carpooling

Carpooling is a Python3 software which the main goal is to present and compare different allocation strategies (Stand-alone, proportional allocation, allocation by separation and Shapley value)..

## Installation

Unzip carpooling.zip file, to run the software use:

## Example
```bash
python3 ./main.py data.json
```

## Usage

```text
Where data.json is the input file with the following format:
```

```json
{
  "route": {
    "depCity": "Toulouse",
    "arrCity": "Munchen",
    "stops": [
      "Narbonne",
      "Lyon",
      "Grenoble"
    ],
    "distance": {
      "Toulouse": {
        "Narbonne": 100
      },
      "Narbonne": {
        "Lyon": 400
      },
      "Lyon": {
        "Grenoble": 50
      },
      "Grenoble": {
        "Munchen": 900
      }
    }
  },
  "costPerKm": 1,
  "Passengers": {
    "A": "Narbonne",
    "B": "Lyon",
    "C": "Grenoble",
    "D": "Munchen"
  }
}
```


## License
[MIT](https://choosealicense.com/licenses/mit/)
