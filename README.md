# Transportistas — Módulo Odoo

Módulo personalizado para Odoo que permite calcular y comparar tarifas de envío en tiempo real entre múltiples transportistas. Desarrollado durante las prácticas formativas en **Electronic Automation Network SL**.

## ¿Qué hace?

El módulo añade un formulario en Odoo donde el usuario introduce los datos del envío (peso, dimensiones, país, ciudad y código postal de destino) y obtiene al instante una lista comparativa de precios de los transportistas disponibles.

## Transportistas integrados

| Transportista | Protocolo | Autenticación |
|---|---|---|
| DHL | REST (HTTP GET) | Basic Auth |
| UPS | REST (HTTP POST) | OAuth2 + caché Redis |
| MBE | SOAP (WSDL) | Basic Auth con zeep |
| Odoo nativo | ORM interno | — |

## Tecnologías

- Python 3
- Odoo 16 (módulo personalizado)
- `requests` — llamadas REST a DHL y UPS
- `zeep` — cliente SOAP para MBE
- `redis` — caché del token OAuth2 de UPS
- XML (vistas y seguridad de Odoo)

## Estructura

```
transportistas/
├── models/
│   ├── models.py          # Modelo principal carrier_query
│   └── APIS/
│       ├── DHL_API.py     # Integración REST con DHL Express
│       ├── UPS_API.py     # Integración OAuth2 + REST con UPS
│       └── MBE_API.py     # Integración SOAP con MBE
├── views/
│   └── views.xml          # Formulario y vistas Odoo
├── security/
│   └── ir.model.access.csv
└── __manifest__.py
```

## Cómo funciona

1. El usuario rellena el formulario con los datos del paquete
2. Al pulsar el botón, el módulo llama en paralelo a las APIs de DHL, UPS y MBE
3. Los precios devueltos se muestran en una lista comparativa dentro del propio formulario de Odoo
4. El token de UPS se cachea en Redis durante 1 hora para evitar llamadas innecesarias de autenticación

## Instalación

1. Copia la carpeta `transportistas/` en el directorio de addons de tu instancia Odoo
2. Activa el modo desarrollador en Odoo
3. Ve a **Aplicaciones → Actualizar lista de aplicaciones**
4. Busca "transportistas" e instala el módulo
5. Configura las credenciales de cada API en los archivos correspondientes de `/models/APIS/`

> **Nota:** Para usar UPS es necesario tener Redis corriendo (`redis` en el mismo host o ajusta el host en `UPS_API.py`)

## Autor

Bryan Steven Ramírez Guerrero  
Prácticas DAM — Electronic Automation Network SL  
Alaquàs, Valencia — 2025
