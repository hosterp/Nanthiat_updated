// openerp.hiworth_project_management = function(instance) {
//     var _t = instance.web._t,
//         _lt = instance.web._lt;
//     var QWeb = instance.web.qweb;

// instance.web.WebClient = instance.web.WebClient.extend({
//     get_notif_box: function(me) {
//             return $(me).closest(".ui-notify-message-style");
//         },

//     check_hiworth_project_management: function () {
//         var self = this;

        
//         this.rpc('/hiworth_project_management/notify')
//         .done(
//             function (notifications) {
//                 _.each(notifications,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } // prevent displaying same notifications
//                         notif.title = QWeb.render('popup_title', {'assigned_to':notif.assigned_to,'user':notif.user,'title': notif.title, 'id': notif.id});
//                         notif.message = QWeb.render('popup_footer');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
//                         // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
//                         // var notification = new Notification(notif.title);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack", {'notif_id': notif.id});
//                         });
//                     }); // #TODO check original module
//                 });
//             }
//         )
//         this.rpc('/hiworth_project_management/notify_task_message')
//         .done(
//             function (notifications_task) {
//                 _.each(notifications_task,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p10_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } // prevent displaying same notifications
//                         notif.title = QWeb.render('popup_title10', {'assigned_to':notif.assigned_to,'user':notif.user,'title': notif.title, 'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
//                         // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
//                         // var notification = new Notification(notif.title);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_task_message", {'notif_id': notif.id});
//                         });
//                     }); // #TODO check original module
//                 });
//             }
//         )
//         this.rpc('/hiworth_project_management/notify_msg')
//         .done(
//             function (notifications_msg) {
//                 _.each(notifications_msg,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p1_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } // prevent displaying same notifications
//                         notif.title = QWeb.render('popup_title_msg', {'user':notif.user,'title': notif.title,'message_type': notif.message_type, 'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
//                         // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
//                         // var notification = new Notification(notif.title);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_msg", {'notif_id': notif.id});
//                         });
//                     }); // #TODO check original module
//                 });
//             }
//         )
//         this.rpc('/hiworth_project_management/notify_msg_cust')
//         .done(
//             function (notifications_msg_cust) {
//                 _.each(notifications_msg_cust,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p1_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } // prevent displaying same notifications
//                         notif.title = QWeb.render('popup_title_msg', {'user':notif.user,'title': notif.title,'message_type': notif.message_type, 'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
//                         // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
//                         // var notification = new Notification(notif.title);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_msg_cust", {'notif_id': notif.id});
//                         });
//                     }); // #TODO check original module
//                 });
//             }
//         )
//         this.rpc('/hiworth_project_management/notify_msg_adm')
//         .done(
//             function (notifications_msg_adm) {
//                 _.each(notifications_msg_adm,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p2_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } // prevent displaying same notifications
//                         notif.title = QWeb.render('popup_title_adm', {'user':notif.user,'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
//                         // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
//                         // var notification = new Notification(notif.title);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_msg", {'notif_id': notif.id});
//                         });
//                     }); // #TODO check original module
//                 });
//             }
//         )
        // this.rpc('/hiworth_project_management/notify_task_adm')
        // .done(
        //     function (notifications_task_adm) {
        //         _.each(notifications_task_adm,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p45_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } // prevent displaying same notifications
        //                 notif.title = QWeb.render('popup_title_task_adm', {'user':notif.user,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
        //                 // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
        //                 // var notification = new Notification(notif.title);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_ack_task", {'notif_id': notif.id});
        //                 });
        //             }); // #TODO check original module
        //         });
        //     }
        // )

        // this.rpc('/hiworth_project_management/notify_site')
        // .done(
        //     function (notifications_msg) {
        //         _.each(notifications_msg,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p5_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
                        // } // prevent displaying same notifications
                        // notif.title = QWeb.render('popup_title_site', {'visit_by':notif.visit_by,'user':notif.user,'title': notif.title, 'id': notif.id});
                        // notif.message = QWeb.render('popup_footer_msg');
                        // notif_elem = self.do_notify(notif.title, notif.message, true);
                        // var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: notif.id1});
                        // var notification = new Notification(notif.title,{body:notif.title,icon:image_url,dir:'auto'});
                        // var notification = new Notification(notif.title);
                        // notif_elem.element.find(".link2showed").on('click',function() {
                        // self.get_notif_box(this).find('.ui-notify-close').trigger("click");
                        // self.rpc("/hiworth_project_management/notify_ack_site", {'notif_id': notif.id});
                        // });
                    // }); // #TODO check original module
                // });
            // }
        // )



        // this.rpc('/hiworth_project_management/notify_general')
        // .done(
        //     function (notifications_msg) {
        //         _.each(notifications_msg,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p6_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_general', {'logged':notif.logged,'user':notif.user,'title': notif.title, 'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_ack_general", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )
        // this.rpc('/hiworth_project_management/notify_file_cust')
        // .done(
        //     function (notifications_filemsg) {
        //         _.each(notifications_filemsg,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p70_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_file_cust', {'logged_user':notif.logged_user,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_file_cust_ack", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )
        // this.rpc('/hiworth_project_management/notify_work_report_admin')
        // .done(
        //     function (notifications_workreport_admin) {
        //         _.each(notifications_workreport_admin,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p71_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_workreport_admin', {'to_id':notif.to_id,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_work_report_admin_ack", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )
        // this.rpc('/hiworth_project_management/notify_work_report_manager')
        // .done(
        //     function (notifications_workreport_manager) {
        //         _.each(notifications_workreport_manager,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p72_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_workreport_man', {'manager':notif.manager,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_work_report_man_ack", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )
        // this.rpc('/hiworth_project_management/notify_work_report_sent')
        // .done(
        //     function (notifications_workreport_sent) {
        //         _.each(notifications_workreport_sent,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p73_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_workreport_sent', {'sent_report':notif.sent_report,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_work_report_sent_ack", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )
        // this.rpc('/hiworth_project_management/notify_leave')
        // .done(
        //     function (notifications_leave) {
        //         _.each(notifications_leave,  function(notif) {
        //             setTimeout(function() {
        //                 if ($('.ui-notify-message p#p74_id').filter(function () {
        //                     return $(this).html() == notif.id;
        //                 }).length) {
        //                     return;
        //                 } 
        //                 notif.title = QWeb.render('popup_title_leave', {'admin':notif.admin,'employee_id':notif.employee_id,'id': notif.id});
        //                 notif.message = QWeb.render('popup_footer_msg');
        //                 notif_elem = self.do_notify(notif.title, notif.message, true);
        //                 notif_elem.element.find(".link2showed").on('click',function() {
        //                 self.get_notif_box(this).find('.ui-notify-close').trigger("click");
        //                 self.rpc("/hiworth_project_management/notify_leave_ack", {'notif_id': notif.id});
        //                 });
        //             }); 
        //         });
        //     }
        // )


//         this.rpc('/hiworth_project_management/notify_approved_msg')
//         .done(
//             function (notify_approved_msg) {
//                 _.each(notify_approved_msg,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p115_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } 
//                         notif.title = QWeb.render('popup_title_notif_man', {'title':notif.title,'req_nofify':notif.req_nofify,'user':notif.user,'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_approved_msg", {'notif_id': notif.id});
//                         });
//                     }); 
//                 });
//             }
//         )

//         this.rpc('/hiworth_project_management/notify_update_task_admin')
//         .done(
//             function (notify_update_task_admin) {
//                 _.each(notify_update_task_admin,  function(notif) {
//                     setTimeout(function() {
//                         if ($('.ui-notify-message p#p200_id').filter(function () {
//                             return $(this).html() == notif.id;
//                         }).length) {
//                             return;
//                         } 
//                         notif.title = QWeb.render('popup_title_notif_event', {'reviewer_id':notif.reviewer_id,'title':notif.title,'user_id':notif.user_id,'id': notif.id});
//                         notif.message = QWeb.render('popup_footer_msg');
//                         notif_elem = self.do_notify(notif.title, notif.message, true);
//                         notif_elem.element.find(".link2showed").on('click',function() {
//                         self.get_notif_box(this).find('.ui-notify-close').trigger("click");
//                         self.rpc("/hiworth_project_management/notify_ack_update_task", {'notif_id': notif.id});
//                         });
//                     }); 
//                 });
//             }
//         )
//         .fail(function (err, ev) {
//             if (err.code === -32098) {
//                 // Prevent the CrashManager to display an error
//                 // in case of an xhr error not due to a server error
//                 ev.preventDefault();
//             }
//         });
//     },

//     start: function (parent) {
//         var self = this;
//         self._super(parent);
//         // console.log('qweqwe');
//         $(document).ready(function () {
//             self.check_hiworth_project_management();
//             setInterval( function() {
//                 // console.log('Working!');
//                 self.check_hiworth_project_management();
//             }, 10 * 1000);
//         });
//     },

// })};
