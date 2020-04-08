function filterGlobal () {
    $('#example').DataTable().search(
        $('#global_filter').val(),
        $('#global_regex').prop('checked'),
        $('#global_smart').prop('checked')
    ).draw();
}

function filterColumn ( i ) {
    $('#example').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
}

$(document).ready(function (){
    var punchlist_user = document.getElementById( "datatable" ).getAttribute( "punchlist_user" );
    var path = '../static/js/datatable_';
    var extension = '.ajax';
    var ajax_file = path + punchlist_user + extension;

    var col_layout = [
              {
                "render": function ( data, type, row, meta ) {
                  return '<a href="/punchlist/edit/'+row.id+'" target="_blank">Edit</a>'; }
              },
                { "data": "id" },
                { "data": "status" },
                { "data": "discipline" },
                { "data": "description" },
                { "data": "comments" },
                { "data": "date_orig" },
                { "data": "due_date" },
                { "data": "author" },
                { "data": "closure" },
                { "data": "supplier" },
                { "data": "system" },
                { "data": "floor" },
                { "data": "phase" },
                { "data": "cat" },
                { "data": "building" }
            ];

    $('#example').DataTable({
        ajax: ajax_file,
        columns: col_layout,
        dom: 'Rlfrtip'
        });

    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
        var export_data = $('#example').DataTable().rows( {search:'applied'} ).data();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
        var export_data = $('#example').DataTable().rows( {search:'applied'} ).data();
    } );

});

