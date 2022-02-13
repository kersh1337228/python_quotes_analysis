$(document).ready(function () {
    // Get CSRF token
    function get_csrf () {
        return document.cookie.match(/csrftoken=([\w]+)[;]?/)[1]
    }
    // Parsing form selection data on form select
    $('select').on('change', function () {
        $.ajax({
            url: `${window.location.origin}/analysis/form/`,
            type: 'GET',
            data: {
                share_name: $(this).val(),
                step: $(this).attr('id')
            },
            success: function (response) {

            },
            error: function (response) {
                alert('error')
            }
        })
    })

    $('#id_share_name').on('input paste', function () {
        search_input = $(this)
        $.ajax({
            url: `${window.location.origin}/analysis/form/`,
            type: 'GET',
            data: {
                name: search_input.val(),
                step: search_input.attr('id')
            },
            success: function (response) {
                $('.share_name').remove()
                search_input.css('border-radius', '11px')
                if (!response.results.length && search_input.val() !== '') {
                    search_input.css('border-radius', '11px 11px 0 0')
                    $('.main_menu > form').append('<div class="share_name">No matches</div>')
                } else if (response.results.length) {
                    search_input.css('border-radius', '11px 11px 0 0')
                    $('.main_menu > form').append('<select class="share_name"></select>')
                    $('.main_menu > form')
                    response.results.forEach(function (element, index) {
                        console.log(element)
                        $('.share_name').append(`<option value="${element.toLowerCase()}">${element}</option>`)
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

    $('.content').on('submit', 'form', function (event) {
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
    $('.content').on('click', '.quotes_details', function() {
        const slug = $(this).attr('id')
        $.ajax({
                url: `${window.location.origin}/quotes/quotes/detail/${slug}`,
                type: 'GET',
                headers: {'X-CSRFTOKEN': get_csrf()},
                data: {},
                success: function (response) {
                    // window.location.href = `${window.location.origin}/quotes/portfolio/list`
                },
                error: function (response) {
                    alert('Error')
                }
        })
    })
    for (i in $('.quotes_change')) {
        let change = $($('.quotes_change')[i])
        if (change.text().startsWith('-')) {
            change.css('color', 'red')
        } else if (change.text().startsWith('+')) {
            change.css('color', 'green')
        } else if (change.text() !== 'Change $') {
            change.css('color', 'yellow')
        }
    }
    for (i in $('.quotes_changep')) {
        let change = $($('.quotes_changep')[i])
        if (change.text().startsWith('-')) {
            change.css('color', 'red')
        } else if (change.text().startsWith('+')) {
            change.css('color', 'green')
        } else if (change.text() !== 'Change %') {
            change.css('color', 'yellow')
        }
    }
})
