odoo.define('sf_chatter_like.widget.Thread', function (require) {
"use strict";

    var DocumentViewer = require('mail.DocumentViewer');
    var mailUtils = require('mail.utils');

    var core = require('web.core');
    var time = require('web.time');
    var Widget = require('web.Widget');
    var ThreadWidget = require('mail.widget.Thread');
    var ThreadField = require('mail.ThreadField');
    var Message = require('mail.model.Message');
    var Notification = require('mail.Manager.Notification');

    var QWeb = core.qweb;

    Notification.include({
        _handlePartnerChannelNotification: function (channelData) {
            if (channelData.type == 'liked_message') {
                this._handlePartnerLikeNotification(channelData);
                return true;
            }
            this._super(channelData);
        },
        _handlePartnerLikeNotification: function (data) {
            var self = this;
            _.each(data.message_ids, function (messageID) {
                var message = _.find(self._messages, function (msg) {
                    return msg.getID() === messageID;
                });
                if (message) {
                    message.liked_partner_ids = data.liked_partner_ids;
                    message.liked_partner_name = data.liked_partner_name ? data.liked_partner_name.split(",") : [];
                    if (data.partner_id == self.getSession().partner_id) {
                        message.liked = data.liked;
                    }
                    self._mailBus.trigger('update_message', message);
                }
            });
        },
    });

    Message.include({
        init: function (parent, data, emojis) {
            this._super(parent, data, emojis);
            this.liked = data.liked || false;
            this.liked_partner_ids = data.liked_partner_ids || [];
            this.liked_partner_name = data.liked_partner_name ? data.liked_partner_name.split(",") : [];
        },
        likeMessage: function () {
            return this._rpc({
                    model: 'mail.message',
                    method: 'user_liked',
                    args: [[this._id]],
                });
        },
        unLikeMessage: function () {
            return this._rpc({
                    model: 'mail.message',
                    method: 'user_unliked',
                    args: [[this._id]],
                });
        }
    });

    ThreadField.include({
        start: function () {
            let self = this, res = this._super();
            this._threadWidget.on('action_liked_message', this, function (messageID) {
                var message = self.call('mail_service', 'getMessage', messageID);
                message.likeMessage();
            });
            this._threadWidget.on('action_unliked_message', this, function (messageID) {
                var message = self.call('mail_service', 'getMessage', messageID);
                message.unLikeMessage();
            });
            return res;
        },
    })

    ThreadWidget.include({
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.events['click .o_react:not([liked="true"]) > .spSvg'] = '_onClickMessageLike';
            this.events['click .o_react[liked="true"] > .spSvg'] = '_onClickUnLike';
            this._reactPopover = null;
            this.messageCheck = null;
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _renderReactPopover: function (thread, messages) {
            let self = this;
            if (this._reactPopover) {
                this._reactPopover.popover('hide');
                this._reactPopover.popover('disable');
            }
            if (!this.$('.tooltip_liked').length) {
                return;
            }
            this._reactPopover = this.$('.tooltip_liked').popover({
                html: true,
                boundary: 'viewport',
                placement: 'auto',
                trigger: 'hover',
                offset: '0, 1',
                content: function () {
                    var $this = $(this);
                    $this.popover('disable');
                    var messageID = $this.data('message-id');
                    var message = _.find(messages, function (message) {
                        return message.getID() === messageID;
                    });
                    if (message.liked_partner_name.length) {
                        $this.popover('enable');
                    }else {
                        $($this.data("bs.popover").tip).empty();
                    }
                    return QWeb.render('react.template', {message: message});
                },
            });
        },
        _onClickMessageLike: function (ev) {
            if (this._reactPopover) {
                this._reactPopover.popover("dispose");
            }
            var messageID = $(ev.currentTarget).data('message-id');
            if (this.messageCheck) {
                var message = _.find(this.messageCheck, function (message) {
                    return message.getID() === messageID;
                });
                message.likeMessage();
            }else {
                this.trigger('action_liked_message', messageID);
            }
        },
        _onClickUnLike: function (ev) {
            if (this._reactPopover) {
                this._reactPopover.popover("dispose");
            }
            var messageID = $(ev.currentTarget).data('message-id');
            if (this.messageCheck) {
                var message = _.find(this.messageCheck, function (message) {
                    return message.getID() === messageID;
                });
                message.unLikeMessage();
            }else {
                this.trigger('action_unliked_message', messageID);
            }
        },
        render: function (thread, options) {
            this._super(thread, options);
            var messages = _.clone(thread.getMessages({ domain: options.domain || [] }));
            this.messageCheck = messages;
            this._renderReactPopover(thread, messages);
        }
    });


});
