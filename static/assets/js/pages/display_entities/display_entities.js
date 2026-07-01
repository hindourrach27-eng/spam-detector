$(function() {
function checkall(clickchk, relChkbox) {
		var checker = $('#' + clickchk);
		var multichk = $('.' + relChkbox);
		checker.click(function () {
				multichk.prop('checked', $(this).prop('checked'));
		});
}

	checkall('contact-check-all', 'contact-chkbox');

	$('#input-search').on('keyup', function() {
		var rex = new RegExp($(this).val(), 'i');
			$('.search-table .search-items:not(.header-item)').hide();
			$('.search-table .search-items:not(.header-item)').filter(function() {
					return rex.test($(this).text());
			}).show();
	});

	$('#btn-add-contact').on('click', function(event) {
		$('#addContactModal #btn-add').show();
		$('#addContactModal #btn-edit').hide();
		$('#addContactModal').modal('show');
	})

function deleteContact() {
	$(".delete").on('click', function(event) {
		event.preventDefault();
		            var id = $(this).attr("id");
	$.ajax({
                type: 'POST',
                url: '/delete_entity',
                data: id,
                success: function (response) {
                // var data=JSON.parse(response)

                    console.log(response);
                    	hide = document.getElementById("alert-remove").style.display = 'block';
			setTimeout(function(){
			   // window.location.reload(1);

	hide = document.getElementById("alert-remove").style.display = 'none';
			}, 3000);

                }
            });
		/* Act on the event */
$(this).parents('.search-items').remove();
	});
}


function addContact() {
$("#btn-add").click(function() {
		var $_En_name = document.getElementById('name-Entity');
		var $_date = document.getElementById('Ent-date');

            $.ajax({
                type: 'POST',
                url: '/add_entity',
                data: {arr: [$_En_name.value, $_date.value]},
                success: function (response) {
			hide = document.getElementById("alert").style.display = 'block';
                    console.log(response);
			setTimeout(function(){
			   window.location.reload(1);
			}, 3000);

                }
            });
	});
}

function editContact() {
	$('.edit').on('click', function(event) {

		var getParentItem = $(this).parents('.search-items');
		var getModal = $('#updateContactModal');
		$('#updateContactModal').modal('show');
 			$(this).parents("tr");
            var $_id = $(this).attr("id");
            var currentRow = $(this).closest("tr");
            var col1 = currentRow.find("td:eq(0)").text();
            var col2 = currentRow.find("td:eq(1)").text();
            var col3 = currentRow.find("td:eq(2)").text();


		col1=col1.replace(/^\s+|\s+$/g, '')
		col2=col2.replace(/^\s+|\s+$/g, '')


		document.getElementById("up-name").value = col1;
		document.getElementById("up-date").value =col2;
		// element.value = col3;

		$("#btn-edit").click(function(){
			var $_name = document.getElementById('up-name');
		var $_date = document.getElementById('up-date');
   			$.ajax({
                type: 'POST',
                url: '/update_entity',
                data: {arr: [$_id ,$_name.value, $_date.value]},
                success: function (response) {
                // var data=JSON.parse(response)
			hide = document.getElementById("alert-update").style.display = 'block';
                    console.log(response);
			setTimeout(function(){
			   window.location.reload(1);
			}, 1000);

                }
            });

		});
	})
}

deleteContact();
addContact();
editContact();

})






