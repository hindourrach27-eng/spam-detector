// $(document).on("click", "#btn-add-contact", function(event) {
// 		$('#addContactModal #btn-add').show();
// 		$('#addContactModal #btn-edit').hide();
// 		$('#addContactModal').modal('show');
// 	})
//
// $(document).on("click", "#btn-add", function () {
// 		var $_team_name = document.getElementById('t-team');
// 		var $_entity = document.getElementById('t-entity');
// 		var $_matricule = document.getElementById('t-matricule');
//
//             $.ajax({
//                 type: 'POST',
//                 url: '/add_team',
//                 data: {arr: [$_team_name.value, $_entity.value,$_matricule.value]},
//                 success: function (response) {
//                     //service.php response
// 					// $( "#users_table" ).load( "user_team_management.html #users_table" );
//                      // window.location.reload();
//                     console.log(response);
//                      // var table = $('#table'+id+' tbody');
//
//
//                 }
//             });
// });

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
                url: '/delete_team',
                data: id,
                success: function (response) {
                // var data=JSON.parse(response)

                    console.log(response);
                    hide = document.getElementById("aler-remove").style.display = 'block';
			setTimeout(function(){
			   // window.location.reload(1);
				hide = document.getElementById("aler-remove").style.display = 'none';
			}, 3000);

                }
            });
		/* Act on the event */
		$(this).parents('.search-items').remove();
	});
}


function addContact() {
$("#btn-add").click(function() {
		var $_team_name = document.getElementById('t-team');
		var $_entity = document.getElementById('t-entity');
		var $_matricule = document.getElementById('t-matricule');

            $.ajax({
                type: 'POST',
                url: '/add_team',
                data: {arr: [$_team_name.value, $_entity.value,$_matricule.value]},
                success: function (response) {
                // var data=JSON.parse(response)
			hide = document.getElementById("alert").style.display = 'block';
                    console.log(response);
			setTimeout(function(){
			   window.location.reload(1);
			}, 5000);

                }
            });
	});
}

function editContact() {
	$('.edit').on('click', function(event) {
		// $('#addContactModal #btn-add').hide();
		// $('#updateContactModal #btn-edit').show();

		// Get Parents
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
		col3=col3.replace(/^\s+|\s+$/g, '')
		 let element = document.getElementById("up-matricule");

		document.getElementById("up-team").value = col1;
		document.getElementById("up-entity").value =col2;
		// element.value = col3;

		$("#btn-edit").click(function(){
			var $_team_name = document.getElementById('up-team');
		var $_entity = document.getElementById('up-entity');
		var $_matricule = document.getElementById('up-matricule');
   			$.ajax({
                type: 'POST',
                url: '/update_team',
                data: {arr: [$_id ,$_team_name.value, $_entity.value,$_matricule.value]},
                success: function (response) {
                // var data=JSON.parse(response)
			hide = document.getElementById("alert-update").style.display = 'block';
                    console.log(response);
			setTimeout(function(){
			   window.location.reload(1);
			}, 3000);

                }
            });

		});
	})
}

// $(".delete-multiple").on("click", function() {
// 		var inboxCheckboxParents = $(".contact-chkbox:checked").parents('.search-items');
// 			inboxCheckboxParents.remove();
// });

deleteContact();
addContact();
editContact();

})






