$(document).ready(function () {
    // Get CSRF token
    function get_csrf () {
        return document.cookie.match(/csrftoken=([\w]+)[;]?/)[1]
    }
    $('.content').on('input paste', '#id_share_name', function () {
        search_input = $(this)
        $.ajax({
            url: `${window.location.origin}/quotes/list/search/`,
            type: 'GET',
            data: {
                name: search_input.val(),
                downloaded: true
            },
            success: function (response) {
                $('.share_name').remove()
                search_input.css('border-radius', '11px')
                if (!response.results.length && search_input.val() !== '') {
                    search_input.css('border-radius', '11px 11px 0 0')
                    search_input.after('<div class="share_name">No matches</div>')
                } else if (response.results.length) {
                    search_input.css('border-radius', '11px 11px 0 0')
                    search_input.after('<select class="share_name"></select>')
                    response.results.forEach(function (element, index) {
                        $('.share_name').append(
                            `<option value="${element.symbol}">${element.symbol} | ${element.name}</option>`
                        )
                    })
                }
            },
            error: function (response) {
                alert('error')
            }
        })
    })

    $('.button_div').on('click', function (){
        form = $(this).parent().children('.form')
        if (form.css('display') === 'none') {
            $(this).parent().children('.form').show(300)
        } else {
            $(this).parent().children('.form').hide(300)
        }
    })

    $('.content').on('click', '.submit_button', function () {
        $(this).parent().trigger('submit')
    })

    $('.content').on('submit', '.portfolio_create_form form', function (event) {
        event.preventDefault()
        let data = new FormData($(this)[0])
        $.ajax({
            url: `${window.location.origin}/quotes/portfolio/create/`,
            type: 'POST',
            processData: false,
            contentType: false,
            data: data,
            success: function (response) {

            },
            error: function (response) {
                $('form').replaceWith(response.responseJSON.form)
            }
        })
    })
    // Change portfolio main data (show change form)
    $('.content').on('click', '#portfolio_config', function() {
        const name = $('.portfolio_name').text()
        const balance = $('.portfolio_balance').text().match(/Balance: ([\w.]+)/)[1]
        $(this).replaceWith(`
            <span class="config_button" id="portfolio_cancel">Cancel</span>
            <span class="config_button" id="portfolio_confirm">Confirm</span>
        `)
        $('#portfolio_delete').remove()
        $('.portfolio_name').replaceWith(`
            <h1 class="portfolio_name">
                <input type="text"  id="new_name" placeholder="Portfolio name"
                 class="${name}" value="${name}">
            </h1>
        `)
        $('.portfolio_balance').replaceWith(`
            <div class="portfolio_balance">
                <input type="text"  id="new_balance" placeholder="Portfolio balance"
                 class="${balance}" value="${balance}">
            </div>      
        `)
    })
    // Cancel portfolio main data changing
    $('.content').on('click', '#portfolio_cancel', function() {
        $(this).replaceWith(`
            <span class="config_button" id="portfolio_config">Configure</span>
            <span class="config_button" id="portfolio_delete">Delete</span>
        `)
        $('#portfolio_confirm').remove()
        $('.portfolio_name').replaceWith(`
            <h1 class="portfolio_name">${$('#new_name').attr('class')}</h1>
        `)
        $('.portfolio_balance').replaceWith(`
            <div class="portfolio_balance">Balance: ${$('#new_balance').attr('class')} $</div>      
        `)
        $('.form_error').remove()
    })
    // Confirm portfolio main data changing
    $('.content').on('click', '#portfolio_confirm', function() {
        if ($('#new_name').val() === $('#new_name').attr('class') &&
            $('#new_balance').val() === $('#new_balance').attr('class')) {
            $('#portfolio_cancel').trigger('click')
            return
        } else {
            $.ajax({
                url: `${window.location.origin}/quotes/portfolio/update/${window.location.href.match(/\/quotes\/portfolio\/detail\/([\w]+)/)[1]}`,
                type: 'PATCH',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {
                    name: $('#new_name').val(),
                    balance: $('#new_balance').val()
                },
                success: function (response) {
                    $('.portfolio_name').replaceWith(`
                        <h1 class="portfolio_name">${$('#new_name').val()}</h1>
                    `)
                    $('.portfolio_balance').replaceWith(`
                        <div class="portfolio_balance">Balance: ${$('#new_balance').val()} $</div>
                    `)
                    $('.form_error').remove()
                    $('#portfolio_confirm').replaceWith(`
                        <span class="config_button" id="portfolio_config">Configure</span>
                        <span class="config_button" id="portfolio_delete">Delete</span>
                    `)
                    $('#portfolio_cancel').remove()
                },
                error: function (response) {
                    $('.form_error').remove()
                    let errors = response.responseJSON.errors
                    let name_errors = ''
                    for (i in errors.name) {
                        name_errors += `<li>${errors.name[i].message}</li>`
                    }
                    $('#new_name').before(
                        `<div class="form_error"><ul class="errorlist">${name_errors}</ul></div>`
                    )
                    let balance_errors = ''
                    for (i in errors.balance) {
                        balance_errors += `<li>${errors.balance[i].message}</li>`
                    }
                    $('#new_balance').before(
                        `<div class="form_error"><ul class="errorlist">${balance_errors}</ul></div>`
                    )
                }
            })
        }
    })
    // Cancel portfolio main data changing
    $('.content').on('click', '#portfolio_delete', function() {
        if (confirm('Are you sure you want to delete the portfolio?')) {
            $.ajax({
                url: `${window.location.origin}/quotes/portfolio/delete/${window.location.href.match(/\/quotes\/portfolio\/detail\/([\w]+)/)[1]}`,
                type: 'DELETE',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {},
                success: function (response) {
                    window.location.href = `${window.location.origin}/quotes/portfolio/list`
                },
                error: function (response) {
                    alert('Error')
                }
            })
        }
    })
    /*Sort submenu realization*/
    $('#sort').on('click', function () {
        sub_menu = $('.sub_menu')
        if (sub_menu.css('visibility') === 'visible') {
            $(this).text('Sort by ▼')
            sub_menu.css('visibility', 'hidden');
            sub_menu.css('opacity', '0');
            sub_menu.css('transform', 'translate(0, 20px)');
        } else {
            $(this).text('Sort by ▲')
            sub_menu.css('visibility', 'visible');
            sub_menu.css('opacity', '1');
            sub_menu.css('transform', 'translate(0, 0)');
        }
    })
    // Quote click
    $('.content').on('click', '.quotes_details, .quotes_details_downloaded', function() {
        const quote = $(this)
        $.ajax({
                url: `${window.location.origin}/quotes/detail/${quote.attr('id')}`,
                type: 'GET',
                data: {
                    symbol: quote.find('ul .quotes_symbol').text(),
                    name: quote.find('ul .quotes_name').text()
                },
                success: function (response) {
                    window.location.href = `${window.location.origin}/quotes/detail/${quote.attr('id')}`
                },
                error: function (response) {
                    alert('Error')
                }
        })
    })
    function quotes_colors() {
        $('.quotes_change, .quotes_changep').each((index, element) => {
            if ($(element).text().startsWith('-')) {
                $(element).css('color', 'rgb(171, 92, 92)')
            } else if ($(element).text().startsWith('+')) {
                $(element).css('color', 'rgb(92, 171, 50)')
            } else if ($(element).text() !== 'Change $' && $(element).text() !== 'Change %') {
                $(element).css('color', 'rgb(219,168,0)')
            }
        })
    }
    quotes_colors()
    // Quotes list search
    $('.content').on('input paste', '#quotes_search', function () {
        $.ajax({
            url: `${window.location.origin}/quotes/list/search/`,
            type: 'GET',
            data: {
                search: $(this).val(),
                page: window.location.href.match(/\/\?page=([\w]+)/) ?
                    window.location.href.match(/\/\?page=([\w]+)/)[1] : 1
            },
            async: false,
            success: function (response) {
                if (response.quotes_html) {
                    $('.portfolios_list').replaceWith(`
                        <div class="portfolios_list">
                            <div class="quotes_list_header">
                                <ul>
                                    <li class="quotes_symbol">Symbol</li>
                                    <li class="quotes_name">Name</li>
                                    <li class="quotes_price">Price $</li>
                                    <li class="quotes_change">Change $</li>
                                    <li class="quotes_changep">Change %</li>
                                    <li class="quotes_volume">Volume</li>
                                </ul>
                            </div>
                            ${response.quotes_html}
                        </div>
                    `)
                } else {
                    $('.portfolios_list').replaceWith(`
                        <div class="portfolios_list">No matching quotes</div>
                    `)
                }
                if (response.pagination_html) {
                    $('.portfolios_list').append(`${response.pagination_html}`)
                }
                quotes_colors()
            },
            error: function (response) {
                alert('error')
            }
        })
    })
    $('.content').on('click', '.portfolio_shares_edit_menu', function () {
        let menu = $(this).children('ul')
        if (menu.css('display') !== 'none') {
            menu.fadeOut(200)
        } else {
            menu.fadeIn(200)
        }
    })
    // Show share search form
    $('.content').on('click', '#portfolio_add_shares', function () {
        if ($('#id_share_name').css('display') === 'none') {
            $('#id_share_name, #portfolio_confirm_add').show(200)
        } else {
            $('#id_share_name, #portfolio_confirm_add').hide(200)
            $('#id_share_name').css('border-radius', '11px')
            $('.share_name').remove()
        }
    })
    $('.content').on('click', '#portfolio_confirm_add', function () {
        $.ajax({
                url: `${window.location.origin}/quotes/portfolio/share/`,
                type: 'PUT',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {
                    symbol: $('.share_name option:selected').val(),
                    slug: window.location.href.match(/\/quotes\/portfolio\/detail\/([\w]+)/)[1],
                    type: 'add'
                },
                success: function (response) {
                    $('span:contains("No shares yet")').remove()
                    $('#id_share_name').remove()
                    $('#portfolio_confirm_add').remove()
                    $('.share_name').remove()
                    $('#portfolio_add_shares').after(
                        `<div>${response.share.symbol} | ${response.share.name}</div>`
                    )
                },
                error: function (response) {

                }
            })
    })
    // Show change shares amount input
    $('.content').on('click', '#portfolio_shares_amount_change', function () {
        let amount_node = $(this).parent().parent().parent().children('.shares_amount')
        const amount = parseInt(amount_node.text())
        amount_node.text('')
        amount_node.append(`<input type="text" maxlength="5" placeholder="Amount" 
        class="shares_input" id="${amount}">
        <ul>
            <li id="cancel_shares_amount_change">Cancel</li>
            <li id="confirm_shares_amount_change">Confirm</li>
        </ul>
        `)
        $('.shares_input').val(amount)
    })
    // Change shares amount cancel button click
    $('.content').on('click', '#cancel_shares_amount_change', function () {
        $(this).parent().parent().text(`${$('.shares_input').attr('id')}`)
    })
    // Change shares amount confirm button click
    $('.content').on('click', '#confirm_shares_amount_change', function () {
        let amount = $(this).parent().parent().children('.shares_input').val()
        if (parseInt(amount) === NaN) {
            $('#cancel_shares_amount_change').trigger('click')
            return
        } else {
            amount = Math.abs(parseInt(amount))
            if (amount === $(this).parent().parent().children('.shares_input').attr('id') || amount === 0) {
                $('#cancel_shares_amount_change').trigger('click')
                return
            }
        }
        let button = $(this)
        $.ajax({
                url: `${window.location.origin}/quotes/portfolio/share/`,
                type: 'PUT',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {
                    symbol: $(this).parent().parent().parent().children('.share_origin_symbol').text(),
                    slug: window.location.href.match(/\/quotes\/portfolio\/detail\/([\w]+)/)[1],
                    amount: amount,
                    type: 'change_amount'
                },
                success: function (response) {
                    button.parent().parent().parent().children('.shares_amount').text(amount)
                },
                error: function (response) {}
            })
    })
    // Delete shares click
    $('.content').on('click', '#portfolio_shares_delete', function () {
        if (confirm('Are you sure you want to delete the share?')) {
            let button = $(this)
            $.ajax({
                url: `${window.location.origin}/quotes/portfolio/share/`,
                type: 'PUT',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {
                    symbol: $(this).parent().parent().parent().children('.share_origin_symbol').text(),
                    slug: window.location.href.match(/\/quotes\/portfolio\/detail\/([\w]+)/)[1],
                    type: 'delete'
                },
                success: function (response) {
                    button.parent().parent().parent().remove()
                    if (!$('.portfolio_share').length) {
                        $('.portfolio_shares_header').remove()
                        $('.portfolio_shares').append('<span>No shares yet</span>')
                    }
                },
                error: function (response) {}
            })
        }
    })
    //
    // Analysis
    //
    // Step 1: choosing portfolio
    $('.content').on('change', '#id_portfolio', function() {
        if ($(this).val()) {
            $.ajax({
                url: `${window.location.origin}/analysis/form/`,
                type: 'GET',
                data: {
                    step: 'portfolio',
                    slug: $(this).val(),
                },
                success: function (response) {
                    $('.errorlist').remove()
                    $('#id_portfolio').after(`
                        <select id="id_time_interval_start" name="time_interval_start"></select>
                    `)
                    response.dates.forEach(
                        (date) => {
                            $('#id_time_interval_start').append(`
                                <option value="${date}">${date}</option>
                            `)
                        }
                    )
                },
                error: function (response) {
                    $('#id_portfolio').before(`
                        <ul class="errorlist">
                            <li>${response.responseJSON.error_message}</li>
                        </ul>
                    `)
                    $('#id_time_interval_start, #id_time_interval_end, #strategy_name').remove()
                }
            })
        } else {
            $('#id_time_interval_start, #id_time_interval_end, #strategy_name').remove()
        }
    })
    // Step 2: choosing the analysis interval start
    $('.content').on('change', '#id_time_interval_start', function() {
        $('#id_time_interval_end').remove()
        $(this).after(`
            <select id="id_time_interval_end" name="time_interval_end"></select>
        `)
        $('#id_time_interval_start option').slice(4).each((index, option) => {
            $('#id_time_interval_end').append(option)
        })
    })
    // Step 3: choosing the analysis interval end
    $('.content').on('change', '#id_time_interval_end', function() {
        $.ajax({
            url: `${window.location.origin}/analysis/form/`,
            type: 'GET',
            data: {
                step: 'strategies',
            },
            success: function (response) {
                $('#id_time_interval_end').after(`
                    <select id="id_strategy" name="strategy"></select>
                `)
                $('#id_strategy_name').append(`
                    <option>Choose the strategy</option>
                `)
                response.strategies.forEach((strategy) => {
                    $('#id_strategy_name').append(`
                        <option value="${strategy.slug}">${strategy.name}</option>
                    `)
                })
            },
            error: function (response) {}
        })
    })
    // Step 4: choosing the strategy to analyse
    $('.content').on('change', '#id_strategy', function() {
        $(this).after(`<div class="button_div" id="analysis_button">Analyse</div>`)
    })
    // Step 5: analysis
    $('.content').on('click', '#analysis_button', function() {
        $(this).parent().trigger('submit')
        // let data = new FormData($(this)[0])
        // $.ajax({
        //         url: `${window.location.origin}/analysis/form/`,
        //         type: 'POST',
        //         processData: false,
        //         contentType: false,
        //         data: {
        //
        //         },
        //         success: function (response) {
        //
        //         },
        //         error: function (response) {
        //         }
        //     })
    })
})
