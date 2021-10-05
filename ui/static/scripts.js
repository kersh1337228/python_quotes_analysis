/*Script file for minor fixes*/

/*Sort submenu realization*/
if($('#sort')) {
    sort_menu = $('#sort')
    sort_menu.click(()=>{
        sub_menu = $('.sub_menu')[0]
        if (sub_menu.style.visibility === 'visible') {
            sort_menu.text('Sort by ▼')
            sub_menu.style.visibility = 'hidden'
            sub_menu.style.opacity = '0'
            sub_menu.style.transform = 'translate(0, 20px)'
        } else {
            sort_menu.text('Sort by ▲')
            sub_menu.style.visibility = 'visible'
            sub_menu.style.opacity = '1'
            sub_menu.style.transform = 'translate(0, 0)'
        }
    })
}