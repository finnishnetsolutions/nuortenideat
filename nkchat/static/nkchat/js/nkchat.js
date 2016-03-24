/*global window*/

(function(window, _, $, Firechat, Mustache, Backbone, console) {

    "use strict";

    var ROLE_ORGANIZATION_ADMIN = 3;
    var ROLE_MODERATOR = 5;

    var ROOM_ROLE_RESPONDENT = 'respondent';
    var ROOM_ROLE_PARTICIPANT = 'participant';
    var ROOM_ROLE_MODERATOR = 'moderator';

    var DEBUG = false;

    console = DEBUG ? console : {log: function () {}};

    var BaseView = Backbone.View.extend({
        effectIn: "fadeIn",
        effectOut: "fadeOut",
        subViewFactory: function (klass, opts) {
            return (new klass(_.extend({chat: this.chat, room: this.room}, opts || {})));
        },
        initialize: function (opts) {
            opts = opts || {};
            this.chat = opts.chat;
            this.room = opts.room;
            this.context = opts.context || {};
            this.initializeSubViews(opts);
            this.bindEvents();
        },
        initializeSubViews: function () {
        },
        bindEvents: function () {
        },
        template: function (ctx) {
            return Mustache.template(this.templateName).render(ctx);
        },
        render: function () {
            var ctx = this.templateContext();
            //console.log('rendering', this.templateName, 'with ctx', ctx);
            this.$el.html(this.template(ctx));
            return this;
        },
        templateContext: function () {
            return this.context || {};
        },
        isActive: function isActive() {
            return this.$el.hasClass('active');
        },
        flash: function () {
            var self = this;
            self.$el[self.effectOut]("fast", function () {
                self.$el[self.effectIn]("fast");
            });
        }
    });

    var ModalView = BaseView.extend({
        className: "modal fade",
        render: function () {
            this._super();
            this.$el.modal();
            return this;
        }
    });

    var ChatMessageView = BaseView.extend({
        tagName: 'li',
        templateName: 'chat-message',
        templateContext: function () {
            var ctx = _.extend({}, this._super());
            ctx.timestamp = moment(ctx.timestamp).format('H.mm');
            ctx.ownMessage = ctx.userId == this.chat.user.uid;
            ctx.deletion = this.room.canModerate();
            return ctx;
        },
        events: {
            'click .delete-message': 'deleteMessage'
        },
        deleteMessage: function (e) {
            e.preventDefault();
            console.log('deleting message', this.id);
            this.room.messagesRef.child(this.id).child('deleted').set(true);
        },
        className: "clearfix chat-message"
    });

    var ChatMessagesView = BaseView.extend({
        tagName: 'ul',
        className: 'chat',
        initialize: function (opts) {
            this._super(opts);
            this.scrollToBottom = _.throttle(this.scrollToBottom, 200);
            this.jumpToBottom = _.once(_.debounce(this.jumpToBottom, 50));
            this.addNotification = _.debounce(this.addNotification, 100);
            _.bindAll(this, 'addMessage', 'scrollToBottom');
        },
        bindEvents: function () {
            var self = this;
            this._super();
            this.room.messagesRef.on('child_removed', function (child) {
                // not used from the UI - messages are always just marked as deleted
                var messageId = child.name();
                console.log('message', messageId, 'removed');
                self.$('#' + messageId).replaceWith(
                    Mustache.template('message-removed').render()
                );
            });
            this.room.messagesRef.on('child_changed', function (child) {
                var messageId, val = child.val();
                if (val && val.deleted) {
                    messageId = child.name();
                    console.log('message', messageId, 'marked as deleted');
                    self.$('#' + messageId).replaceWith(
                        Mustache.template('message-removed').render()
                    );
                }
            });
        },
        render: function () {
            return this;
        },
        addMessage: function (message) {
            this.$el.append(
                this.subViewFactory(
                    ChatMessageView, {context: message, id: message.id}
                ).render().$el
            );
            this.scrollToBottom();
            this.jumpToBottom();
        },
        addNotification: function (html) {
            this.$el.append(html);
            this.scrollToBottom();
        },
        jumpToBottom: function () {
            this.$el.parent('.room-messages').scrollTop(this.$el.height());
        },
        scrollToBottom: function () {
            var $body = this.$el.parent('.room-messages');
            var target = this.$el.height();
            $body.animate({scrollTop: target});
        }
    });

    var GroupChatMessagesView = ChatMessagesView.extend({
        initialize: function (opts) {
            this.wasModerated = null;
            this.showModeationStatus = _.throttle(this.showModerationStatus, 2000);
            this._super(opts);
        },
        bindEvents: function () {
            var self = this;
            this._super();
            _.bindAll(this, 'showModerationStatus');
            this.room.on('blocked-roles-change', this.showModerationStatus);
        },
        render: function () {
            this._super();
            this.showModerationStatus();
            return this;
        },
        showModerationStatus: function () {
            console.log('showModerationStatus', _.keys(this.room.blockedRoles).length);
            var isModerated = _.keys(this.room.blockedRoles).length > 0;
            if ((isModerated && ((this.wasModerated === false) || !this.room.canChat())) || this.wasModerated) {
                this.addNotification(Mustache.template('room-moderated').render(
                   {blocked: this.room.blockedRoles}
                ));
            }
            this.wasModerated = isModerated;
            console.log('wasModerated', this.wasModerated);
        }
    });

    var ChatMessageFormView = BaseView.extend({
        templateName: 'message-form',
        tagName: "form",
        bindEvents: function (opts) {
            _.bindAll(this, 'submit');
        },
        events: {
            'submit': 'submit'
        },
        submit: function (e) {
            e.preventDefault();
            var msg = this.$('.chat-message').val().replace(/^\s+|\s+$/g, '');
            if(msg) {
                this.chat.fireChat.sendMessage(
                    this.room.id,
                    this.$('.chat-message').val(),
                    this.room.getRole() + '-message'
                );
                this.trigger('message-sent');
                this.$('.chat-message').val('').focus();
            }
        }
    });

    var GroupChatMessageFormView = ChatMessageFormView.extend({
        bindEvents: function () {
            var self = this;
            this._super();
            _.bindAll(this, 'blockingChanged');
            this.room.on('blocked-roles-change', this.blockingChanged);
            this.room.on('destroyed', function () {
                self.$('#btn-chat').addClass('disabled');
                self.$('.chat-message')
                    .prop('disabled', true)
                    .val('Keskustelu on päättynyt.');
            });
        },
        render: function () {
            this._super().blockingChanged();
            return this;
        },
        blockingChanged: function () {
            this.$('#btn-chat').toggleClass('disabled', !this.room.canChat());
        }
    });

    var ChatTabView = BaseView.extend({
        templateName: 'chat-tab',
        tagName: 'li',
        initialize: function (opts) {
            this.label = opts.label;
            this.refreshNewMessages = _.debounce(this.refreshNewMessages, 300);
            _.bindAll(this, 'refreshNewMessages');
            this._super(opts);
        },
        open: function () {
            this.$el.children('a').trigger('click');
            return this;
        },
        templateContext: function () {
            var labelShort = this.label;

            if(this.label.length > 6) {
                labelShort = this.label.substring(0, 6) + '…';
            }

            return {id: this.room.id,
                    label: this.label,
                    labelShort: labelShort};
        },
        deactivate: function () {
            this.$el.removeClass('active');
        },
        refreshNewMessages: function () {
            console.log('REFRESH NewMessage', this.room.name, this.room.unreadMessages);
            if(this.room.unreadMessages > 0) {
                this.$('.new-messages').html(
                    $('<span class="badge"/>').text(this.room.unreadMessages)
                );
            } else {
                this.$('.new-messages').html('');
            }
        }
    });

    var ChatWindowView = BaseView.extend({
        formView: ChatMessageFormView,
        messagesView: ChatMessagesView,
        className: 'fade in tab-pane',
        initializeSubViews: function () {
            this.form = this.subViewFactory(this.formView);
            this.messages = this.subViewFactory(this.messagesView);
        },
        render: function () {
            this._super();
            this.$('.room-messages').html(this.messages.render().$el);
            this.$('.panel-footer').html(this.form.render().$el);
            console.log('ChatWindowView render');
            return this;
        },
        deactivate: function (onComplete) {
            var $el = this.$el;
            $el.children('.chat-panel').fadeOut("fast", function () {
                $el.removeClass("active");
                $(this).removeAttr('style');
                if(onComplete) {
                    onComplete();
                }
            });
            return this;
        },
        flash: function () {
            var self = this, $el = this.$('.chat-panel');
            $el[self.effectOut]("fast", function () {
                $el[self.effectIn]("fast");
            });
        }
    });

    var PrivateChatWindowView = ChatWindowView.extend({
        templateName: 'private-chat-window',
        initialize: function (opts) {
            this._super(opts);
            this.partner = opts.partner;
        }
    });

    var GroupChatUserContextMenu = BaseView.extend({
        templateName: 'room-user-context-menu',
        className: 'chat-user-contextmenu',
        initialize: function (opts) {
            this.trigger = opts.trigger;
            this.userId = $(this.trigger.target).data('uid');
            this.userRole = $(this.trigger.target).data('role');
            _.bindAll(this, 'destroy', 'toggleRespondent');
            this._super(opts);
        },
        bindEvents: function () {
            var self = this;
            $('body').on('click', this.destroy);
            $('body').on('contextmenu', this.destroy);

        },
        events: {
            'click .toggle-respondent': 'toggleRespondent'
        },
        toggleRespondent: function (e) {
            e.preventDefault();
            console.log('toggleRespondent', this.room, this);
            if (this.userRole === ROOM_ROLE_RESPONDENT) {
                this.room.metaRef.child('respondents').child(this.userId).remove();
                console.log('removed', this.userId, 'from respondents');
            } else {
                this.room.metaRef.child('respondents').child(this.userId).set(true);
                console.log('added', this.userId, 'to respondents');
            }
        },
        destroy: function () {
            this.remove();
        },
        templateContext: function () {
            return {
                'makeRespondent': this.userRole !== ROOM_ROLE_RESPONDENT,
                'removeRespondent': this.userRole === ROOM_ROLE_RESPONDENT
            }
        },
        render: function () {
            var elWidth, windowWidth = $(window).width(),
                elHeight, windowHeight = $(window).height();
            $('body').append(this._super().$el);
            elWidth = this.$el.children('ul').first().width();
            elHeight = this.$el.children('ul').first().height();
            this.$el.css({
                display: 'block',
                left: Math.min(windowWidth - elWidth - 40, this.trigger.pageX),
                top: this.trigger.pageY+10
            });
            return this;
        }
    });

    var GroupChatUsersView = BaseView.extend({
        tagName: 'ul',
        templateName: 'group-chat-users',
        initialize: function (opts) {
            this._usersCache = [];
            this._super(opts);
        },
        bindEvents: function () {
            var self = this;
            _.bindAll(this, 'refreshUsers', 'showUserContextMenu');
            this.room.on('users-updated', _.once(this.refreshUsers));
            this.room.on('users-updated', _.debounce(this.refreshUsers), 5000);
            this.room.refreshUsers();
        },
        events: function () {
            return {
               'click li a': 'showUserContextMenu',
               'contextmenu li a': 'showUserContextMenu'
            };
        },
        showUserContextMenu: function (e) {
            console.log('showContext');
            e.preventDefault();
            e.stopPropagation();
            if (this.room.canModerate()) {
                this.subViewFactory(GroupChatUserContextMenu, {
                    trigger: e
                }).render();
            }
        },
        templateContext: function () {
            return {
                users: this._usersCache,
                blockedRoles: this.room.blockedRoles
            };
        },
        // TODO: move permcheck method to this.room?
        userIsRespondent: function (uid) {
            return _.contains(this._respondentsCache, uid || this.chat.user.uid);
        },
        refreshUsers: function (users) {
            this._usersCache = _.groupBy(users, 'role');
            this.render();
        }
    });

    var GroupChatSettingsView = BaseView.extend({
        tagName: 'ul',
        className:'dropdown-menu',
        attrs: {
            'role': 'menu'
        },
        templateName: 'group-chat-settings-menu',
        bindEvents: function () {
            _.bindAll(this, 'render');
            this.room.on('blocked-roles-change', this.render);
        },
        templateContext: function () {
            return {
                blockedRoles: this.room.blockedRoles
            }
        }
    });

    var GroupChatWindowView = ChatWindowView.extend({
        formView: GroupChatMessageFormView,
        messagesView: GroupChatMessagesView,
        className: 'fade in tab-pane group-chat',
        templateName: 'group-chat-window',
        bindEvents: function () {
            var self = this;
            this._super();
            _.bindAll(this, 'toggleBlocking', 'render');
        },
        initializeSubViews: function () {
            var self = this;
            this._super();
            this.users = this.subViewFactory(GroupChatUsersView);
            this.settings = this.subViewFactory(GroupChatSettingsView);
        },
        events: {
            'click .toggle-role-blocking': 'toggleBlocking',
            'click .delete-room': 'deleteRoom'
        },
        toggleBlocking: function (e) {
            e.preventDefault();
            this.room.toggleBlocking($(e.target).data('role'));
        },
        deleteRoom: function (e) {
            e.preventDefault();
            console.log('deleteRoom', e.target);
            if (window.confirm($(e.target).data('confirmation'))) {
                console.log('CLOSE', this.room.id);
                this.room.archive();
            }
            this.trigger('deleted');
        },
        templateContext: function () {
            return _.extend({}, this._super(), {
                settingsMenu: this.room.canModerate(),
                blockedRoles: this.room.blockedRoles
            });
        },
        render: function () {
            this._super();
            this.$('.room-users').html(this.users.render().$el);
            if(this.room.canModerate()) {
                this.$('.window-actions').prepend(this.settings.render().$el);
            }
            return this;
        }
    });

    var ChatView = BaseView.extend({
        bindEvents: function () {
            _.bindAll(this, 'toggle', 'minimize', 'markMinimized', 'close', 'addMessage');
            this.tab.delegateEvents({
                'click': this.toggle,
                'markMinimized': this.markMinimized
            });
            this.window.$el.on('click', '.minimize-chat', this.minimize);
            this.window.$el.on('click', '.close-chat', this.close);
            this.window.on('deleted', this.close);

            this.minimizationKey = 'room.' + this.room.id + '.minimized';
            this.lastReadKey = 'room.' + this.room.id + '.lastRead';
        },
        addMessage: function (message) {
            this.room.lastMessageTimestamp = message.timestamp;
            console.log('ADD MESSAGE', this.room.name)
            if(this.tab.isActive()) {
                console.log('ADD MESSAGE', this.room.name, 'was active');
                this.room.unreadMessages = 0;
                window.sessionStorage.removeItem(this.minimizationKey);
                window.sessionStorage.setItem(this.lastReadKey, message.timestamp);
            } else {
                console.log('ADD MESSAGE', this.room.name, 'not active');
                var lastReadMessageTimestamp = parseInt(
                    window.sessionStorage.getItem(this.lastReadKey) || 0
                );
                if (message.timestamp > lastReadMessageTimestamp) {
                    this.room.unreadMessages++;
                    console.log('INC ', this.room.unreadMessages);
                } else {
                    console.log('NO INC ', this.room.unreadMessages, message.timestamp, '>', lastReadMessageTimestamp);
                }
            }
            this.window.messages.addMessage(message);
            this.tab.refreshNewMessages();
        },
        render: function () {
            this.tab.render();
            this.window.render();
            this.chat.$tabs.append(this.tab.$el);
            this.chat.$tabContent.prepend(this.window.$el);
                        this.open();
            console.log('ChatView render')
            return this;
        },
        unminimize: function () {
            window.sessionStorage.removeItem(this.minimizationKey);
            window.sessionStorage.setItem(this.lastReadKey, this.room.lastMessageTimestamp);
            this.window.$el.toggleClass('active', true);
            this.room.unreadMessages = 0;
            this.tab.refreshNewMessages();
            this.window.messages.scrollToBottom();
        },
        open: function (unminimize) {
            if (unminimize) {
                this.unminimize();
            }
            if (window.sessionStorage.getItem(this.minimizationKey)) {
            } else {
                if(this.tab.isActive()) {
                    this.tab.flash();
                } else {
                    this.tab.open();
                }
            }
        },
        minimize: function () {
            this.tab.deactivate();
            this.window.deactivate();
            this.markMinimized();
        },
        markMinimized: function () {
            window.sessionStorage.setItem(this.minimizationKey, true);
            console.log('MARKED');
        },
        toggle: function (e) {
            e.preventDefault();

            if(this.tab.isActive()) {
                this.minimize();
                e.stopPropagation();
            } else {
                this.tab.$el.siblings().not('.dropup').trigger('markMinimized');
                this.unminimize();
                // active class needs to exist for a tab-pane for fade-effect to work
                if(this.chat.$tabContent.children('.active').length === 0) {
                    this.window.$el.toggleClass('active', true);
                }
            }
        },
        close: function () {
            var self = this;
            this.window.deactivate(function () {
                self.tab.remove();
                self.window.remove();
                self.remove();
                self.trigger('closed');
            });
        }
    });

    var PrivateChatView = ChatView.extend({
        public: false,
        initializeSubViews: function (opts) {
            var self = this;
            this.partner = opts.partner;
            this.setPartnerOnlineStatusWithLag = _.debounce(
                this.setPartnerOnlineStatus, 8000
            );
            this.tab = this.subViewFactory(ChatTabView, {
                label: this.partner.name
            });
            this.window = this.subViewFactory(PrivateChatWindowView, {
                partner: this.partner,
                context: this.partner,
                id: this.room.id
            });
        },
        bindEvents: function () {
            var self = this;
            this._super();
            this.partnerOnline = null;
            this.partnerInRoom = null;
            this.partnerInvited = false;
            this.partnerInRoomRef = this.chat.usersRef.child(this.partner.uid)
                                                      .child('rooms')
                                                      .child(this.room.id);
            this.partnerOnlineRef = this.chat.usersOnlineRef.child(
                this.partner.name.toLowerCase()
            );
            this.partnerInRoomRef.on('value', function (snapshot) {
                var inRoom = !!snapshot.val();
                if(inRoom === false) {
                    self.partnerInvited = false;
                }
                self.partnerInRoom = inRoom;
                console.log('partnerInRoom', inRoom);
            });
            this.window.form.on('message-sent', function () {
                if((self.partner.uid !==  self.chat.user.uid) &&
                   (self.partnerInRoom === false) &&
                   (self.partnerInvited === false))
                {
                    self.partnerInvited = true;
                    self.chat.fireChat.inviteUser(self.partner.uid, self.room.id);
                    console.log('invited', self.partner.uid, 'to', self.room.id);
                }
            });
            _.bindAll(this, 'partnerOnlineStatusChanged');
            this.partnerOnlineRef.on('value', this.partnerOnlineStatusChanged);
        },
        partnerOnlineStatusChanged: function (snapshot) {
            var isOnline = !!snapshot.val();
            if(this.partnerOnline === null) {
                this.setPartnerOnlineStatus(isOnline);
            } else {
                this.setPartnerOnlineStatusWithLag(isOnline);
            }
        },
        setPartnerOnlineStatus: function (isOnline) {
            this.window.form.$el.find('#btn-chat').toggleClass('disabled', !isOnline);
            console.log(isOnline, 'partner status');
            if(this.partnerOnline !== isOnline) {
                if(((this.partnerOnline === null) && !isOnline)  || (this.partnerOnline !== null)) {
                    this.window.messages.addNotification(
                        Mustache.template('partner-online-status-change').render({
                            name: this.partner.name,
                            online: isOnline
                        })
                    );
                }
            }
            this.partnerOnline = isOnline;
        }
    });

    var GroupChatView = ChatView.extend({
        public: true,
        initializeSubViews: function (opts) {
            var self = this;
            this._super(opts);
            this.tab = this.subViewFactory(ChatTabView, {
                label: '#' + this.room.name
            });
            this.window = this.subViewFactory(GroupChatWindowView, {
                id: this.room.id
            });
        }
    });

    var CreateGroupChatView = ModalView.extend({
        templateName: 'create-group-chat',
        initialize: function (opts) {
            this._super(opts);
            _.bindAll(this, 'submit');
        },
        events: {
            'submit form': 'submit'
        },
        submit: function (e) {
            var name = this.$('#new-group-chat-name').val();
            e.preventDefault();
            console.log('creating group chat with name', name);
            this.chat.createGroupChat(name);
            this.$el.modal('hide');
        }
    });

    function NkChat(firebaseUrl, authToken, target, opts) {
        this.opts = opts || {};
        this.fireBase = new Firebase(firebaseUrl);
        this.authToken = authToken;

        this.$wrap = target;
        this.$tabs = null;
        this.$tabContent = null;
        this.$supportPersonnel = null;
        this.$groupChatsButton = null;

        this.privateChats = {}; // uid -> roomId
        this.rooms = {};

        this.fireChat = null;

        this.onlineModsRef = this.fireBase.child('moderators-online');
        this.onlineOrgAdminsRef = this.fireBase.child('organization-admins-online');
        this.usersOnlineRef = this.fireBase.child('user-names-online');
        this.roomUsersRef = this.fireBase.child('room-users');
        this.roomMetaRef = this.fireBase.child('room-metadata');
        this.roomMessagesRef = this.fireBase.child('room-messages');

        this.usersRef = this.fireBase.child('users');
        this.myPresenceTimestamp = null;

        this.user = null;

        _.bindAll(this, 'login', 'authCallback', 'render', 'refreshOnlineModerators',
                        'openPrivateChat');

        this.render();
        this.bindUIEvents();
        this.refreshOnlineModerators();
        this.refreshOnlineOrganizationAdmins();
        this.login();
    };

    NkChat.prototype = {
        bindUIEvents: function () {
            var self = this;
            this.$wrap.on('click', '.open-private-chat', function (e) {
                var name = $(this).attr('data-name'),
                    uid = $(this).attr('data-uid');
                e.preventDefault();
                if (uid in self.privateChats) {
                    self.rooms[self.privateChats[uid]].open(true);
                    return;
                } else {
                    //console.log('not yet chatting with', uid, 'creating room');
                    self.createPrivateRoom({uid: uid, name: name});
                }
            });
            this.$wrap.on('click', '.create-group-chat', function (e) {
                e.preventDefault();
                (new CreateGroupChatView({chat: self})).render();
            });
            this.$wrap.on('click', '.create-group-chat-submit', function (e) {
                this.createGroupChat($('#new-group-chat-name').val());
            });
            this.$wrap.on('click', '.open-group-chat', function (e) {
                var roomId = $(this).data('room-id');
                e.preventDefault();
                if (roomId in self.rooms) {
                    self.rooms[roomId].open(true);
                } else {
                    self.fireChat.enterRoom($(this).data('room-id'));
                }
            });
        },
        updatePresenceTimestamp: function () {
            this.myPresenceTimestamp.set(Firebase.ServerValue.TIMESTAMP);
            _.delay(_.bind(this.updatePresenceTimestamp, this), 15000);
            console.log('presence updated and re-scheduled');
        },
        bindDataEvents: function () {
            var self = this;

            self.myPresenceTimestamp = self.usersRef.child(self.user.uid)
                .child('onlineAt');

            self.updatePresenceTimestamp();

            this.fireChat.on('room-enter', function (room) {
                var partner;
                room.usersRef = self.roomUsersRef.child(room.id);
                room.metaRef = self.roomMetaRef.child(room.id);
                room.messagesRef = self.roomMessagesRef.child(room.id);
                room._selfCreated = room.creator.uid == self.user.uid;
                room._respondentsCache = [];
                room.blockedRoles = {};
                room._bindings = {};
                room.destroyed = false;
                room.unreadMessages = 0;
                room.trigger = function (event) {
                    var args = Array.prototype.slice.call(arguments, 1);
                    if (event in room._bindings) {
                        _.each(room._bindings[event], function (cb) {
                            cb.apply(null, args);
                        });
                    }
                };
                room.metaRef.on('value', function (snapshot) {
                    var val = snapshot.val();
                    if((!!val === false) || (val.type === 'archived')) {
                        self.fireChat.leaveRoom(room.id);
                        console.log('DESTROYYY');
                        room.trigger('destroyed');
                        room.destroyed = true;
                    }
                });
                room.getRole = function (uid) {
                    var role, uid = uid || self.user.uid;
                    if(_.contains(room._respondentsCache, uid)) {
                        return ROOM_ROLE_RESPONDENT;
                    } else if(uid == room.creator.uid && room.type == "public") {
                        return ROOM_ROLE_MODERATOR;
                    } else {
                        role = uid.split('-')[0];
                        if (role == 'organization') {
                            role = ROOM_ROLE_PARTICIPANT;  // You are not special.
                        }
                        return role;
                    }
                };
                room.on = function (event, callback) {
                    if (!(event in room._bindings)) {
                        room._bindings[event] = [];
                    }
                    room._bindings[event].push(callback);
                };
                room.usersUpdated = function (snapshot) {
                    var self = this, users = snapshot.val();
                    users = _.map(users, function (u) {
                        var user = _.values(u)[0];
                        user.role = room.getRole(user.id)
                        return user;
                    });
                    room.trigger('users-updated', users);
                };
                room.refreshUsers = function () {
                    room.usersRef.once('value', room.usersUpdated);
                };
                room.metaRef.child('respondents').on('value', function (snapshot) {
                    room._respondentsCache = _.keys(snapshot.val()) || [];
                    room.refreshUsers();
                });
                room.canModerate = function () {
                    return (room._selfCreated && room.type == "public") || self.canModerate() ||
                        _.contains(room._respondentsCache, self.user.uid);
                };
                room.destroy = function () {
                    room.metaRef.remove();
                };
                room.archive = function () {
                    room.metaRef.child('endedAt').set(Firebase.ServerValue.TIMESTAMP);
                    room.metaRef.child('type').set('archived');
                };
                room.metaRef.child('blocked-roles').on('value', function (snapshot) {
                    room.blockedRoles = snapshot.val() || {};
                    console.log('BLOCKING', room.blockedRoles);
                    room.trigger('blocked-roles-change', room.blockedRoles);
                });
                room.isBlockedRole = function (role) {
                    console.log('isBlockedRole', role, !!room.blockedRoles[role]);
                    return !!room.blockedRoles[role];
                };
                room.toggleBlocking = function (role) {
                    if (room.isBlockedRole(role)) {
                        room.metaRef.child('blocked-roles').child(role).remove();
                    } else {
                        room.metaRef.child('blocked-roles').child(role).set(true);
                    }
                };
                room.canChat = function () {
                    if(room.destroyed) {
                        return false;
                    }
                    console.log('CANCHAT', room.blockedRoles, room.getRole(self.user.uid));
                    return !room.blockedRoles[room.getRole(self.user.uid)];
                };
                room.usersRef.on('value', room.usersUpdated);

                if (room.type == 'public') {
                    self.openGroupChat(room);
                } else {
                    partner = room.creator.uid === self.user.uid ? room.target : room.creator;
                    self.openPrivateChat(room, partner);
                }
            });
            this.fireChat.on('room-invite', function (invite) {
                if (invite.fromUserId in self.privateChats) {
                    console.log('opening new chatty for', invite.fromUserId);
                }
                self.fireChat.acceptInvite(invite.id);
            });
            this.fireChat.on('message-add', function(roomId, message) {
                if ((roomId in self.rooms) && !message.deleted) {
                    self.rooms[roomId].addMessage(message);
                }
            });
            this.fireChat._roomRef.on('value', function (snapshot) {
                var groupChats =  _.where(_.values(snapshot.val()), {type: 'public'});
                self.renderGroupChats(groupChats);
            });
            this.fireChat.on('room-exit', function (roomId) {
                self.forgetRoom(roomId);
            });
        },
        forgetRoom: function (roomId) {
            var room, self = this;
            if (roomId in self.rooms) {
                console.log('exiting room', roomId);
                room = self.rooms[roomId];
                if(!room.public) {
                    delete self.privateChats[room.partner.uid];
                    console.log('delete private chat');
                }
                delete self.rooms[roomId];
            }
        },
        openPrivateChat: function (room, partner) {
            var self = this, chat;
            chat = new PrivateChatView({
                room: room,
                chat: this,
                partner: partner
            });
            self.rooms[room.id] = chat;
            self.privateChats[partner.uid] = room.id;
            chat.on('closed', function () {
                self.fireChat.leaveRoom(room.id);
            });
            chat.render();
            console.log('rendered', room, 'with', partner.uid);
        },
        openGroupChat: function (room) {
            var self = this, chat;
            chat = new GroupChatView({
                room: room,
                chat: this
            });
            self.rooms[room.id] = chat;
            chat.on('closed', function () {
                self.fireChat.leaveRoom(room.id);
            });
            chat.render();
        },
        render: function () {
            this.$wrap.html(Mustache.template('chatbar').render());
            this.$supportPersonnel = this.$wrap.find('.support-personnel');
            this.$groupChats = this.$wrap.find('.group-chats');
            this.$tabs = this.$wrap.find('.nkchat-tabs');
            this.$tabContent = this.$wrap.find('.nkchat-tab-content');
            this.$groupChatsButton = this.$wrap.find('.group-chats-button');
        },
        renderGroupChats: function (groupChats) {
            this.$groupChats.html(
                Mustache.template('group-chats').render({
                    rooms: groupChats,
                    creation: this.canCreateGroupChat()
                })
            );
            this.$groupChatsButton.toggle(
                this.canCreateGroupChat() || (groupChats.length > 0)
            );
        },
        canCreateGroupChat: function () {
            return this.user.role >= ROLE_ORGANIZATION_ADMIN;
        },
        canModerate: function () {
            return this.user.role >= ROLE_MODERATOR;
        },
        refreshOnlineModerators: function () {
            var self = this;
            this.onlineModsRef.on('value', function (snapshot) {
                var mods = snapshot.val() || [];
                mods = _.map(mods, function (u) {
                    return _.values(u)[0];
                });
                self.$supportPersonnel.find('.moderator').remove();
                self.$supportPersonnel.find('.moderators-header').after(
                    Mustache.template('moderators-online').render({'moderators': mods})
                );
            });
        },
        refreshOnlineOrganizationAdmins: function () {
            var self = this;
            this.onlineOrgAdminsRef.on('value', function (snapshot) {
                var orgs = snapshot.val() || [], admins = [];
                _.each(orgs, function (users, organizationId) {
                    users = _.map(users, function (u) {
                        return _.values(u)[0];
                    });
                    admins.push.apply(admins, users);
                });
            });
        },
        login: function () {
            this.fireBase.auth(this.authToken, this.authCallback);
        },
        authCallback: function (err, user) {
            var self = this;
            if (err) {
                console.log('firebase login failed', err, user);
            } else {
                this.fireChat = new Firechat(
                    this.fireBase,
                    this.opts
                );
                console.log('authed as', user.auth);
                this.fireChat.setUser(
                    user.auth.uid,
                    user.auth.name,
                    user.auth.role,
                    user.auth.organizations,
                    function () {
                        self.user = user.auth;
                        self.bindDataEvents();
                        self.fireChat.resumeSession();
                        $(window.document).trigger('nkchat-initialized', {nkChat: self});
                    }
                );
            }
        },
        bindOrganizationAdminStatus: function (organizationId, username, cb) {
            var username = '@' + username;
            console.log('bind to ', organizationId, username.toLowerCase());
            var ref = this.onlineOrgAdminsRef.child(organizationId).child(username.toLowerCase());
            ref.once('value', function (snapshot) {
                cb(!!snapshot.val());
                // add 8 sec lag to keep onliners online thru page switches
                cb = _.debounce(cb, 8000);
                ref.on('value', function (snapshot) {
                    cb(!!snapshot.val())
                })
            });
        },
        createPrivateRoom: function (partner) {
            var self = this,
                opts = {name: 'Private Chat', type: 'private', target: partner};
            this.fireChat.createRoom(opts, function (roomId) {
                console.log('created', partner.uid, "->", roomId, 'entering...');
                self.fireChat.enterRoom(roomId);
            });
        },
        createGroupChat: function (name) {
            var self = this,
                opts = {name: name, type: 'public'};
            this.fireChat.createRoom(opts, function (roomId) {
                console.log('created', roomId, 'entering...');
                self.fireChat.enterRoom(roomId);
            });
        },
        openSupportChatByUsername: function (username) {
            console.log('request support from', username);
            var self = this;
            this.usersOnlineRef.child('@' + username.toLowerCase()).once('value', function (snapshot) {
                var val = snapshot.val(), target;
                if (val) {
                    target = _.values(val)[0];
                    if(target.id.indexOf('moderator-') === 0 || target.id.indexOf('organization-') === 0) {
                        if (target.id in self.privateChats) {
                            self.rooms[self.privateChats[target.id]].open(true);
                        } else {
                            self.createPrivateRoom({'uid': target.id, 'name': target.name});
                        }
                    } else {
                        console.log(username, 'is not a support person');
                    }
                } else {
                    console.log(username, 'is not online');
                }
            });

        }
    };

    window.NkChat = NkChat;

})(window, _, jQuery, Firechat, Mustache, Backbone, window.console);
