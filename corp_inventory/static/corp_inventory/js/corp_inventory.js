/**
 * Corp Inventory JavaScript
 */

(function($) {
    'use strict';

    var CorpInventory = {
        /**
         * Initialize the app
         */
        init: function() {
            this.initSync();
            this.initFilters();
            this.initDataTables();
            this.initModals();
            this.initCorpSearch();
        },

        /**
         * Initialize sync functionality
         */
        initSync: function() {
            $('.btn-sync').on('click', function(e) {
                e.preventDefault();
                var $btn = $(this);
                var corpId = $btn.data('corp-id');
                
                if ($btn.hasClass('disabled')) {
                    return false;
                }
                
                $btn.addClass('disabled');
                $btn.html('<i class="fas fa-sync fa-spin"></i> Syncing...');
                
                $.ajax({
                    url: $btn.attr('href'),
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': CorpInventory.getCookie('csrftoken')
                    },
                    success: function(response) {
                        if (response.status === 'success') {
                            CorpInventory.showMessage('Sync started successfully!', 'success');
                            setTimeout(function() {
                                location.reload();
                            }, 2000);
                        } else {
                            CorpInventory.showMessage(response.message || 'Sync failed', 'danger');
                            $btn.removeClass('disabled');
                            $btn.html('<i class="fas fa-sync"></i> Sync Now');
                        }
                    },
                    error: function() {
                        CorpInventory.showMessage('Error starting sync', 'danger');
                        $btn.removeClass('disabled');
                        $btn.html('<i class="fas fa-sync"></i> Sync Now');
                    }
                });
            });
        },

        /**
         * Initialize filter functionality
         */
        initFilters: function() {
            // Search functionality
            $('#item-search').on('keyup', function() {
                var value = $(this).val().toLowerCase();
                $('.hangar-table tbody tr').filter(function() {
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
                });
            });

            // Division filter
            $('#division-filter').on('change', function() {
                var division = $(this).val();
                if (division === '') {
                    $('.hangar-table tbody tr').show();
                } else {
                    $('.hangar-table tbody tr').each(function() {
                        var rowDivision = $(this).data('division');
                        $(this).toggle(rowDivision == division);
                    });
                }
            });

            // Location filter
            $('#location-filter').on('change', function() {
                var location = $(this).val();
                if (location === '') {
                    $('.hangar-table tbody tr').show();
                } else {
                    $('.hangar-table tbody tr').each(function() {
                        var rowLocation = $(this).data('location');
                        $(this).toggle(rowLocation == location);
                    });
                }
            });

            // Clear filters
            $('#clear-filters').on('click', function() {
                $('#item-search').val('');
                $('#division-filter').val('');
                $('#location-filter').val('');
                $('.hangar-table tbody tr').show();
            });
        },

        /**
         * Initialize DataTables
         */
        initDataTables: function() {
            if ($.fn.DataTable && $('.hangar-table').length) {
                $('.hangar-table').DataTable({
                    order: [[0, 'asc']],
                    pageLength: 50,
                    lengthMenu: [[25, 50, 100, -1], [25, 50, 100, "All"]],
                    responsive: true,
                    dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>rtip'
                });
            }

            if ($.fn.DataTable && $('.transaction-table').length) {
                $('.transaction-table').DataTable({
                    order: [[0, 'desc']],
                    pageLength: 50,
                    lengthMenu: [[25, 50, 100, -1], [25, 50, 100, "All"]],
                    responsive: true
                });
            }
        },

        /**
         * Initialize modals
         */
        initModals: function() {
            // Delete confirmation
            $('.btn-delete-corp').on('click', function(e) {
                e.preventDefault();
                var corpName = $(this).data('corp-name');
                var href = $(this).attr('href');
                
                if (confirm('Are you sure you want to remove tracking for ' + corpName + '? This will delete all stored data.')) {
                    window.location.href = href;
                }
            });

            // Enable/Disable tracking
            $('.btn-toggle-tracking').on('click', function(e) {
                e.preventDefault();
                var $btn = $(this);
                var corpId = $btn.data('corp-id');
                var action = $btn.data('action');
                
                $.ajax({
                    url: '/corp-inventory/manage/toggle/' + corpId + '/',
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': CorpInventory.getCookie('csrftoken')
                    },
                    success: function(response) {
                        if (response.status === 'success') {
                            location.reload();
                        } else {
                            CorpInventory.showMessage(response.message || 'Action failed', 'danger');
                        }
                    },
                    error: function() {
                        CorpInventory.showMessage('Error performing action', 'danger');
                    }
                });
            });
        },

        /**
         * Initialize corporation search (ESI lookup)
         */
        initCorpSearch: function() {
            $('#corp-name-input').on('blur', function() {
                var corpName = $(this).val();
                if (corpName.length < 3) {
                    return;
                }
                
                // You could add ESI corporation lookup here
                // For now, users will enter the corp ID manually
            });
        },

        /**
         * Show message to user
         */
        showMessage: function(message, type) {
            type = type || 'info';
            var alertClass = 'alert-' + type;
            var html = '<div class="alert ' + alertClass + ' alert-dismissible fade in">' +
                      '<button type="button" class="close" data-dismiss="alert">&times;</button>' +
                      message + '</div>';
            
            $('.corp-inventory-wrapper').prepend(html);
            
            setTimeout(function() {
                $('.alert').fadeOut(function() {
                    $(this).remove();
                });
            }, 5000);
        },

        /**
         * Get CSRF cookie
         */
        getCookie: function(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = $.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    // Initialize on document ready
    $(document).ready(function() {
        CorpInventory.init();
    });

})(jQuery);
