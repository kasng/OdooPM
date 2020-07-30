odoo.define('sync_documents.DashboardListController', function (require) {
"use strict";

var ListController = require('web.ListController');
const DashboardCommonController = require('sync_documents.DashboardCommonController');
const dragEventsMixins = require('sync_documents.dragEventsMixins');


var DashboardListController = ListController.extend(dragEventsMixins, DashboardCommonController, {
    events: _.extend({}, ListController.prototype.events, dragEventsMixins.dragEvents),

    start: function () {
        this.$('.o_content').addClass('sd_documents_dashboard d-flex');
        return this._super.apply(this, arguments);
    },

});

return DashboardListController;

});
