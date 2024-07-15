backend_api = {
    "base_url": "http://127.0.0.1:8000/",
    "username": "dev",
    "password": "CHANGE_ME",
    "endpoints": {
        "originate": "v1/originate",
        "blocks_units_by_condo": "v1/condo/{condo_id}/blocks_units",
    },
}

condos = {
    "gnovit": {
        "url": "https://api.example.com:8099",
        "origin": "1000",
        "destination": {
            "101": "5500000000000",
            "102": "5500000000000",
            "103": "5500000000000",
            "201": "5500000000000",
        },
        "username": "gnovit",
        "password": "CHANGE_ME",
    },
    "terra_nova": {
        "url": "https://api.example.com:8099",
        "origin": "1001",
        "destination": {
            "101": "5500000000000",
            "102": "5500000000000",
            "103": "5500000000000",
            "201": "5500000000000",
        },
        "username": "gnovit",
        "password": "CHANGE_ME",
    },
    "condo2": {
        "url": "https://condo2.example.com:8098",
        "origin": "1000",
        "destination": {
            "101": "5500000000000",
            "102": "5500000000000",
            "103": "5500000000000",
            "201": "5500000000000",
        },
        "username": "condo2",
        "password": "CHANGE_ME",
    },
}
