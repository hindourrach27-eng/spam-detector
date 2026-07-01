$(function() {

function editEntities() {
	$(document).on('click', '.update_entity_span', function() {
    // $('.update_entity_span').on('click', function(event) {
	        $(this).parents("tr");
            var $_id = $(this).attr("id").split('__');
            var id_entity=$_id[0]
            var chef_prod_id_old=$_id[1]
            var $_rh_id=$_id[2]
            console.log("id+++++++++++++++++")
            console.log($_id)
            console.log("+++++++++++++++++")
            var currentRow = $(this).closest("tr");
            var col1 = currentRow.find("td:eq(1)").text();
            var col2 = currentRow.find("td:eq(2)").text();
            var col3 = currentRow.find("td:eq(3)").text();
            var col4 = currentRow.find("td:eq(4)").text();
            col1=col1.replace(/^\s+|\s+$/g, '')
            col2=col2.replace(/^\s+|\s+$/g, '')
            col3=col3.replace(/^\s+|\s+$/g, '')
            col4=col4.replace(/^\s+|\s+$/g, '')
            // console.log("row+++++++++++++++++")
            // console.log(col1)
            // console.log(col2)
            // console.log(col3)
            // console.log(col4)
            // console.log("input +++++++++++++++++")

            document.getElementById("entity_name_update").value = col1;
		    // document.getElementById("chef_prod_update").value =col3;
		    document.getElementById("date_creation_update").value =getCurrentDate(new Date(col2));
		    // document.getElementById("respo_rh_update").value =col4;
		    // element.value = col3;
         $("#chef_prod_update option[value='"+chef_prod_id_old+"']").remove();
            //$("#entity_update_team").val(2).remove();
            $('#chef_prod_update').append(`<option value="`+chef_prod_id_old+`" selected>`+col3+`</option>`);

             $("#respo_rh_update option[value='"+$_rh_id+"']").remove();
            //$("#entity_update_team").val(2).remove();
            $('#respo_rh_update').append(`<option value="`+$_rh_id+`" selected>`+col4+`</option>`);

		// $("#update_entity_btn").click(function(){
         $("#update_entity_btn").off('click').on('click', function(event){
            var $chef_prod_update = document.getElementById('chef_prod_update').value;
            var $respo_rh_update = document.getElementById('respo_rh_update').value;
            var $date_creation_update = document.getElementById('date_creation_update').value;
            var $entity_name_update = document.getElementById('entity_name_update').value;
            console.log($chef_prod_update)
            console.log($respo_rh_update)
            console.log($date_creation_update)
            console.log($entity_name_update)
   			$.ajax({
                type: 'POST',
                url: '/update_entity',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'name':$entity_name_update,"chef_prod_id_new":$chef_prod_update,"date":$date_creation_update,"respo_rh":$respo_rh_update,"id_entity":id_entity,'chef_prod_id_old':chef_prod_id_old},
                success: function (response) {
                     $("#myModal-update-entity").modal('hide');
			        $("#toast_update").show()
                    setTimeout(function(){
                     $("#toast_update").hide()
                    }, 2000);
                    console.log("nbr ex");
                display_entities()
                }
            });


		});
	})
}
function editTeams() {
	$(document).on('click', '.update_team', function() {
    // $('.update_entity_span').on('click', function(event) {
	        $(this).parents("tr");
            var $_id = $(this).attr("id").split('__');
            var $_id_team=$_id[0]
            var $_tl_id_old=$_id[1]
            var $_entity_id=$_id[2]

            var currentRow = $(this).closest("tr");
            var col2 = currentRow.find("td:eq(1)").text();
            var col3 = currentRow.find("td:eq(2)").text();
            var col4 = currentRow.find("td:eq(3)").text();
            var col5 = currentRow.find("td:eq(4)").text();

            col2=col2.replace(/^\s+|\s+$/g, '')
            col3=col3.replace(/^\s+|\s+$/g, '')
            col4=col4.replace(/^\s+|\s+$/g, '')
            col5=col5.replace(/^\s+|\s+$/g, '')

            document.getElementById("team_name_update").value = col2;

            $("#entity_update_team option[value='"+$_entity_id+"']").remove();
            //$("#entity_update_team").val(2).remove();
            $('#entity_update_team').append(`<option value="`+$_entity_id+`" selected>`+col5+`</option>`);
		    document.getElementById("team_date_creation_update").value =getCurrentDate(new Date(col4));
		    // document.getElementById("respo_rh_update").value =col4;
		    $("#tl_update option[value='"+$_tl_id_old+"']").remove();
            //$("#entity_update_team").val(2).remove();
            $('#tl_update').append(`<option value="`+$_tl_id_old+`" selected>`+col3+`</option>`);

		// $("#update_entity_btn").click(function(){
         $("#update_team_btn").off('click').on('click', function(event){
             console.log("***************************")
            var $team_name_update= document.getElementById('team_name_update').value;
            var $team_date_creation_update = document.getElementById('team_date_creation_update').value;
            var $tl_new_id = document.getElementById('tl_update').value;
            var $entity_id = document.getElementById('entity_update_team').value;
            console.log($team_date_creation_update)
            console.log($team_name_update)
   			$.ajax({
                type: 'POST',
                url: '/update_team',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'name':$team_name_update,"tl_id_new":$tl_new_id,"date":$team_date_creation_update,"id_team":$_id_team,'tl_id_old':$_tl_id_old,'entity_id':$entity_id},
                success: function (response) {
                     $("#myModal-update-team").modal('hide');
			        $("#toast_update").show()
                    setTimeout(function(){
                     $("#toast_update").hide()
                    }, 2000);
                    console.log("nbr ex");
                display_teams()
                }
            });


		});
	})
}
function editEntity_chef_prod() {
	$(document).on('click', '.update_entity_chef_prod', function() {
	        $(this).parents("tr");
            var $_id = $(this).attr("id").split('__');
            var id_entity=$_id[0]
            var chef_prod_id_old=$_id[1]

         $("#change_entity_chef_prod_btn").off('click').on('click', function(event){
            var $chef_prod_new = document.getElementById('change_entity_chef_prod').value;
            var $chef_prod_date_affectation = document.getElementById('chef_prod_date_affectation').value;

   			$.ajax({
                type: 'POST',
                url: '/update_entity_chef_prod',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'id_entity':id_entity,"chef_prod_id_new":$chef_prod_new,'chef_prod_id_old':chef_prod_id_old,'chef_prod_date_affectation':$chef_prod_date_affectation},
                success: function (response) {
                     $("#modal_change_entity_chef_prod").modal('hide');
			        $("#toast_update").show()
                    setTimeout(function(){
                     $("#toast_update").hide()
                    }, 2000);
                    console.log("nbr ex");
                display_entities()
                }
            });


		});
	})
}

function change_team_tl() {
	$(document).on('click', '.update_team_tl', function() {
	        $(this).parents("tr");
            var $_id = $(this).attr("id").split('__');
            var id_team=$_id[0]
            var tl_id_old=$_id[1]
            var currentRow = $(this).closest("tr");
            var col2 = currentRow.find("td:eq(2)").text();
            col2=col2.replace(/^\s+|\s+$/g, '')
        console.log(col2)
           $("#change_team_tl option[value='"+tl_id_old+"']").remove();
            $('#change_team_tl').append(`<option value="`+tl_id_old+`" selected>`+col2+`</option>`);

         $("#change_team_tl_btn").off('click').on('click', function(event){


            var $tl_new = document.getElementById('change_team_tl').value;
            var $date = document.getElementById('tl_date_affectation').value;

   			$.ajax({
                type: 'POST',
                url: '/change_team_tl',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'id_team':id_team,"tl_id_old":tl_id_old,'tl_new':$tl_new,'date':$date},
                success: function (response) {
                     $("#modal_change_team_tl").modal('hide');
			        $("#toast_update").show()
                    setTimeout(function(){
                     $("#toast_update").hide()
                    }, 2000);
                    console.log("nbr ex");
                display_teams()
                }
            });


		});
	})
}

function draw_table_thead(table) {
    table.append("<tr><th>Nom d'entite</th><th>Date de création</th>\<th>chef de production</th><th>Responsable RH</th><th></th></tr>")
}

function draw_table_entities_tbody(value,table,index) {

    table.append("<tr class='font-weight-bold'>" +
        "<td><span class='display_entity_teams' id=\""+ value['id']+"\"> <i class=\"ti-plus\" id=\"shhow_hide_icon"+value['id']+"\"></i></span></td>" +
        "<td>" + value['name'] + "</td>" +
        "<td>" + value['date_creation'] + "</td>" +
        "<td>" + value['full_name_chef_prod'] + "</td>" +
        "<td>" + value['responsible_rh_full_name'] + "</td>" +
        "<td>" +
        "<span class='update_entity_span'   id='" + value['id']+"__"+value['chef_prod_id']+"__"+value['rh_id']+"' data-toggle=\"modal\" data-target=\"#myModal-update-entity\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Edit entity \"> <i class=\"ti-pencil-alt fa-lg\" style='color: #2F55D5 ;'></i></span>" +
        "<span class='update_entity_chef_prod'   id='" + value['id']+"__"+value['chef_prod_id']+ "' data-toggle=\"modal\" data-target=\"#modal_change_entity_chef_prod\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"change prod manager\" style='margin-left: 5px;'> <i class=\"ti-pencil-alt fa-lg\" style='color: #2F55D5 ;'></i></span></td>" +


        "</tr>");
    }
function draw_table2(value,table) {
    table.row.add($("<tr><td>" + value['name'] + "</td><td>" + value['date_creation'] + "</td><td>" + value['full_name_chef_prod'] + "</td><td>" + value['responsible_rh_full_name'] + "</td> <td><span  class=\"update_entity\" id='" + value['id']+ "' data-toggle=\"modal\" data-target=\"#myModal-update-entity\"> <i class=\"fas fa-edit\"></i></span></td></tr>")).draw();
    }

function draw_table_entities_user(value,table) {
    var col=""
    var entities=value['entities_list']
    $.each(entities,function(index,value2) {
        col=col+" <button class=\"btn btn-light\">" +
            "<span class = \"vertical\" style=\"margin-right: 5px;\"></span>"+value2['entity_name']+
            "<a type=\"button\" class=\"btn btn-light delete_entity_user\" id='"+value2['entity_id']+'__'+value2['user_id']+"'>\n" +
            "<i class=\"fa fa-times fa-xs\" ></i></a><a type=\"button\" class=\"btn btn-light update_entity_user\" id='"+value2['entity_id']+'__'+value2['user_id']+"' data-toggle=\"modal\" data-target=\"#centermodal\"><i class=\"far fa-edit\"></i></a></button>"
    })
    table.append("<tr>" +
        "<td>" + value['user_name'] + "</td>" +
        "<td>" + col + "</td>" +
        "</tr>");
    }
function draw_table_teams_tbody(value,table,index) {
        table.append("<tr class='font-weight-bold'>" +
        "<td><span class='display_teams_tl' id=\""+ value['team_id']+"\"> <i class=\"ti-plus\" id=\"shhow_hide_icon_team_tl"+value['team_id']+"\"></i></span></td>" +
        "<td>" + value['team_name'] + "</td>" +
        "<td>" + value['tl'] + "</td>" +
        "<td>" + value['date_creation'] + "</td>" +
        "<td>" + value['entity_name'] + "</td>" +
        "<td>" +
        "<span class='update_team'   id='" + value['team_id']+"__"+value['tl_id']+"__"+value['entity_id']+"' data-toggle=\"modal\" data-target=\"#myModal-update-team\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Edit team \"> <i class=\"ti-pencil-alt fa-lg\" style='color: #5466B8 ; '></i></span>" +
        "<span class='update_team_tl'   id='" + value['team_id']+"__"+value['tl_id']+ "' data-toggle=\"modal\" data-target=\"#modal_change_team_tl\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"change Team leader\" style='margin-left: 5px;'> <i class=\"ti-pencil-alt fa-lg\" style='color: #1A53F0'></i></span>" +
        "<span class='delete_team'   id='" + value['team_id']+"' data-toggle=\"modal\"  data-toggle=\"tooltip\" data-placement=\"top\" title=\"Delete team\" style='margin-left: 5px;'> <i class=\"ti-trash fa-lg\" style='color: #C70039;'></i></span>" +
            "</td>" +
       "</tr>");
    }

function draw_table_teams_mailer(value,table) {
    var col=""
    var entities=value['teams_list']
    $.each(entities,function(index,value2) {
        col=col+" <button class=\"btn btn-light\">" +
            "<span class = \"vertical\" style=\"margin-right: 5px;\"></span> "+value2['entity_name']+" : "+value2['team_name']+
            "<a type=\"button\" class=\"btn btn-light delete_team_mailer_btn\" id='"+value2['team_id']+'__'+value2['mailer_id']+"'>\n" +
            "<i class=\"fa fa-times fa-xs\" ></i></a><a type=\"button\" class=\"btn btn-light update_team_mailer\" id='"+value2['team_id']+'__'+value2['mailer_id']+"' data-toggle=\"modal\" data-target=\"#update_mailer_team\"><i class=\"far fa-edit\"></i></a></button>"
    })
    table.append("<tr>" +
        "<td width=\"50\"><span class='display_teams_mailer' id=\""+ value['mailer_id']+"\"> <i class=\"ti-plus\" id=\"show_hide_icon_team_mailer"+value['mailer_id']+"\"></i></span></td>" +
        "<td width=\"200\">" + value['mailer_name'] + "</td>" +
        "<td>" + col + "</td>" +
             "</tr>");
    }

function display_entities() {

            //     table1.destroy();
// $("#entities_table").dataTable().fnDestroy()

            $.ajax({
                type: 'POST',
                url: '/get_entities',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#entities_table")){
                        $('#entities_table').DataTable().destroy();
                        $('#entities_table tbody').html("");
                    }

                     var table_tbody =  $("#entities_table tbody");
                     // var table_thead =  $("#entities_table thead");
                    // table.empty();
                    // table.clear();
                    // console.log(response)
                    // $('#entities_table').dataTable().fnClearTable();
                    // draw_table_tbody(table_thead)
                    $.each(response,function(index,value) {
                        draw_table_entities_tbody(value,table_tbody,index)

                    })



                    $("#entities_table").DataTable()
                    // if ( $.fn.dataTable.isDataTable( '#entities_table' ) ) {
                    //     $("#entities_table").DataTable({
                    //     "scrollY": "300px",
                    //     "scrollCollapse": true,
                    //     "paging": false,
                    //      // "destroy": true
                    //     // resonsive:true
                    //     });
                    //     }
                    //     else {
                    //   $("#entities_table").DataTable({
                    //                         "scrollY": "300px",
                    //                         "scrollCollapse": true,
                    //                         "paging": false,
                    //                          // "destroy": true
                    //                         // resonsive:true
                    //                         });
                    //         }



                }

            });
}

function display_entities_user() {
    $.ajax({
                type: 'POST',
                url: '/get_entities_user',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#entities_users_table")){
                                $('#entities_users_table').DataTable().destroy();
                                $('#entities_users_table tbody').html("");
                            }

                     var table_tbody =  $("#entities_users_table tbody");

                    $.each(response,function(index,value) {
                        draw_table_entities_user(value,table_tbody)

                    })
                    $("#entities_users_table").DataTable()
                }

            });
}

function display_teams() {
            $.ajax({
                type: 'POST',
                url: '/get_teams',
                success: function (response) {
                    if($.fn.DataTable.isDataTable("#teams_table")){
                        $('#teams_table').DataTable().destroy();
                        $('#teams_table tbody').html("");
                    }
                     var table_tbody =  $("#teams_table tbody");
                    $.each(response,function(index,value) {
                        draw_table_teams_tbody(value,table_tbody,index)

                    })
                    $("#teams_table").DataTable()
                }
            });
}

function display_teams_mailer() {
    $.ajax({
                type: 'POST',
                url: '/get_all_teams_mailers',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#teams_mailer_table")){
                                $('#teams_mailer_table').DataTable().destroy();
                                $('#teams_mailer_table tbody').html("");
                            }

                     var table_tbody =  $("#teams_mailer_table tbody");

                    $.each(response,function(index,value) {
                        draw_table_teams_mailer(value,table_tbody)

                    })
                    $("#teams_mailer_table").DataTable()
                }

            });
}


function delete_entitie_user(entity_id,user_id){
     $.ajax({
                type: 'POST',
                url: '/delete_entitie_user',
                data:{'entity_id':entity_id,'user_id':user_id},
                success: function (response) {
                // var data=JSON.parse(response)
                    $("#toast_msg_delete").show()
                    setTimeout(function(){
			        $("#toast_msg_delete").hide()
			        }, 2000);
                display_entities_user()
                }
            });
}

function update_entitie_user(entity_id_new,entity_id_old,user_id,date){
     $.ajax({
                type: 'POST',
                url: '/update_entitie_user',
                data:{'entity_id_old':entity_id_old,'entity_id_new':entity_id_new,'user_id':user_id,'date':date},
                success: function (response) {
                // var data=JSON.parse(response)
                    $("#toast_update").show()
                    setTimeout(function(){
			        $("#toast_update").hide()
			        }, 2000);
                display_entities_user()
                }
            });
}

function delete_team_mailer_fun(team_id,mailer_id){
    console.log("****************************************")
     $.ajax({
                type: 'POST',
                url: '/delete_team_mailer',
                data:{'team_id':team_id,'mailer_id':mailer_id},
                success: function (response) {
                // var data=JSON.parse(response)
                    $("#toast_msg_delete").show()
                    setTimeout(function(){
			        $("#toast_msg_delete").hide()
			        }, 2000);
                display_teams_mailer()
                }
            });
}

function update_team_mailer(team_id_new,team_id_old,mailer_id,date){
     $.ajax({
                type: 'POST',
                url: '/update_team_mailer',
                data:{'team_id_old':team_id_old,'team_id_new':team_id_new,'mailer_id':mailer_id,"date":date},
                success: function (response) {
                // var data=JSON.parse(response)
                    $("#update_mailer_team").modal('hide')
                    $("#toast_update").show()
                    setTimeout(function(){
			        $("#toast_update").hide()
			        }, 2000);
                display_teams_mailer()
                }
            });
}

function getCurrentDate(t) {
  const date = ('0' + t.getDate()).slice(-2);
  const month = ('0' + (t.getMonth() + 1)).slice(-2);
  const year = t.getFullYear();
  return `${year}-${month}-${date}`;
}

$('#add_entity').click(function(){
var name=document.getElementById('entity_name_input').value;
var id_chef_prod=document.getElementById('chef_prod_input').value;
var date=document.getElementById('date_creation_input').value;
var respo_rh=document.getElementById('respo_rh_input').value;
      $.ajax({
                type: 'POST',
                url: '/add_entity',
                data:{arr:[name,id_chef_prod,date,respo_rh]},
                success: function (response) {
                // var data=JSON.parse(response)
                $("#toast_msg").show()
                    setTimeout(function(){
			   $("#toast_msg").hide()
               //                      document.getElementById("alert").style.display = 'none';

			}, 2000);

                   document.getElementById('entity_name_input').value="";
                   document.getElementById('date_creation_input').value="";
                   document.getElementById('respo_rh_input').value="";
                    $('#add_entity_form_div').hide();
                    $('#show_add_entity_btn').show();
                   display_entities()

                }
            });
      display_entities()

 });

$('#add_team').click(function(){
var team_name=document.getElementById('team_name').value;
var tl=document.getElementById('tl_add_team').value;
var entity=document.getElementById('entity_add_team').value;
var team_date=document.getElementById('team_date').value;
      $.ajax({
                type: 'POST',
                url: '/add_team',
                data:{"team_name":team_name,"tl":tl,"entity":entity,"team_date":team_date},
                success: function (response) {
                // var data=JSON.parse(response)
                $("#toast_msg").show()
                    setTimeout(function(){
			   $("#toast_msg").hide()
               //                      document.getElementById("alert").style.display = 'none';

			}, 2000);

                   document.getElementById('entity_name_input').value="";
                   document.getElementById('date_creation_input').value="";
                   document.getElementById('respo_rh_input').value="";
                    $('#add_team_form_div').hide();
                    $('#show_add_team_btn').show();
                   display_teams()

                }
            });

 });


$('#add_entity_user').click(function(){
var entities_users = $('#entities_users_add').val();
var users_entity = $('#users_entity_add').val();
var date = $('#entities_users_add_date').val();

console.log(entities_users)
console.log(users_entity)
      $.ajax({
                type: 'POST',
                url: '/add_entity_user',
                data:{'entities_users':entities_users,'users_entity':users_entity,'date':date},
                success: function (response) {
                // var data=JSON.parse(response)
                $("#toast_msg").show()
                    setTimeout(function(){
			   $("#toast_msg").hide()
               //                      document.getElementById("alert").style.display = 'none';

			}, 2000);
                    $('#entities_users_add').val(null).trigger("change");

                    display_entities_user()
                }
            });


 });

$('#add_team_mailer').click(function(){
var teams = $('#team_mailers_add').val();
var mailers = $('#mailers_add').val();
var date =  $('#date_mailer_team_input').val();

console.log(teams)
console.log(mailers)
console.log(date)
      $.ajax({
                type: 'POST',
                url: '/add_team_mailer',
                data:{'teams':teams,'mailers':mailers,'date':date},
                success: function (response) {
                // var data=JSON.parse(response)
                $("#toast_msg").show()
                    setTimeout(function(){
			   $("#toast_msg").hide()
               //                      document.getElementById("alert").style.display = 'none';

			}, 2000);
                    $('#entities_users_add').val(null).trigger("change");

                    display_teams_mailer();
                     $('#add_team_mailer_form_div').hide();
                     $('#show_add_team_mailer_btn').show();
                }
            });


 });



$('#show_add_entity_btn').click(function(){
    $('#add_entity_form_div').show();
    $('#show_add_entity_btn').hide();

});
$('#show_add_team_btn').click(function(){
    $('#add_team_form_div').show();
    $('#show_add_team_btn').hide();

});
$('#show_add_entity_user_btn').click(function(){
    $('#add_entityToUser_form_div').show();
    $('#show_add_entity_user_btn').hide();

});
$('#show_add_team_mailer_btn').click(function(){
    $('#add_team_mailer_form_div').show();
    $('#show_add_team_mailer_btn').hide();

});

 // $('.delete_entity_user').click(function(){
$(document).on('click', '.delete_entity_user', function() {
     var $_id=$(this).attr('id');
     $_id=$_id.split("__");
     var entity_id = $_id[0]
     var user_id = $_id[1]
    delete_entitie_user(entity_id,user_id)
  });

$(document).on('click', '.update_entity_user', function() {
     var $_id=$(this).attr('id');
     $_id=$_id.split("__");
     var entity_id_old = $_id[0]
     var user_id = $_id[1]
                console.log(".................1...............")

      $('#update_entity_for_user_btn').off('click').on('click', function(event){
          console.log("................................")
          $('#centermodal').modal('hide')
          var entity_id_new=document.getElementById("entity_user_update").value;
          var date=document.getElementById("date_entity_user_update").value;
            update_entitie_user(entity_id_new,entity_id_old,user_id,date);
       });
  });

$(document).on('click', '.display_entity_teams', function(){
    var $_id = $(this).attr("id");
    var clicks = $(this).data('clicks');
    var row = $(this).parents("tr");
    var rowIndex = row[0].rowIndex;
    console.log(clicks)
    $(this).data("clicks",!clicks)
    if (clicks){
        console.log("even")
        console.log(rowIndex)
    $('#shhow_hide_icon'+$_id).removeClass('ti-minus');
  $('#shhow_hide_icon'+$_id).addClass('ti-plus');
  $('#entities_table > tbody > tr').eq(rowIndex).remove();


}else {
        console.log("odd")
 $('#shhow_hide_icon'+$_id).removeClass('ti-plus');
    $('#shhow_hide_icon'+$_id).addClass('ti-minus');
            $.ajax({
                            type: 'POST',
                            url: '/get_entitie_teams',
                            data: {'entity_id':$_id},
                            success: function (response) {

                                              var teams ="" ;
                                        if (response.length === 0){
                                                    teams="<p class='font-weight-bold'> &nbsp;&nbsp; &nbsp;&nbsp; No data available</p>"
                                                   console.log(teams)                     }
                                        else{

                                        $.each(response,function (index,value) {
                                           teams=teams+"<div class=\"col-md-3\">" +
                                            "                    <div class=\"card border\" style='padding: 10px 10px 10px 10px;'>" +

                                            "                            <h5 class=\"mb-0\" style='color: #FFA5B4; '>"+value['team_name']+"  "+value['team_id']+"</h5>" +
                                            "                        <div class=\"card-body\">\n" +
                                            "                          <div class='row font-weight-bold' >  Team leader :&nbsp;&nbsp;  "+value['tl']+"</div>" +
                                            "                           <div class='row font-weight-bold'>   Date : &nbsp;&nbsp; "+value['date_creation']+"</div>" +
                                            "                        </div>" +
                                            "                    </div>" +
                                            "                </div>";
                                        })
                                        }
                                    $('#entities_table > tbody > tr').eq(rowIndex-1).after('<tr ><td>Teams</td><td colspan="5"><div class=\"row\">'+teams+'</div></td></tr>');


                            }
                        });

}
});

$(document).on('click', '.display_teams_tl', function(){
    var $_id = $(this).attr("id");
    var clicks = $(this).data('clicks');
    var row = $(this).parents("tr");
    var rowIndex = row[0].rowIndex;
    console.log(clicks)
    $(this).data("clicks",!clicks)
    if (clicks){
        console.log("even")
        console.log(rowIndex)
    $('#shhow_hide_icon_team_tl'+$_id).removeClass('ti-minus');
  $('#shhow_hide_icon_team_tl'+$_id).addClass('ti-plus');
  $('#teams_table > tbody > tr').eq(rowIndex).remove();


}else {
        console.log("odd")
        $('#shhow_hide_icon_team_tl'+$_id).removeClass('ti-plus');
        $('#shhow_hide_icon_team_tl'+$_id).addClass('ti-minus');
        $.ajax({
                            type: 'POST',
                            url: '/get_tls_team',
                            data: {'team_id':$_id},
                            success: function (response) {
console.log(response)
                                              var teams ="" ;
                                        if (response.length === 0){
                                                    teams="<p class='font-weight-bold'> &nbsp;&nbsp; &nbsp;&nbsp; No data available</p>"
                                                   console.log(teams)                     }
                                        else{

                                        $.each(response,function (index,value) {
                                           teams=teams+"<div class=\"col-md-3\">" +
                                            "                    <div class=\"card border\" style='padding: 10px 10px 10px 10px;'>" +
                                            "                            <h5 class=\"mb-0\" style='color: #FFA5B4; '>"+value['tl_name']+"</h5>" +
                                            "                        <div class=\"card-body\">\n" +
                                            "                          <div class='row font-weight-bold' >  Date in  :&nbsp;&nbsp;  "+value['date_in']+" Date out  :&nbsp;&nbsp;  "+value['date_out']+"</div>" +
                                           "                          <div class='row font-weight-bold' >  State :&nbsp;&nbsp;  "+value['state']+"</div>" +
                                            "                        </div>" +
                                            "                    </div>" +
                                            "                </div>";
                                        })
                                        }
                                    $('#teams_table > tbody > tr').eq(rowIndex-1).after('<tr ><td>Teams</td><td colspan="5"><div class=\"row\">'+teams+'</div></td></tr>');


                            }
                        });

}
});

$(document).on('click', '.display_teams_mailer', function(){
    var $_id = $(this).attr("id");
    var clicks = $(this).data('clicks');
    var row = $(this).parents("tr");
    var rowIndex = row[0].rowIndex;
    console.log(clicks)
    $(this).data("clicks",!clicks)
    if (clicks){
        console.log("even")
        console.log(rowIndex)
    $('#show_hide_icon_team_mailer'+$_id).removeClass('ti-minus');
  $('#show_hide_icon_team_mailer'+$_id).addClass('ti-plus');
  $('#teams_mailer_table > tbody > tr').eq(rowIndex).remove();


}else {
        console.log("odd")
        $('#show_hide_icon_team_mailer'+$_id).removeClass('ti-plus');
        $('#show_hide_icon_team_mailer'+$_id).addClass('ti-minus');
        $.ajax({
                            type: 'POST',
                            url: '/get_mailer_teams',
                            data: {'mailer_id':$_id},
                            success: function (response) {
                                    console.log(response)
                                        var teams ="" ;
                                        if (response.length === 0){
                                                    teams="<p class='font-weight-bold'> &nbsp;&nbsp; &nbsp;&nbsp; No data available</p>"
                                                   console.log(teams)                     }
                                        else{

                                        $.each(response,function (index,value) {
                                           teams=teams+"<div class=\"col-md-3\">" +
                                            "                    <div class=\"card border\" style='padding: 10px 10px 10px 10px;'>" +
                                            "                            <h5 class=\"mb-0\" style='color: #FFA5B4; '>"+value['entity_name']+" : "+value['team_name']+"</h5>" +
                                            "                        <div class=\"card-body\">\n" +
                                            "                          <div class='row font-weight-bold' >  Date in  :&nbsp;&nbsp;  "+value['date_in']+" </div>" +
                                            "                          <div class='row font-weight-bold' >  Date out  :&nbsp;&nbsp;  "+value['date_out']+"</div>" +
                                           "                          <div class='row font-weight-bold' >  State :&nbsp;&nbsp;  "+value['state']+"</div>" +
                                            "                        </div>" +
                                            "                    </div>" +
                                            "                </div>";
                                        })
                                        }
                                    $('#teams_mailer_table > tbody > tr').eq(rowIndex-1).after('<tr ><td>Teams</td><td colspan="2"><div class=\"row\">'+teams+'</div></td></tr>');


                            }
                        });

}
});

$(document).on('click', '.delete_team', function() {
    var $_id_team = $(this).attr("id");
    		$.ajax({
                type: 'POST',
                url: '/delete_team',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'id_team':$_id_team},
                success: function (response) {
                     // $("#myModal-update-team").modal('hide');
			        $("#toast_delete").show()
                    setTimeout(function(){
                     $("#toast_delete").hide()
                    }, 2000);
                    // console.log("nbr ex");
                display_teams()
                }
            });
});

$(document).on('click', '.update_team_mailer', function() {
     var $_id=$(this).attr('id');
     $_id=$_id.split("__");
     var team_id_old = $_id[0]
     var mailer_id = $_id[1]
            var currentRow = $(this).closest("tr");
            var mailer_name = currentRow.find("td:eq(1)").text();
            mailer_name=mailer_name.replace(/^\s+|\s+$/g, '')
    console.log("++++++++++++++++")
    console.log(mailer_name)
            document.getElementById("mailer_name").innerHTML=mailer_name

      $('#update_team_for_mailer_btn').off('click').on('click', function(event){
          console.log("................................")
          $('#team_mailer_update').modal('hide')
          var team_id_new=document.getElementById("team_mailer_update").value;
          var date=document.getElementById("date_team_mailer_update").value;
            update_team_mailer(team_id_new,team_id_old,mailer_id,date);
       });
  });
$(document).on('click', '.delete_team_mailer_btn', function() {
    console.log("++++++++++++++++")
     var $_id=$(this).attr('id');
     $_id=$_id.split("__");
     var team_id = $_id[0]
     var mailer_id = $_id[1]
    delete_team_mailer_fun(team_id,mailer_id)
  });


$('#div-part1').click(function(){
        $('.div-part1').show();
        $('.div-part2').hide();
        $('.div-part3').hide();
        $('.div-part4').hide();
        $('.entities_table').show();

        $(this).addClass('active');
        $('#div-part2').removeClass('active');
        $('#div-part3').removeClass('active');
        $('#div-part4').removeClass('active');
        $("#div-part2").css({ 'background-color' : '', 'color' : '' });
        $("#div-part4").css({ 'background-color' : '', 'color' : '' });


        display_entities();

    });
$('#div-part2').click(function(){
        $('.div-part1').hide();
        $('.div-part2').show();
        $('.div-part3').hide();
        $('.div-part4').hide();
        $('.entities_table').hide();
        // $(this).addClass('active');
        $('#div-part1').removeClass('active');
        $('#div-part3').removeClass('active');
        $('#div-part4').removeClass('active');
        $(this).css({ 'background-color' : '#FFA5B4', 'color' : 'white' });
        $("#div-part4").css({ 'background-color' : '', 'color' : '' });
        display_entities_user();
    });
$('#div-part3').click(function(){
        $('.div-part1').hide();
        $('.div-part2').hide();
        $('.div-part3').show();
        $('.div-part4').hide();
        $('.entities_table').hide();
        $(this).addClass('active');
        $('#div-part2').removeClass('active');
        $('#div-part1').removeClass('active');
        $('#div-part4').removeClass('active');
        $("#div-part2").css({ 'background-color' : '', 'color' : '' });
        $("#div-part4").css({ 'background-color' : '', 'color' : '' });
        display_teams()

    });
$('#div-part4').click(function(){
        $('.div-part1').hide();
        $('.div-part2').hide();
        $('.div-part3').hide();
        $('.div-part4').show();
        $('.entities_table').hide();
        $(this).addClass('active');
        $('#div-part2').removeClass('active');
        $('#div-part3').removeClass('active');
        $('#div-part1').removeClass('active');
        $("#div-part2").css({ 'background-color' : '', 'color' : '' });
         // $(this).css({ 'background-color' : '#FF5733', 'color' : 'white' });
         $(this).css({ 'background-color' : '#FFA5B4', 'color' : 'white' });
         display_teams_mailer()
    });


editEntities();
display_entities();
editEntity_chef_prod();
editTeams();
change_team_tl();
})




