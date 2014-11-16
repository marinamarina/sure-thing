$(document).ready(function () {
    $('.nav-tabs li').click(function (e) {
        //TODO: showing an active tab does not work
        //e.preventDefault()
        $(this).addClass('active')
    })
})