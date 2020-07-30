odoo.define('sync_documents.DashboardKanbanModel', function (require) {
"use strict";

var KanbanModel = require('web.KanbanModel');

var DashboardKanbanModel = KanbanModel.extend({
    fetchSpecialData: function (recordID) {
        var record = this.localData[recordID];
        return this._fetchSpecialActivity(record, 'activity_ids').then(function (data) {
            record.specialData.activity_ids = data;
        });
    },
});

return DashboardKanbanModel;

});
