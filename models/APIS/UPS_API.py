import os
import base64
import requests
import logging
import json
import redis

URL_UPS_PRODUCTION = "https://onlinetools.ups.com/"

def get_config(key):
    configs = {
        'EANUPS_API_USER': os.environ.get('UPS_API_USER', 'YOUR_UPS_API_USER'),
        'EANUPS_API_PWD': os.environ.get('UPS_API_PWD', 'YOUR_UPS_API_PWD')
    }
    return configs.get(key)

def get_token_ups():
    USERNAME = get_config('EANUPS_API_USER')
    PASSWORD = get_config('EANUPS_API_PWD')

    claves = f"{USERNAME}:{PASSWORD}"
    encoded_credentials = base64.b64encode(claves.encode()).decode()

    r = redis.Redis(host='redis', port=6379, db=0)
    access_token = r.get("accessTokenUPS")

    if access_token:
        return access_token.decode()

    payload = "grant_type=client_credentials"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = requests.post(
        URL_UPS_PRODUCTION + "security/v1/oauth/token",
        headers=headers,
        data=payload
    )

    if response.status_code == 200:
        json_data = response.json()
        token = json_data.get("access_token")
        if token:
            r.set("accessTokenUPS", token, ex=3600)
            return token
    else:
        raise Exception(f"Error al obtener el token: {response.status_code} - {response.text}")

def ups_rates_v2(ship_city, ship_postal_code, state_province_code, ship_country_code, total_weight):
    try:
        logging.basicConfig(filename="eanups_v2.log", level=logging.DEBUG)

        access_token = get_token_ups()

        version = "v2403"
        request_option = "Shop"

        if total_weight == 0:
            total_weight = 1

        shipper_number = os.environ.get('UPS_SHIPPER_NUMBER', 'YOUR_SHIPPER_NUMBER')
        shipper_name   = os.environ.get('UPS_SHIPPER_NAME', 'YOUR_COMPANY_NAME')
        origin_address = os.environ.get('UPS_ORIGIN_ADDRESS', 'YOUR_ADDRESS')
        origin_city    = os.environ.get('UPS_ORIGIN_CITY', 'YOUR_CITY')
        origin_state   = os.environ.get('UPS_ORIGIN_STATE', 'XX')
        origin_postal  = os.environ.get('UPS_ORIGIN_POSTAL', '00000')
        origin_country = os.environ.get('UPS_ORIGIN_COUNTRY', 'ES')

        payload = {
            "RateRequest": {
                "Request": {
                    "TransactionReference": {"CustomerContext": "EAN0001"}
                },
                "Shipment": {
                    "Shipper": {
                        "Name": shipper_name,
                        "ShipperNumber": shipper_number,
                        "Address": {
                            "AddressLine": [origin_address, "", ""],
                            "City": origin_city,
                            "StateProvinceCode": origin_state,
                            "PostalCode": origin_postal,
                            "CountryCode": origin_country
                        }
                    },
                    "ShipTo": {
                        "Name": "",
                        "Address": {
                            "AddressLine": ["", "", ""],
                            "City": ship_city,
                            "StateProvinceCode": state_province_code,
                            "PostalCode": ship_postal_code,
                            "CountryCode": ship_country_code
                        }
                    },
                    "ShipFrom": {
                        "Name": shipper_name,
                        "Address": {
                            "AddressLine": [origin_address, "", ""],
                            "City": origin_city,
                            "StateProvinceCode": origin_state,
                            "PostalCode": origin_postal,
                            "CountryCode": origin_country
                        }
                    },
                    "PaymentDetails": {
                        "ShipmentCharge": {
                            "Type": "01",
                            "BillShipper": {"AccountNumber": shipper_number}
                        }
                    },
                    "ShipmentRatingOptions": {"NegotiatedRatesIndicator": "Y"},
                    "Service": {"Code": "02", "Description": "UPS Package"},
                    "NumOfPieces": "1",
                    "Package": {
                        "PackagingType": {"Code": "02", "Description": "Packaging"},
                        "Dimensions": {
                            "UnitOfMeasurement": {"Code": "CM", "Description": "Centimeters"},
                            "Length": "10", "Width": "10", "Height": "10"
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {"Code": "KGS", "Description": "Kilograms"},
                            "Weight": str(total_weight)
                        }
                    }
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "transId": "XXX1",
            "transactionSrc": "testingEAN"
        }

        response = requests.post(
            URL_UPS_PRODUCTION + f"api/rating/{version}/{request_option}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logging.error(f"Error de conexión con UPS: {response.status_code} - {response.text}")
            return []

        response_ups = response.json()
        rates_ups = []

        rated_shipments = response_ups.get("RateResponse", {}).get("RatedShipment", [])
        if isinstance(rated_shipments, list):
            for shipment in rated_shipments:
                service_code = shipment.get("Service", {}).get("Code")
                monetary_value = shipment.get("TotalCharges", {}).get("MonetaryValue")

                if service_code in ["11", "65"] and monetary_value and float(monetary_value) > 0:
                    rate = {
                        "Service": service_code,
                        "NetShipmentTotalPrice": shipment.get("NegotiatedRateCharges", {}).get("TotalCharge", {}).get("MonetaryValue")
                    }
                    rates_ups.append(rate)
        else:
            logging.error("ERROR_UPS_RESPONSE: No existe RateResponse['RatedShipment']")

        return rates_ups

    except Exception as e:
        logging.exception(f"Excepción en ups_rates_v2: {e}")
        return []
