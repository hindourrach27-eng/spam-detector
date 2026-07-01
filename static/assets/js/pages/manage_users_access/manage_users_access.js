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
                url: '/delete_access_user',
                data: {arr:[id]},
                success: function (response) {
                // var data=JSON.parse(response)
                    console.log(response);
                    hide = document.getElementById("aler-remove").style.display = 'block';
			setTimeout(function(){
			   window.location.reload(1);
				hide = document.getElementById("aler-remove").style.display = 'none';
						   // window.location.reload(1);
			}, 3000);

                }
            });
		/* Act on the event */
		$(this).parents('.search-items').remove();
	});
}


function addContact() {
$("#btn-add").click(function() {
		var $_user = document.getElementById('users_selected');
		var $_role = document.getElementById('in-role');

            $.ajax({
                type: 'POST',
                url: '/add_accessToUser',
                data: {arr: [$_user.value, $_role.value]},
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
		var getParentItem = $(this).parents('.search-items');
		var getModal = $('#updateContactModal');
		$('#updateContactModal').modal('show');
 			$(this).parents("tr");
            var $_id = $(this).attr("id");
				var input_name=document.getElementById("user")
		console.log($_id)
		input_name.value=$_id.split("**")[1]
		var user_id=$_id.split("**")[0];

		$("#btn-edit").click(function(){
		var $_role = document.getElementById('up-role');
   			$.ajax({
                type: 'POST',
                url: '/update_access_user',
                data: {arr: [user_id ,$_role.value]},
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






