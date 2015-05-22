<!-- Pagination frontend logic -->
$(document).ready(function() {
    
    $('.pagination a').click(function(event){
        event.preventDefault();
        //$.get("https://projects.propublica.org/nonprofits/api/v1/organizations/'", function(data, status){
        //    alert("Data: " + data + "\nStatus: " + status);
        var pageNo = $(this).html();

        if (pageNo === '«') {
        	pageNo = parseInt($('.active a').html()) - 1;
        } else if (pageNo === '»') {
        	pageNo = parseInt($('.active a').html()) + 1;
        };

        $.post('/',
            {search: $('#search_value').val(), page: pageNo},
            function(data, status) {
                $('body').html(data);
            });
    });
    
    $(window).resize(function() {
        console.log($(window).height());
        console.log($('body').height());
        $('#home_p').css( 'min-height', $(window).height() - 188 );
    }).resize();
});