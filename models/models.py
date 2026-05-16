from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from .APIS import UPS_API
from .APIS import MBE_API
from .APIS import DHL_API

class carrier_query(models.Model):
    _name = 'transportistas.carrier_query'
    _description = 'transportistas.carrier_query'

    show_prices = fields.Boolean(default=False)
    weight = fields.Float(string="Weight", required=True)
    country = fields.Char(string="Country", required=True)
    ship_city = fields.Char(string="City", required=True)
    broad = fields.Float(string="Broad", required=True)
    long = fields.Float(string="Long", required=True)
    province_state = fields.Char(string="Province/State", required=True)
    cp = fields.Char(string="CP", required=True)
    alp = fields.Char(string="A x L x P", compute="_compute_alp")

    list_carriers = fields.One2many('transportistas.carriers', 'carrier_id', string="List of carriers")

    @api.depends('long', 'broad', 'weight')
    def _compute_alp(self):
        for record in self:
            record.alp = record.long * record.broad * record.weight if record.long and record.broad and record.weight else 0

    def toggle_show_prices(self):
        for record in self:
            if record.show_prices:
                record.list_carriers = [(5, 0, 0)]
                record.show_prices = False
            else:
                if record.weight > 0 and record.broad > 0 and record.long > 0:
                    record.show_prices = True

                    carriers_info = []
                    carriers_info += record._get_odoo_carriers()
                    carriers_info += record._get_ups_carriers()
                    carriers_info += record._get_mbe_carriers('SSE')
                    carriers_info += record._get_mbe_carriers('SEE')
                    carriers_info += record._get_dhl_carriers()

                    record.list_carriers = [(5, 0, 0)]
                    record.list_carriers = [(0, 0, {'name': t['name'], 'price': t['price']}) for t in carriers_info]
                else:
                    raise ValidationError("Remember that the fields must be greater than 0")

    def _get_odoo_carriers(self):
        carriers_info = []
        carriers = self.env['delivery.carrier'].search([])
        for t in carriers:
            if t.delivery_type == "fixed":
                price = t.fixed_price
            elif t.delivery_type == "base_on_rule":
                order = self.env['sale.order'].search([], limit=1)
                if order:
                    shipment_rate = t.rate_shipment(order)
                    price = shipment_rate.get('price', 0.0) if shipment_rate else 0.0
                else:
                    price = 0.0
            else:
                price = 0.0

            carriers_info.append({'name': t.name, 'price': price})
        return carriers_info

    def _get_ups_carriers(self):
        carriers_info = []
        try:
            ups_rates = UPS_API.ups_rates_v2(
                ship_city=self.ship_city,
                ship_postal_code=self.cp,
                state_province_code=self.province_state,
                ship_country_code=self.country,
                total_weight=self.weight
            )

            for rate in ups_rates:
                service_code = rate.get("Service")

                if service_code == "11":
                    service_name = "UPS Standard"
                elif service_code == "65":
                    service_name = "UPS Express"
                else:
                    service_name = f"UPS {service_code}"

                price = float(rate.get("NetShipmentTotalPrice", 0.0))
                carriers_info.append({'name': service_name, 'price': price})

        except Exception as e:
            logging.exception(f"Error obteniendo tarifas UPS: {str(e)}")
        return carriers_info

    def _get_mbe_carriers(self, service):
        carriers = []
        for record in self:
            try:
                response = MBE_API.get_mbe_rates(
                    country=record.country,
                    city=record.ship_city,
                    zipcode=record.cp,
                    weight=record.weight,
                    length=record.long,
                    width=record.broad,
                    height=record.weight,
                    service=service
                )

                if 'ShippingOptions' in response and response['ShippingOptions']:
                    for service in response['ShippingOptions']['ShippingOption']:
                        carriers.append({
                            'name': f"MBE - {service['ServiceDesc']}",
                            'price': float(service['NetShipmentTotalPrice'])
                        })
            except Exception:
                logging.getLogger(__name__).exception("Error retrieving MBE rates:")

        return carriers

    def _get_dhl_carriers(self):
        carriers_info = []
        try:
            response = DHL_API.get_dhl_rates(
                dest_country=self.country,
                dest_postal_code=self.cp,
                dest_city=self.ship_city,
                weight=self.weight,
                length=self.long,
                width=self.broad,
                height=self.weight  # reutilizas el peso como altura
            )

            if 'products' in response:
                for option in response['products']:
                    name = f"DHL - {option.get('productName', 'Sin nombre')}"
                    price = float(option.get('totalPrice', [{}])[0].get('price', 0.0))
                    carriers_info.append({'name': name, 'price': price})

        except Exception as e:
            logging.getLogger(__name__).exception("Error obteniendo tarifas DHL:")

        return carriers_info


class carriers(models.Model):
    _name = 'transportistas.carriers'
    _description = 'transportistas.carriers'

    name = fields.Char(string="Name", required=True)
    price = fields.Float(string="Price", required=True)
    carrier_id = fields.Many2one('transportistas.carrier_query', string="Carrier")