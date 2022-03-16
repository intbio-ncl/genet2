function handle_submit_input(id){
    $('#submit_forms').children('div').each(function () {
        $("#" + this.id).not("#"+id).slideUp();
    });
    $("#"+id).slideToggle();
}


$(document).ready(function() {
    if ($('#staticBackdrop').length) {
        $('#staticBackdrop').modal('show');
    }
  });