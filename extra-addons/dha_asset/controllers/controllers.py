# -*- coding: utf-8 -*-
# from odoo import http


# class DhaAsset(http.Controller):
#     @http.route('/dha_asset/dha_asset/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dha_asset/dha_asset/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dha_asset.listing', {
#             'root': '/dha_asset/dha_asset',
#             'objects': http.request.env['dha_asset.dha_asset'].search([]),
#         })

#     @http.route('/dha_asset/dha_asset/objects/<model("dha_asset.dha_asset"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dha_asset.object', {
#             'object': obj
#         })
