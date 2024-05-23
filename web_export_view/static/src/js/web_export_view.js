openerp.web_export_view = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this,
                view_manager = self.getParent().ViewManager,
                view_name = view_manager && view_manager.active_view,
                active_view = view_name && view_manager.views[view_name];
            this._super.apply(this, arguments);
            if (active_view.controller instanceof instance.web.ListView) {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls').on('click', self.on_sidebar_export_view_xls);
            }
        },

        on_sidebar_export_view_xls: function (e, active_domain) {
            var self = this,
                view = this.getParent(),
                fields_view = view.fields_view,
                children = view.getChildren(),
                deferred = new jQuery.Deferred();
            if (children) {
                children.every(function (child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; 
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; 
                    }
                    return true;
                });
            }
            export_columns_keys = [];
            export_columns_names = [];
            $.each(view.visible_columns, function () {
                if (this.tag == 'field') {
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            if(view.$(
                'tr.oe_list_header_columns > th > ' +
                'input.oe_list_record_selector:checked'
            ).length == 0) {
                row_ids = view.$(
                    '.oe_list_content > tbody > tr[data-id]' +
                    ':has(th.oe_list_record_selector > input:checked)'
                ).map(function() {
                    return parseInt(jQuery(this).data('id'));
                }).toArray();
                deferred = view.dataset.read_ids(row_ids, export_columns_keys);
            }
            else {
                deferred = view.dataset.read_slice(export_columns_keys);
                export_columns_names.push(
                    _t('Selected records:') + ' ' +
                    String(
                        _(view.ViewManager.searchview.query.pluck('values'))
                        .chain().flatten(true).pluck('label').value()
                        .join('; ') || _('All records')
                    )
                );
            }
            var x2many = _(export_columns_keys).filter(function(field) {
                return ['one2many', 'many2many']
                    .indexOf(fields_view.fields[field].type) > -1;
            });
            if(x2many.length) {
                deferred = deferred.then(function(records) {
                    var name_gets = [], names = {};
                    _(records).chain().map(function(record) {
                        return _(record).chain().pairs().filter(function(pair)
                        {
                            return x2many.indexOf(pair[0]) > -1;
                        })
                        .value()
                    })
                    .flatten(true)
                    .groupBy(0)
                    .each(function(pairs, field) {
                        name_gets.push(
                            new instance.web.Model(
                                fields_view.fields[field].relation
                            )
                            .call('name_get', [
                                _(pairs).chain().pluck(1).flatten(true)
                                .value(),
                                view.dataset.get_context()
                            ])
                            .then(function(name_gets) {
                                names[field] = _.object(name_gets);
                            })
                        );
                    })
                    return jQuery.when.apply(jQuery, name_gets)
                    .then(function() {
                        _(records).each(function(record) {
                            _(x2many).each(function(field) {
                                record[field] = _(record[field])
                                .map(function(id) {
                                    return names[field][id];
                                })
                                .join(', ');
                                record[
                                    _.str.sprintf('%s__display', field)
                                ] = record[field];
                            });
                        });
                        return records;
                    });
                });
            }
            return deferred.then(function(records) {
                var export_rows = [];
                $.each(records, function(index, record) {
                    var export_row = [],
                        record = new instance.web.list.Record(record).toForm();
                    $.each(view.visible_columns, function() {
                        if(this.tag == 'field'){
                            export_row.push(
                                this.type != 'integer' && this.type != 'float' ?
                                jQuery('<div/>').html(this.format(
                                    record.data, {process_modifiers: false}
                                )).text() : record.data[this.id].value
                            );
                        };
                    })
                    export_rows.push(export_row);
                });
                view.session.get_file({
                    url: '/web/export/xls_view',
                    data: {data: JSON.stringify({
                        model: view.model,
                        headers: export_columns_names,
                        rows: export_rows,
                    })},
                });
            });
        }
    });

};
