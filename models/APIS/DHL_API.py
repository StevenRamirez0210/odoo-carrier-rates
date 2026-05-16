import os
import requests
import logging

def get_dhl_rates(
    dest_country, dest_postal_code, dest_city,
    weight, length, width, height
):
    url = "https://express.api.dhl.com/mydhlapi/test/rates"
    headers = {
        "accept": "application/json",
        "Message-Reference": "d0e7832e-5c98-11ea-bc55-0242ac13",
        "Message-Reference-Date": "Wed, 21 Oct 2015 07:28:00 GMT",
        "x-version": "2.12.0",
        "Authorization": f"Basic {os.environ.get('DHL_AUTH_TOKEN', 'YOUR_DHL_AUTH_TOKEN')}"
    }

    params = {
        "accountNumber": os.environ.get('DHL_ACCOUNT_NUMBER', 'YOUR_DHL_ACCOUNT_NUMBER'),
        "originCountryCode": os.environ.get('ORIGIN_COUNTRY', 'ES'),
        "originPostalCode": os.environ.get('ORIGIN_POSTAL_CODE', '00000'),
        "originCityName": os.environ.get('ORIGIN_CITY', 'YOUR_ORIGIN_CITY'),
        "destinationCountryCode": dest_country,
        "destinationPostalCode": dest_postal_code,
        "destinationCityName": dest_city,
        "weight": weight,
        "length": length,
        "width": width,
        "height": height,
        "plannedShippingDate": "2025-04-11",
        "isCustomsDeclarable": "false",
        "unitOfMeasurement": "metric",
        "nextBusinessDay": "false",
        "strictValidation": "false",
        "getAllValueAddedServices": "false",
        "requestEstimatedDeliveryDate": "true",
        "estimatedDeliveryDateType": "QDDF"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except Exception:
        logging.getLogger(__name__).exception("Error en DHL API:")
        return {}
