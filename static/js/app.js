document.addEventListener('DOMContentLoaded', function () {
  const tables = document.querySelectorAll('table.datatable');
  if (tables.length && window.jQuery && $.fn.DataTable) {
    tables.forEach(function (table) {
      $(table).DataTable();
    });
  }
  // Future Chart.js logic will go here
});
