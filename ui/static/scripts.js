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