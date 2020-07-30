# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import zipfile
import io
import logging

from ast import literal_eval
from odoo.http import request, content_disposition
from odoo.osv import expression
from odoo import http, tools
from odoo.tools import consteq

logger = logging.getLogger(__name__)

class Documents(http.Controller):

    def _make_zip(self, name, attachments):
        stream = io.BytesIO()
        try:
            with zipfile.ZipFile(stream, 'w') as doc_zip:
                for attachment in attachments:
                    if attachment.type in ['url', 'empty']:
                        continue
                    filename = attachment.name
                    doc_zip.writestr(filename, base64.b64decode(attachment['datas']),
                                     compress_type=zipfile.ZIP_DEFLATED)
        except zipfile.BadZipfile:
            logger.exception("BadZipfile exception")

        content = stream.getvalue()
        headers = [
            ('Content-Type', 'zip'),
            ('X-Content-Type-Options', 'nosniff'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition(name))
        ]
        return request.make_response(content, headers)

    @http.route(['/files/zip'], type='http', auth='user')
    def _get_zip(self, file_ids, zip_name, *args, **kwargs):
        ids_list = [int(x) for x in file_ids.split(',')]
        env = request.env
        return self._make_zip(zip_name, env['ir.attachment'].browse(ids_list))

    @http.route(['/attachment/download/<int:share_id>/<access_token>/<int:attachment_id>'], type='http', auth='public', website=True)
    def attachment_download(self, share_id=None, access_token=None, attachment_id=None, **post):
        share = request.env['attachments.share'].sudo().search([('id', '=', share_id)])
        if share and share.state != 'expired':
            status, headers, content = request.env['ir.http'].binary_content(model='ir.attachment', id=attachment_id, download=True)
            if status == 304:
                response = werkzeug.wrappers.Response(status=status, headers=headers)
            elif status == 301:
                return werkzeug.utils.redirect(content, code=301)
            elif status != 200:
                response = request.not_found()
            else:
                content_base64 = base64.b64decode(content)
                headers.append(('Content-Length', len(content_base64)))
                response = request.make_response(content_base64, headers)
        else:
            return request.render('sync_documents.link_expire', {})
        return response


    @http.route(["/attachment/upload/<int:share_id>/<token>"], type='http', auth='public', methods=['POST'], csrf=False)
    def attachment_upload(self, share_id=None, token=None, **kwargs):
        attachment_obj = request.env['ir.attachment']
        share = request.env['attachments.share'].sudo().browse(share_id)
        if share and share.type != 'upload' and share.state != 'expired':
            for file in request.httprequest.files.getlist('files'):
                data = file.read()
                datas = base64.b64encode(data)
                vals = {
                    'mimetype': file.content_type,
                    'name': file.filename,
                    'store_fname': file.filename,
                    'datas': datas,
                    'tag_ids': [(6, 0, share.tag_ids.ids)],
                    'folder_id': share.folder_id and share.folder_id.id or False
                }
                attachment = attachment_obj.sudo().create(vals)
            return """<script type='text/javascript'>
                    window.open("/attachment/share/%s/%s", "_self");
                </script>""" % (share_id, token)
        return request.not_found()

    @http.route(["/all_attachment/download/<int:share_id>"], type='http', auth='public')
    def all_attachment_download(self, share_id=None, **kwargs):
        domain = []
        try:
            share = request.env['attachments.share'].sudo().browse(share_id)
            if share and share.domain and share.state != 'expired':
                domain = literal_eval(share.domain)
                domain = expression.AND([domain, [['folder_id', '=', share.folder_id.id], ['type', '!=', 'empty']]])
                if share.tag_ids:
                    domain = expression.AND([domain, [['tag_ids', 'in', share.tag_ids and share.tag_ids.ids or []]]])
                attachments = request.env['ir.attachment'].sudo().search(domain)
                zip_name = share.name or 'shared' + '.zip'
                return self._make_zip(zip_name, attachments)
        except Exception:
            logger.exception("Failed to make zip")
        return request.not_found()


    @http.route(['/attachment/share/<int:share_id>/<token>'], type='http', auth='public')
    def attachment_share(self, share_id=None, token=None):
        domain, values = [], {}
        share = request.env['attachments.share'].sudo().browse(share_id)
        if share.state == 'expired':
            expire_vals = {'end_date': share.end_date}
            return request.render('sync_documents.link_expire', expire_vals)
        if not consteq(token, share.access_token):
            return request.not_found()

        if share.domain:
            domain = literal_eval(share.domain)
            domain = expression.AND([domain, [['folder_id', '=', share.folder_id.id], ['type', '!=', 'empty']]])
            if share.tag_ids:
                domain = expression.AND([domain, [['tag_ids', 'in', share.tag_ids and share.tag_ids.ids or []]]])
            attachments = http.request.env['ir.attachment'].sudo().search(domain)
            values.update({
                'token': str(token),
                'share': share,
                'attachments': attachments,
            })
        return request.render('sync_documents.document', values)
