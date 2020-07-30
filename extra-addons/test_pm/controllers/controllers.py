# -*- coding: utf-8 -*-
# from odoo import http


# class TestPm(http.Controller):
#     @http.route('/test_pm/test_pm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_pm/test_pm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_pm.listing', {
#             'root': '/test_pm/test_pm',
#             'objects': http.request.env['test_pm.test_pm'].search([]),
#         })

#     @http.route('/test_pm/test_pm/objects/<model("test_pm.test_pm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_pm.object', {
#             'object': obj
#         })
