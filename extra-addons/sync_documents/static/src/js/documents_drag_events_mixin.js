odoo.define('sync_documents.dragEventsMixins', function (require) {
"use strict";

const core = require('web.core');
const Qweb = core.qweb;

return {
    dragEvents: {
        'drop .sd_documents_dashboard_view': '_onDrop',
        'dragover .sd_documents_dashboard_view': '_onDragOver',
        'dragleave .sd_documents_dashboard_view': '_onDragLeave',
    },

    _onDrop: function (ev) {
        ev.preventDefault();
        var self = this;
        const removeDropOverlay = () => {
            self.renderer.$el.removeClass('sd_drop_over');
            self.$('.sd_upload_overlay').remove();
        };

        if (!self._searchPanel.get_selected_folder_id()) {
            removeDropOverlay();
            return false;
        };

        this._processUpload(ev.originalEvent.dataTransfer.files).always(function () {
            removeDropOverlay();
            self.reload();
        });
    },

    _onDragOver: function (ev) {
        ev.preventDefault();
        this.renderer.$el.addClass('sd_drop_over');
        if (!this.$('.sd_upload_overlay').length) {
            this.$('.sd_documents_dashboard_view').append($(Qweb.render('DocumentsUpload')))
        };
        $(document).on('dragover:kanbanView', _.bind(this._onDragLeave, this));
    },

    _onDragLeave: function (ev) {
        var target = document.elementFromPoint(ev.originalEvent.clientX, ev.originalEvent.clientY);
        if ($.contains(this.renderer.$el[0], ev.target) || $.contains(this.renderer.$el[0], target)) {
            return;
        };

        $(document).off('dragover:kanbanView');
        this.renderer.$el.removeClass('sd_drop_over');
        this.$('.sd_upload_overlay').remove();
    },
};

});