backend_api = {
    "base_url": "https://api.example.com:8099/",
    "username": "gnovit",
    "password": "CHANGE_ME",
    "ignore-ssl-certificate-check": True,
    "endpoints": {
        "originate": "v1/originate",
        "blocks_units_by_condo": "v1/condo/{condo_id}/blocks_units",
    },
}

qrcode2call_url = 'https://qrcode2call.gnovit.com/call'

# qrcode2call_url = 'http://localhost:8080/call'

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
        'condo_id': '0000000',
    },
  
}
