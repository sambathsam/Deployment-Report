$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-report").modal("show");
      },
      success: function (data) {
        $("#modal-report .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#report-table tbody").html(data.html_report_list);
          $("#modal-report").modal("hide");
        }
        else {
          $("#modal-report .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  // Create report
  $(".js-create-report").click(loadForm);
  $("#modal-report").on("submit", ".js-report-create-form", saveForm);

  // Update report
  $("#report-table").on("click", ".js-update-report", loadForm);
  $("#modal-report").on("submit", ".js-report-update-form", saveForm);
  
  //Delete report
  $("#report-table").on("click", ".js-delete-report", loadForm);
  $("#modal-report").on("submit", ".js-report-delete-form", saveForm);

});