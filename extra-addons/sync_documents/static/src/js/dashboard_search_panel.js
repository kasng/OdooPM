odoo.define('sync_documents.DocumentsSearchPanel', function (require) {
    "use strict";

    var core = require('web.core');

    const SearchPanel = require('web.SearchPanel');

    var qweb = core.qweb;

    const DocumentsSearchPanel = SearchPanel.extend({

        init: function (parent, params) {
            this._super.apply(this, arguments);
            this.context = params.hasOwnProperty('context') ? params.context : null;
        },

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


        /**
         * @private
         * @param {Object} category
         * @returns {string}
         */
        _renderCategory: function (category) {
            console.log(category);
            console.log(this.context);
            return qweb.render('SyncDoc.SearchPanel.Category', {category: category});
        },

        _fetchCategories: function () {
            var self = this;
            var proms = Object.keys(this.categories).map(function (categoryId) {
                var category = self.categories[categoryId];
                var field = self.fields[category.fieldName];
                var categoriesProm;
                if (field.type === 'selection') {
                    var values = field.selection.map(function (value) {
                        return {id: value[0], display_name: value[1]};
                    });
                    categoriesProm = Promise.resolve(values);
                } else {
                    categoriesProm = self._rpc({
                        method: 'search_panel_select_range',
                        model: self.model,
                        args: [category.fieldName],
                        kwargs: {
                            context: {
                                'res_model': self.context.default_res_model,
                                'res_id': self.context.default_res_id
                            }
                        },
                    }).then(function (result) {
                        category.parentField = result.parent_field;
                        return result.values;
                    });
                }
                return categoriesProm.then(function (values) {
                    self._createCategoryTree(categoryId, values);
                });
            });
            return Promise.all(proms);
        },
    });

    return DocumentsSearchPanel;

});
