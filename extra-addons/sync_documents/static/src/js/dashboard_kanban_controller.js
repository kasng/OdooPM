odoo.define('sync_documents.DashboardKanbanController', function (require) {
    "use strict";

    const core = require('web.core');
    const session = require('web.session');
    var Chatter = require('mail.Chatter');
    var Dialog = require('web.Dialog');
    var KanbanController = require('web.KanbanController');
    var DashboardManager = require('sync_documents.DashboardManager');
    var DocumentViewer = require('mail.DocumentViewer');

    const DashboardCommonController = require('sync_documents.DashboardCommonController');
    const dragEventsMixins = require('sync_documents.dragEventsMixins');

    const Qweb = core.qweb;
    const _t = core._t;

    var DashboardKanbanController = KanbanController.extend(dragEventsMixins, DashboardCommonController, {
        events: _.extend({}, KanbanController.prototype.events, dragEventsMixins.dragEvents, {
            'mousedown .o_kanban_image, .o_nocontent_help': function (e) {
                e.preventDefault();
            },
        }),
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            on_select_record: '_onSelectRecord',
            on_files_download: '_onFilesDownload',
            on_archive_document: '_onArchiveDocument',
            on_unarchive_document: '_onUnArchiveDocument',
            on_open_chatter: '_onOpenChatter',
            on_perform_action: '_onPerformAction',
            on_open_model: '_onOpenModel',
            replace_file: '_onReplaceFile',
            on_close_chatter: '_onCloseChatter',
            on_attachment_preview: '_onAttachmentPreview',
            on_edit_record: '_onEditRecord',
            on_change_folder: '_onChangeFolder',
            on_change_tag: '_onChangeTag',
            on_upload_attachment: '_onUploadAttachment',
            on_attach_project: '_onOpenAttachProject',
            on_detach_project: '_onOpenDetachProject',
            on_show_excerpt: '_onShowExcerpt'
        }),
        init: function (parent, model, renderer, params) {
            console.log(arguments);
            this._super.apply(this, arguments);
            this.record = this.model.get(this.handle);
            this.recordIDs = [];
        },
        start: function () {
            this.$('.o_content').addClass('sd_documents_dashboard d-flex');
            return this._super.apply(this, arguments);
        },
        _onPerformAction: function (ev) {
            var self = this;
            return this._rpc({
                model: 'document.action.rule',
                method: 'action_execute',
                args: [[ev.data.selected_action_id], ev.data.attachment_ids],
            }).then(function () {
                return self.reload();
            });
        },
        _onOpenModel: function (ev) {
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Documents Entry',
                target: 'current',
                res_id: ev.data.selected_record_id,
                res_model: ev.data.selected_record_model,
                views: [[false, 'form']],
            });
        },
        _renderChatter: function (record, mailFields, options) {
            var self = this;
            var $chatterBlock = $(Qweb.render('DashboardChatter'));
            self.chatter = new Chatter(self, record, mailFields, options);
            return self.chatter.appendTo($chatterBlock).then(function () {
                self.$el.find('.sd_documents_dashboard').addClass('sd_chatter_open').append($chatterBlock);
                if (self.isClosedChatter && true === self.isClosedChatter) {
                    return self.closeChatter();
                }
            });
        },
        _loadChatter: function (record) {
            var self = this;
            return this.model.fetchSpecialData(record.id).then(function () {
                self.closeChatter();
                record = self.model.get(record.id);
                var options = {
                    display_log_button: true,
                    isEditable: true,
                };
                var mailFields = {
                    mail_thread: 'message_ids',
                    mail_followers: 'message_follower_ids',
                    mail_activity: 'activity_ids'
                };
                return self._renderChatter(record, mailFields, options);
            });
        },
        _onCloseChatter: function () {
            this.closeChatter();
            this.isClosedChatter = true;
        },

        closeChatter: function () {
            this.$el.find('.sd_documents_dashboard').removeClass('sd_chatter_open');
            this.$('.sd_chatter').remove();
            if (this.chatter) {
                this.chatter.destroy();
            }
        },

        _onReplaceFile: function (ev) {
            var self = this;
            var $upload_input = $('<input type="file" name="files[]"/>');
            $upload_input.on('change', function (e) {
                var f = e.target.files[0];
                var state = self.model.get(self.handle);
                var reader = new FileReader();

                reader.onload = function (e) {
                    // convert data from "data:application/zip;base64,R0lGODdhAQBADs=" to "R0lGODdhAQBADs="
                    var dataString = e.target.result;
                    var data = dataString.split(',', 2)[1];
                    var mimetype = dataString.substring(
                        dataString.indexOf(":") + 1,
                        dataString.indexOf(";")
                    );
                    return self._rpc({
                        model: 'ir.attachment',
                        method: 'write',
                        args: [[ev.data.id], {datas: data, mimetype: mimetype, store_fname: f.name, name: f.name}],
                    }).then(function () {
                        self.reload();
                    });
                };
                reader.readAsDataURL(f);
            });
            $upload_input.click();
        },
        _onUploadAttachment: function (ev) {
            var self = this;
            var $fileUploader = $(Qweb.render('FileUploader'));
            $fileUploader.on('change', function (e) {
                var file = e.target.files[0];
                var reader = new FileReader();
                reader.onload = function (e) {
                    var rowData = e.target.result;
                    var datas = rowData.split(',', 2)[1];
                    var mimeType = rowData.substring(
                        rowData.indexOf(":") + 1,
                        rowData.indexOf(";")
                    );
                    self._rpc({
                        model: 'ir.attachment',
                        method: 'write',
                        args: [[ev.data.id], {
                            datas: datas,
                            mimetype: mimeType,
                            type: 'binary',
                            store_fname: file.name,
                        }],
                    }).then(function () {
                        $fileUploader.removeAttr('disabled');
                        $fileUploader.val("");
                        self.reload();
                    });
                };
                reader.readAsDataURL(file);
            });
            $fileUploader.click();
        },
        _onOpenChatter: function (ev) {
            ev.stopPropagation();
            var state = this.model.get(this.handle);
            var record = _.findWhere(state.data, {id: ev.data.id});
            this.isClosedChatter = false;
            this._loadChatter(record);
        },
        _onArchiveDocument: function (ev) {
            var self = this;
            ev.stopPropagation();
            var recIDs = _.pluck(ev.data.records, 'id');
            this.model.actionArchive(recIDs, this.handle).then(function () {
                self.update({}, {reload: false});
            });
        },
        _onUnArchiveDocument: function (ev) {
            var self = this;
            ev.stopPropagation();
            var recIDs = _.pluck(ev.data.records, 'id');
            this.model.actionUnarchive(recIDs, this.handle).then(function () {
                self.update({}, {reload: false});
            });
        },
        _onFilesDownload: function (ev) {
            var self = this;
            ev.stopPropagation();
            var resIDs = ev.data.resIDs;
            if (resIDs.length === 1) {
                if (ev.data.records[0].data.type != "empty") {
                    window.location = '/web/content/' + resIDs[0] + '?download=true';
                }
            } else {
                var currentFolder = _.findWhere(self._searchPanel.get_folders(), {'id': self._searchPanel.get_selected_folder_id()});
                var folderName = currentFolder.display_name.trim().toLowerCase();
                session.get_file({
                    url: '/files/zip',
                    data: {
                        file_ids: resIDs,
                        zip_name: 'documents-' + folderName + '.zip',
                    },
                });
            }
            ;
        },
        _onChangeFolder: function (ev) {
            var self = this, selectedFolderID = ev.data.selectedFolderID,
                resIDs = ev.data.resIDs;
            console.log(ev.data.resIDs);
            this._updateRecord(resIDs, {'folder_id': selectedFolderID, 'tag_ids': [[6, 0, []]]})
        },
        _onChangeTag: function (ev) {
            var self = this, selectedTagID = ev.data.selectedTagID,
                resIDs = ev.data.resIDs,
                operation = ev.data.operation;
            if (operation === 'add') {
                this._updateRecord(resIDs, {'tag_ids': [[4, selectedTagID]]})
            } else {
                this._updateRecord(resIDs, {'tag_ids': [[3, selectedTagID]]})
            }
            ;
        },
        _rerenderChatter: function (state) {
            var self = this;
            if (this.chatter) {
                if (this.recordIDs.length === 1) { //&& this.$el.hasClass('sd_chatter_open')
                    var record = _.findWhere(state.data, {res_id: this.recordIDs[0]});
                    if (record) {
                        return self._loadChatter(record);
                    }
                    ;
                }
                ;
                self._onCloseChatter();
            }
            return Promise.resolve();
        },
        _update: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var state = self.model.get(self.handle);
                return self._rerenderChatter(state).then(() => {
                    self._renderDocumentManager(state, self.recordIDs);
                });
            });
        },
        _renderDocumentManager: function (state, recordIDs) {
            var self = this;

            const destroyDashboardManager = () => {
                if (this.dashboardManager) {
                    self.$el.find('.dashboard-manager-wrap').removeClass('is-active');
                    this.dashboardManager.destroy();
                }
                ;
            };

            if (_.isEmpty(recordIDs)) {
                destroyDashboardManager();
                return false;
            }
            ;
            var tags = [], removeTags = [], tagsByIDs = [];

            _.each(state.data, function (record) {
                if (_.contains(recordIDs, record.res_id)) {
                    tagsByIDs.push(record.data.tag_ids.res_ids);
                }
            });

            var filteredTagIDs = _.intersection.apply(_, tagsByIDs);
            tags = this._searchPanel.get_tags();
            removeTags = _.filter(tags, function (tag) {
                return _.contains(filteredTagIDs, tag.id);
            });

            tags = _.filter(tags, function (tag) {
                return !_.contains(filteredTagIDs, tag.id);
            });
            // update `display_name` of folders
            var folders = _.map(self._searchPanel.get_folders(), (f, i) => {
                return _.mapObject(f, (v, k) => {
                    return (k === "display_name" && f.parent_id) ? _.str.sprintf("%s / %s", f.parent_id[1], v) : v;
                });
            });

            var params = {
                recordIDs: recordIDs || _.pluck(state.data, 'res_id'),
                state: state,
                folders: folders,
                tags: tags,
                removeTags: removeTags || [],
                selectedFolderID: self._searchPanel.get_selected_folder_id(),
                isArchived: _.some(state.data, f => {
                    return !f.data.active;
                }),
            };

            destroyDashboardManager();
            if (!_.isEmpty(recordIDs)) {
                this.dashboardManager = new DashboardManager(this, params);
                this.dashboardManager.appendTo(this.$('.dashboard-manager-wrap'));
                this.$('.dashboard-manager-wrap').addClass('is-active');
                if (recordIDs.length === 1) {
                    this.$('.sf-doc-' + recordIDs[0]).addClass('sd_record_selected');
                }
            }
            ;
        },
        _onRecordSelect: function (recordIDs) {
            var self = this;
            var state = this.model.get(this.handle);
            state.currentRecords = recordIDs;
            this._rerenderChatter(state).then(function () {
                self._renderDocumentManager(state, recordIDs);
            });
            $('.sd_btn_edit').toggle(this.recordIDs.length === 1);
        },
        _onAttachmentPreview: function (ev) {
            var self = this, record = ev.data.record,
                recordID = ev.data.record.id;
            var documentViewer = new DocumentViewer(this, [record], recordID);
            documentViewer.appendTo(this.$('.sd_documents_dashboard_view'));
        },
        _onEditRecord: function (ev) {
            var self = this, recordID = ev.data.id;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_model_res_id',
                args: ["sync_documents.attachment_form_view"],
            })
                .then(function (data) {
                    console.log(data);
                    console.log(ev.data.res_id);
                    var state = $.bbq.getState(true);
                    return self.do_action({
                        type: 'ir.actions.act_window',
                        name: "Documents Dashboard",
                        res_model: 'ir.attachment',
                        views: [[data[1], 'form']],
                        target: 'current',
                        res_id: Number(String(ev.data.res_id).replace('ir.attachment_', '')),
                        view_id: 'sync_doc_attachment_form_view',
                        domain: [['res_field', '=', false], ['folder_id', '!=', false]],
                        id: state.action
                    });
                });
        },
        _updateRecord: function (recordID, form_values) {
            var self = this;
            return this._rpc({
                model: self.modelName,
                method: 'write',
                args: [recordID, form_values],
            }).then(function () {
                self.reload().then(function () {
                    self.$('.sf-doc-' + recordID).addClass('sd_record_selected');
                });
            });
        },
        _onSaveRecord: function (ev, recordID) {
            var self = this, form_values = {};
            var form_fields = $(ev.target).parents().find('.sd_edit_record_form').serializeArray();
            _.each(form_fields, function (input) {
                if (input.value !== '') {
                    form_values[input.name] = input.value;
                }
                ;
            });
            this._updateRecord(recordID, form_values);
        },
        _onSelectRecord: function (ev) {
            ev.stopPropagation();
            var state = this.model.get(this.handle);
            var shiftKey = ev.data.originalEvent.shiftKey;
            var ctrlKey = ev.data.originalEvent.ctrlKey || ev.data.originalEvent.metaKey;
            if (ev.data.flag || shiftKey || ctrlKey) {
                if (this.recordIDs.length === 1 && this.recordIDs[0] === ev.data.resID) {
                    this.recordIDs = [];
                } else if (shiftKey && !_.isEmpty(this.recordIDs)) {
                    var recordIDs = _.pluck(state.data, 'res_id');
                    var anchorIndex = recordIDs.indexOf(this.selectFromId);
                    var selectedRecordIndex = recordIDs.indexOf(ev.data.resID);
                    var lowerIndex = Math.min(anchorIndex, selectedRecordIndex);
                    var upperIndex = Math.max(anchorIndex, selectedRecordIndex);
                    var shiftSelection = recordIDs.slice(lowerIndex, upperIndex + 1);
                    if (ctrlKey) {
                        this.recordIDs = _.uniq(this.recordIDs.concat(shiftSelection));
                    } else {
                        this.recordIDs = shiftSelection;
                    }
                } else if (ctrlKey && !_.isEmpty(this.recordIDs)) {
                    var oldIds = this.recordIDs;
                    this.recordIDs = _.without(this.recordIDs, ev.data.resID);
                    if (this.recordIDs.length === oldIds.length) {
                        this.recordIDs.push(ev.data.resID);
                        this.selectFromId = ev.data.resID;
                    }
                } else {
                    this.recordIDs = [ev.data.resID];
                    this.selectFromId = ev.data.resID;
                }
                ;
            } else if (ev.data.selected) {
                this.recordIDs.push(ev.data.resID);
                this.recordIDs = _.uniq(this.recordIDs);
            } else {
                this.recordIDs = _.without(this.recordIDs, ev.data.resID);
            }
            ;
            this._onRecordSelect(this.recordIDs);
            this.renderer.selectRecord(this.recordIDs);
        },

        _onShowExcerpt: function (ev) {
            ev.stopPropagation();
            return new Dialog(this, {
                title: _t('Excerpt'),
                $content: Qweb.render('Document.Excerpt', {
                    'excerpt': ev.data.record.excerpt
                }),
            }).open();
        },

        _onOpenAttachProject: function (ev) {
            console.log(ev);
            ev.stopPropagation();
            var self = this;
            console.log(this.recordIDs);
            console.log(self.recordIDs[0]);
            console.log(ev.data.res_id);
            var state = $.bbq.getState(true);
            console.log(state);
            self._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_model_res_id',
                args: ["sync_documents.dha_document_project_list"],
            })
                .then(function (data) {
                    console.log(data);
                    var state = $.bbq.getState(true);
                    console.log(state);
                    return self.do_action({
                        type: 'ir.actions.act_window',
                        name: "Attach to Project",
                        res_model: 'ir.attachment',
                        views: [[data[1], 'form']],
                        target: 'new',
                        res_id: self.recordIDs[0],
                        id: state.action,
                        context: {
                            "selectedDocuments": self.recordIDs
                        }
                    }, {
                        on_close: function () {
                            self.trigger_up('reload');
                        },
                    });
                });
        },

        _onOpenDetachProject: function (ev) {
            console.log(ev);
            ev.stopPropagation();
            console.log(this.recordIDs);
        }
    });

    return DashboardKanbanController;

});
