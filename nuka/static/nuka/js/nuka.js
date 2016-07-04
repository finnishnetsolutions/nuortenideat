/*global nkChat*/

$(function () {

    "use strict";

    $(document).on('click', '.disabled', function (e) {
        e.preventDefault();
    });

    $(document).on('nkchat-initialized', function (e, data) {
        $('.org-admin-online-status').each(function () {
            var self = $(this);
            data.nkChat.bindOrganizationAdminStatus(
                self.attr('data-organization-id'),
                self.attr('data-username'),
                function (isOnline) {
                    self.text(isOnline ? 'Online' : 'Offline')
                        .toggleClass('online', isOnline);
                }
            );
            self.click(_.debounce(function (e) {
                if(self.hasClass('online')) {
                    data.nkChat.openSupportChatByUsername(
                        self.attr('data-username')
                    );
                }
            }, 1000, true)).click(function (e) {
                e.preventDefault(); // preventDefault even if rate-limit applied
            });
        })
    });

    $(document).on('click', '.object-moderation-reasons .show-more', function (e) {
        e.preventDefault();
        $(this).parents('.object-moderation-reasons').first().addClass('show-all');
    });

    $(".btn-group-input").find("input").focus(function() {
        $(this).parent().addClass("buttonselect-label-focus");
    }).blur(function() {
        $(this).parent().removeClass("buttonselect-label-focus");
    });

    $(document).on('click', '.disable-after-press', function() {
       $(this).addClass('disabled');
    });
});