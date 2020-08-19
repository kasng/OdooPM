odoo.define('sync_documents.DashboardManager', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    const core = require('web.core');
    const Qweb = core.qweb;

    var DashboardManager = Widget.extend({
        template: 'DashboardManager',
        events: {
            'click .sd_btn_download': '_onFileDownload',
            'click .sd_btn_archive': '_onArchiveDocument',
            'click .sd_btn_un_archive': '_onUnArchiveDocument',
            'click .sd_btn_chatter': '_onOpenChatter',
            'click .sd_btn_replace': '_onReplaceDocument',
            'click .sd_btn_edit': '_onEditRecord',
            'click .sd_btn_folder .dropdown-item ': '_onChangeFolder',
            'click .sd_btn_tags .add-tag .dropdown-item': '_onAddTag',
            'click .actions_menu .dropdown-item': '_onAction',
            'click .js_open_corresponding_record': '_onOpenCorrespondingRecord',
            'click .sd_btn_tags .dropdown-submenu .dropdown-item ': '_onRemoveTag',
            'mouseover .dropdown-submenu': '_onOpenSubMenu',
            'mouseout .sd_btn_tags': '_onCloseSubMenu',
            'click .sd_btn_chatter_close': '_onCloseChatter',
            'click .attach-project': '_onOpenAttachProject',
            'click .detach-project': '_onOpenDetachProject',
        },
        init: function (parent, params) {
            var self = this;
            this._super.apply(this, arguments);
            this.recordIDs = params.recordIDs;
            this.records = [];
            this.folders = params.folders;
            this.tags = params.tags;
            this.removeTags = params.removeTags;
            this.selectedFolderID = params.selectedFolderID;
            this.isArchived = params.isArchived;
            this.documentActionRules = [];
            this.correspondingRecords = {};
            this._getRecords(params);
        },
        willStart: function () {
            return Promise.all([
                this._getActions(),
                this._getCorrespondingRecords(),
                this._super.apply(this, arguments)
            ]);
        },
        start: function () {
            this._processFields();
            this._hideChatter();
            return this._super.apply(this, arguments);
        },
        _hideChatter: function () {
            var self = this;
            if (self.recordIDs.length == 1) {
                var $chatter = $(Qweb.render('sync_documents.Chatter'));
                self.$('.chatter').replaceWith($chatter);
            }
            ;
        },
        _getActions: function () {
            var self = this;
            if (!this.selectedFolderID) {
                return false;
            }
            ;
            // var selectedID = this.selectedFolderID;
            // var selectedFolder = _.findWhere(this.folders, {id: selectedID});
            return this._rpc({
                model: 'document.action.rule',
                method: 'get_action_rules',
                args: [this.selectedFolderID, self.recordIDs],
            }).then(function (results) {
                self.documentActionRules = results;
            });
        },
        _getCorrespondingRecords: function () {
            var self = this;
            if (!this.recordIDs || this.recordIDs.length > 1) {
                return Promise.resolve();
            }
            ;
            return this._rpc({
                model: 'document.action.rule',
                method: 'get_corresponding_records',
                args: [[], this.recordIDs[0]],
            }).then(function (records) {
                self.correspondingRecords = records;
            });
        },
        _onAction: function (ev) {
            ev.preventDefault();
            this.trigger_up('on_perform_action', {
                selected_action_id: $(ev.target).data('id'),
                attachment_ids: this.recordIDs
            });
        },
        _onOpenCorrespondingRecord: function (ev) {
            ev.preventDefault();
            this.trigger_up('on_open_model', {
                selected_record_id: $(ev.target).data('id'),
                selected_record_model: $(ev.target).data('model'),
            });
        },
        _onReplaceDocument: function () {
            this.trigger_up('replace_file', {
                id: this.records[0].data.id,
            });
        },
        _onOpenSubMenu: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            $(ev.target).find('.dropdown-menu').stop(true, true).fadeIn("slow");
            $(ev.target).addClass('show');
        },
        _onCloseSubMenu: function (ev) {
            $(ev.target).find('.dropdown-submenu .dropdown-menu').stop(true, true).fadeOut("fast");
            $(ev.target).find('.dropdown-submenu .dropdown-menu').removeClass('show');
        },
        _renderField: function (fieldName, options) {
            var record;
            options = options || {};
            // generate the record to pass to the FieldWidget
            var values = _.uniq(_.map(this.records, function (record) {
                if (fieldName === 'name') {
                    return record.data[fieldName];
                } else {
                    return record.data[fieldName] && record.data[fieldName].res_id;
                }
                ;
            }));
        },
        _processFields: function () {
            var options = {mode: 'edit'};
            if (this.records.length === 1) {
                this._renderField('name', options);
            }
            ;
        },
        _getRecords: function (params) {
            var self = this;
            _.each(params.recordIDs, function (resID) {
                var record = _.findWhere(params.state.data, {res_id: resID});
                if (record) {
                    self.records.push(record);
                }
                ;
            });
        },
        _onOpenChatter: function () {
            this.trigger_up('on_open_chatter', {
                id: this.records[0].id,
            });
        },
        _onCloseChatter: function () {
            this.trigger_up('on_close_chatter');
        },
        _onFileDownload: function (ev) {
            this.trigger_up('on_files_download', {
                resIDs: _.pluck(this.records, 'res_id'),
                records: this.records
            });
        },
        _onEditRecord: function () {
            this.trigger_up('on_edit_record', {
                id: this.records[0].id,
                res_id: this.records[0].res_id
            });
        },
        _onChangeFolder: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.selectedFolderID = $(ev.target).data('id');
            this.trigger_up('on_change_folder', {
                resIDs: _.pluck(this.records, 'res_id'),
                selectedFolderID: this.selectedFolderID,
            });
        },
        _onAddTag: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($(ev.target).parents('.dropdown-submenu').length === 0) {
                this.selectedTagID = $(ev.target).data('id');
                this.trigger_up('on_change_tag', {
                    operation: 'add',
                    resIDs: _.pluck(this.records, 'res_id'),
                    selectedTagID: this.selectedTagID,
                });
            }
            ;
        },
        _onRemoveTag: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.selectedTagID = $(ev.target).data('id');
            this.trigger_up('on_change_tag', {
                operation: 'remove',
                resIDs: _.pluck(this.records, 'res_id'),
                selectedTagID: this.selectedTagID,
            });
        },
        _onArchiveDocument: function () {
            var self = this;
            this.trigger_up('on_archive_document', {
                records: self.records,
            });
        },
        _onUnArchiveDocument: function () {
            this.trigger_up('on_unarchive_document', {
                records: this.records,
            });
        },

        _onOpenAttachProject: function (ev) {
            ev.preventDefault();
            this.trigger_up('on_attach_project', {
                records: this.records,
            });
        },
        _onOpenDetachProject: function (ev) {
            ev.preventDefault();
            this.trigger_up('on_detach_project', {
                records: this.records,
            });
        }
    });

    return DashboardManager;

});