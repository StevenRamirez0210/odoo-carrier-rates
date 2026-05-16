import os
import random
import string

def get_mbe_rates(country, city, zipcode, weight, length, width, height, service):
    from zeep import Client, Settings
    from zeep.transports import Transport
    from requests import Session

    wsdl_url = 'https://api.mbeonline.es/ws/e-link.wsdl'
    username = os.environ.get('MBE_USERNAME', 'YOUR_MBE_USERNAME')
    pwd      = os.environ.get('MBE_PASSWORD', 'YOUR_MBE_PASSWORD')

    session = Session()
    session.auth = (username, pwd)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Zeep'
    })

    transport = Transport(session=session)
    settings = Settings(strict=False)
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
    client.service._binding_options['address'] = 'https://api.mbeonline.es/ws'
    reference = generate_random_string(10)

    request_data = {
        'RequestContainer': {
            'System': "",
            'Credentials': {
                'Username': username,
                'Passphrase': pwd
            },
            'InternalReferenceID': reference,
            'ShippingParameters': {
                'DestinationInfo': {
                    'Country': country,
                    'ZipCode': zipcode,
                    'City': city
                },
                'ShipType': 'EXPORT',
                'PackageType': 'GENERIC',
                'Insurance': 'false',
                'Service': service,
                'Items': {
                    'Item': [
                        {
                            'Weight': weight,
                            'Dimensions': {
                                'Lenght': length,
                                'Width': width,
                                'Height': height
                            }
                        }
                    ]
                }
            }
        }
    }

    return client.service.ShippingOptionsRequest(**request_data)

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))
