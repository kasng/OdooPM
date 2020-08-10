odoo.define('sync_documents.DocumentsSearchPanel', function (require) {
    "use strict";

    const SearchPanel = require('web.SearchPanel');

    const DocumentsSearchPanel = SearchPanel.extend({

        get_folders: function () {
            var categ = _.findWhere(this.categories, {fieldName: 'folder_id'});
            return _.map(_.keys(categ.values), fId => {
                return categ.values[fId];
            });
        },

        get_selected_folder_id: function () {
            var categ = _.findWhere(this.categories, {fieldName: 'folder_id'});
            return categ.activeValueId;
        },

        get_selected_tag_ids: function () {
            var filter = _.findWhere(this.filters, {fieldName: 'tag_ids'});
            return _.filter(_.keys(filter.values), tId => {
                return filter.values[tId].checked;
            });
        },

        get_tags: function () {
            var filter = _.findWhere(this.filters, {fieldName: 'tag_ids'});
            return _.sortBy(_.map(_.keys(filter.values), tId => filter.values[tId]), (i, o) => {
                return (i.group_sequence === o.group_sequence) ? i.sequence - o.sequence : i.group_sequence - o.group_sequence;
            });
        },

    });

    return DocumentsSearchPanel;

});
