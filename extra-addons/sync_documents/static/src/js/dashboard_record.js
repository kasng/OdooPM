odoo.define('sync_documents.DashboardRecord', function (require) {
    "use strict";

    var KanbanRecord = require('web.KanbanRecord');

    var DashboardRecord = KanbanRecord.extend({
        events: _.extend({}, KanbanRecord.prototype.events, {
            'click .o_kanban_details': '_onSelectRecord',
            'click .sd_request_image': '_onAttachmentRequest',
            'click .o_kanban_image_preview': '_onAttachmentPreview',
            'click .sd_record_selector': '_onSelectionOfToggle'
        }),
        start: function () {
            this._super.apply(this, arguments);
        },
        getID: function () {
            return this.id;
        },
        _onSelectionOfToggle: function (ev) {
            this._onToggleSelect(true, ev);
        },
        _onAttachmentRequest: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('on_upload_attachment', {id: this.id});
        },
        update: function () {
            var self = this;
            var selected = this.$el.hasClass('o_record_selected');
            return this._super.apply(this, arguments).then(function () {
                if (selected) {
                    self.$el.addClass('o_record_selected');
                }
                ;
            });
        },
        selectRecord: function (selected) {
            this.$el.toggleClass('sd_record_selected', selected);
        },
        _onToggleSelect: function (flag, ev) {
            this.trigger_up('on_select_record', {
                flag: flag,
                originalEvent: ev,
                resID: this.getID(),
                selected: !this.$el.hasClass('sd_record_selected'),
            });
        },
        _onSelectRecord: function (ev) {
            ev.preventDefault();
            if (!$(ev.target).hasClass('oe_kanban_action')) {
                this._onToggleSelect(true, ev);
            }
        },
        _onAttachmentPreview: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('on_attachment_preview', {record: this.recordData});
        }

    });

    return DashboardRecord;

});
