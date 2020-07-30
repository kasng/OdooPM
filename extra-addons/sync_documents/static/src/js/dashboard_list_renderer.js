odoo.define('sync_documents.DashboardListRenderer', function (require) {
"use strict";

var ListRenderer = require('web.ListRenderer');

var DashboardListRenderer = ListRenderer.extend({
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            const _classes = 'sd_documents_dashboard_view h-100';
            self.$el.addClass(_.str.sprintf(_classes + " %s", _.contains(odoo._modules, 'allure_backend_theme') ? 'oe_allure' : ''));
        });
    },
});

return DashboardListRenderer;

});
