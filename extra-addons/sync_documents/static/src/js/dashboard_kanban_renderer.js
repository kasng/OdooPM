odoo.define('sync_documents.DashboardKanbanRenderer', function (require) {
    "use strict";

    var KanbanRenderer = require('web.KanbanRenderer');
    var DashboardRecord = require('sync_documents.DashboardRecord');

    var DashboardKanbanRenderer = KanbanRenderer.extend({
        config: _.extend({}, KanbanRenderer.prototype.config, {
            KanbanRecord: DashboardRecord,
        }),
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                const _classes = 'sd_documents_dashboard_view position-relative ' +
                    'align-content-start d-flex justify-content-center align-items-center order-2 h-100';
                self.$el.addClass(_.str.sprintf(_classes + " %s", _.contains(odoo._modules, 'allure_backend_theme') ? 'oe_allure' : ''));
                _.defer(function () {
                    self.$el.wrap($('<div>', {
                        class: 'sd_dashboard_body d-flex flex-column',
                    }));
                    self.setElement(self.$el);
                    self.$el.parent().append('<div class="dashboard-manager-wrap"></div>');
                });
            });
        },
        _onCheckSelection: function (recordIDs) {
            if (recordIDs.length !== 0) {
                this.$el.closest('.sd_documents_dashboard').addClass('sd_open_manager')
                    .removeClass('sd_selected_records')
            } else if (recordIDs.length > 1) {
                this.$el.closest('.sd_documents_dashboard').addClass('sd_selected_records')
            } else {
                this.$el.closest('.sd_documents_dashboard').removeClass('sd_open_manager')
                    .removeClass('sd_selected_records')
            }
        },
        selectRecord: function (recordIDs) {
            this._onCheckSelection(recordIDs);
            _.each(this.widgets, function (widget) {
                var isSelected = _.contains(recordIDs, widget.getID());
                widget.selectRecord(isSelected);
            });
        },
    });

    return DashboardKanbanRenderer;
});
