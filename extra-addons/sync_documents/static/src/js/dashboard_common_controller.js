odoo.define('sync_documents.DashboardCommonController', function (require) {
    "use strict";

    const core = require('web.core');
    const Qweb = core.qweb;

    return {

        _processUpload: function (files) {
            var self = this;
            var defs = [];
            var tagIDs = this._searchPanel.get_selected_tag_ids();
            _.each(files, function (f) {
                var def = $.Deferred();
                defs.push(def);
                var reader = new FileReader();
                reader.onload = function (ev) {
                    def.resolve({
                        name: f.name,
                        store_fname: f.name,
                        datas: ev.target.result,
                    });
                };
                reader.readAsDataURL(f);
            });
            return $.when.apply($, defs).then(function () {
                var records = Array.prototype.slice.call(arguments);
                _.each(records, function (record) {
                    record.datas = record.datas.split(',', 2)[1];
                    record.folder_id = self._searchPanel.get_selected_folder_id();
                    if (!_.isEmpty(tagIDs)) {
                        record.tag_ids = [[6, 0, tagIDs]];
                    }
                    ;
                });
                return self._rpc({
                    model: 'ir.attachment',
                    method: 'create',
                    args: [records],
                });
            });
        },

        _onUploadDocument: function () {
            var self = this;
            var $fileUploader = $(Qweb.render('FileUploader'));
            $fileUploader.on('change', function (ev) {
                self._processUpload(ev.target.files).always(function () {
                    self.reload();
                    $fileUploader.remove();
                });
            });
            $fileUploader.click();
        },

        _onUploadUrl: function (ev) {
            ev.preventDefault();
            var self = this;
            this.do_action('sync_documents.action_attachment_upload_url', {
                additional_context: {
                    default_folder_id: self._searchPanel.get_selected_folder_id(),
                    default_tag_ids: [[6, 0, self._searchPanel.get_selected_tag_ids()]],
                },
                on_close: function () {
                    self.reload();
                },
            });
        },

        _onRequestDoc: function (ev) {
            ev.preventDefault();
            var self = this;
            this.do_action('sync_documents.action_request_attachment', {
                additional_context: {
                    default_folder_id: this._searchPanel.get_selected_folder_id(),
                    default_tag_ids: [[6, 0, this._searchPanel.get_selected_tag_ids()]],
                },
                on_close: function () {
                    self.reload();
                },
            });
        },

        _onShareDoc: function (ev) {
            ev.preventDefault();
            var self = this;
            var state = this.model.get(this.handle, {raw: true});
            var vals = {
                domain: [['res_field', '=', false], ['folder_id', '!=', false]],
                folder_id: self._searchPanel.get_selected_folder_id(),
                tag_ids: [[6, 0, self._searchPanel.get_selected_tag_ids()]],
            };
            return this._rpc({
                model: 'attachments.share',
                method: 'on_create_share',
                args: [vals],
            }).then(function (result) {
                self.do_action(result);
            });
        },

        _updateButtons: function () {
            this._super.apply(this, arguments);
            if (this._oldSearchPanel && !this._searchPanel) {
                this._searchPanel = _.clone(this._oldSearchPanel);
            }
            const selectedFolderId = this._searchPanel.get_selected_folder_id();
            this.$buttons.find('.sd_dashboard_upload').prop('disabled', !selectedFolderId);
            this.$buttons.find('.sd_dashboard_url').prop('disabled', !selectedFolderId);
            this.$buttons.find('.sd_dashboard_request').prop('disabled', !selectedFolderId);
            this.$buttons.find('.sd_dashboard_share').prop('disabled', !selectedFolderId);
        },

        renderButtons: function ($node) {
            this.$buttons = $(Qweb.render('DashboardView.buttons'));
            this.$buttons.on('click', '.sd_dashboard_upload', _.bind(this._onUploadDocument, this));
            this.$buttons.on('click', '.sd_dashboard_url', _.bind(this._onUploadUrl, this));
            this.$buttons.on('click', '.sd_dashboard_request', _.bind(this._onRequestDoc, this));
            this.$buttons.on('click', '.sd_dashboard_share', _.bind(this._onShareDoc, this));
            this.$buttons.appendTo($node);
            this._updateButtons();
        },
    }

});
