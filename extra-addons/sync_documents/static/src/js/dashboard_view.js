odoo.define('sync_documents.AbstractDashboard', function (require) {
    "use strict";

    var KanbanView = require('web.KanbanView');
    var ListView = require('web.ListView');

    var DashboardKanbanController = require('sync_documents.DashboardKanbanController');
    var DashboardKanbanModel = require('sync_documents.DashboardKanbanModel');
    var DashboardKanbanRenderer = require('sync_documents.DashboardKanbanRenderer');
    var DocumentsSearchPanel = require('sync_documents.DocumentsSearchPanel');

    var DashboardListController = require('sync_documents.DashboardListController');
    var DashboardListRenderer = require('sync_documents.DashboardListRenderer')

    var view_registry = require('web.view_registry');
    const core = require('web.core');
    const _lt = core._lt;

    var AbstractDashboard = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: DashboardKanbanController,
            Model: DashboardKanbanModel,
            Renderer: DashboardKanbanRenderer,
            SearchPanel: DocumentsSearchPanel,
        }),
        display_name: _lt('Documents Dashboard'),
        groupable: false,
        searchMenuTypes: ['filter', 'favorite'],
        init: function () {
            this._super.apply(this, arguments);
            var extraFields = [
                'active',
                'store_fname',
                'display_name',
                'folder_id',
                'message_follower_ids',
                'message_ids',
                'activity_ids',
                'message_attachment_count',
                'mimetype',
                'name',
                'partner_id',
                'res_id',
                'res_model',
                'res_model_name',
                'res_name',
                'tag_ids',
                'type',
                'url',
            ];
            _.defaults(this.fieldsInfo[this.viewType], _.pick(this.fields, extraFields));
        },

        _createSearchPanel: async function (parent, params) {
            this.searchPanelParams.context = this.loadParams.context;
            return this._super.apply(this, arguments);
        }
    });

    var AbstractListDashboard = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: DashboardListController,
            Renderer: DashboardListRenderer,
            SearchPanel: DocumentsSearchPanel,
        }),
        display_name: _lt('Documents List'),
    });

    view_registry.add('documents_dashboard', AbstractDashboard);
    view_registry.add('documents_dashboard_list', AbstractListDashboard);

    return {
        'AbstractDashboard': AbstractDashboard,
        'AbstractListDashboard': AbstractListDashboard
    };

});
