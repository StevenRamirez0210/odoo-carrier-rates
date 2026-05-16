# -*- coding: utf-8 -*-
# from odoo import http


# class Transportistas(http.Controller):
#     @http.route('/transportistas/transportistas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transportistas/transportistas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('transportistas.listing', {
#             'root': '/transportistas/transportistas',
#             'objects': http.request.env['transportistas.transportistas'].search([]),
#         })

#     @http.route('/transportistas/transportistas/objects/<model("transportistas.transportistas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transportistas.object', {
#             'object': obj
#         })
