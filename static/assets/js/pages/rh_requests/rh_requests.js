$(function() {

    get_administrative_request();
$('#div-part1').click(function(){
        $('.div-part1').show();
        $('.div-part2').hide();
        $('.div-part3').hide();
        // $('.div-part4').hide();
        $('.administrative_requests_table').show();

        $(this).addClass('active');
        $('#div-part2').removeClass('active');
        $('#div-part3').removeClass('active');
        // $('#div-part4').removeClass('active');
        $("#div-part2").css({ 'background-color' : '', 'color' : '#34495E' });
        $("#div-part3").css({ 'background-color' : '', 'color' : '#34495E' });
        // $("#div-part4").css({ 'background-color' : '', 'color' : '' });
        $(this).css({ 'background-color' : '#34495E', 'color' : 'white' });

    get_administrative_request();

        // display_entities();

    });
$('#div-part2').click(function(){
        $('.div-part1').hide();
        $('.div-part2').show();
        $('.div-part3').hide();
        // $('.div-part4').hide();
        $('.administrative_requests_table').hide();
        // $(this).addClass('active');
        $('#div-part1').removeClass('active');
        $('#div-part3').removeClass('active');
        // $('#div-part4').removeClass('active');
        $(this).css({ 'background-color' : '#34495E', 'color' : 'white' });
        $("#div-part1").css({ 'background-color' : '', 'color' : '#34495E' });
        $("#div-part3").css({ 'background-color' : '', 'color' : '#34495E' });
        get_recup_leave_requests();
});

$('#div-part3').click(function(){
        $('.div-part1').hide();
        $('.div-part2').hide();
        $('.div-part3').show();
        // $('.div-part4').hide();
        $('.mission_requests_table').hide();
        // $(this).addClass('active');
        $('#div-part1').removeClass('active');
        $('#div-part2').removeClass('active');
        // $('#div-part4').removeClass('active');
        $(this).css({ 'background-color' : '#34495E', 'color' : 'white' });
        $("#div-part1").css({ 'background-color' : '', 'color' : '#34495E' });
        $("#div-part2").css({ 'background-color' : '', 'color' : '#34495E' });
        get_mission_request();
});




function administrative_requests_table(response,table) {
  $.each(response,function(index,value) {
      var state="";
      var buttons="";
      var file_buttons="";

           if (value['request_name'].toLowerCase()==="attestation de salaire" && value['state']==="accepted"){
           file_buttons="" +
              // "<button type=\"button\" class=\"btn btn-secondary\" id=\"\" ><i class=\"ti-settings\"></i>&nbsp;&nbsp;Generate file</button>" +
              "&nbsp;&nbsp;<button type=\"button\" class=\"btn btn-secondary generate_salary_attestation\" data-toggle=\"modal\" data-target=\"#salary_attestationModal\" id=\""+value['id']+"__"+value['user_id']+"\"><i class=\"ti-settings\" ></i><i class=\"ti-download\" ></i></button>";
            buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";


         }
           else if(value['request_name'].toLowerCase()==="attestation de salaire" || value['request_name'].toLowerCase()==="attestation de travail" )
           {
               buttons="&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
                 "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";}
           else if(value['request_name'].toLowerCase()==="attestation de travail" && value['state']==="accepted"){
             file_buttons="" +
              // "<button type=\"button\" class=\"btn btn-secondary\" id=\"\" ><i class=\"ti-settings\"></i>&nbsp;&nbsp;Generate file</button>" +
              "&nbsp;&nbsp;<button type=\"button\" class=\"btn btn-secondary generate_attestation_travail\"  id=\""+value['id']+"__"+value['user_id']+"\"><i class=\"ti-settings\" ></i>&nbsp;&nbsp;<i class=\"ti-download\" ></i></button>";


         }
          else if(value['request_name'].toLowerCase()==="avance sur le salaire"){
             buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }
        else if(value['request_name'].toLowerCase()==="ordre de mission ld"){
             buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }
          else if(value['request_name'].toLowerCase()==="ordre de mission cd"){
             buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }
            else if(value['request_name'].toLowerCase()==="autorisation de sortie"){
             buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }
            else if(value['request_name'].toLowerCase()==="attestation de titularisation"){
                buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         } else if(value['request_name'].toLowerCase()==="bulletins de paie"){
                buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }else if(value['request_name'].toLowerCase()==="domiciliation bancaire"){
                buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_attestation\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

         }
      if (value['progress_state']==='not done') {
         state= '<span class=\"badge badge-warning px-2 py-1\">Not Done</span>';

      }
          else {

          if(value['state']==="accepted"){
             state=state+ '<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success generate_attestation_travail \"  id=\"'+value['id']+'\"><i class="fa fa-check"></i> </span>';

          }
          else if(value['state']==="refused"){
              state=state+ '<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger \"  id=\"'+value['id']+'\"><i class=\"fa fa-times\"></i> </span>'
          }
          // buttons="";
          state=state+'<span class=\"badge badge-success px-2 py-1\">Done</span>' ;
      }


      table.append("<tr class='font-weight-bold'>" +
        "<td>" + value['user_name'] + "</td>" +
        "<td >" + value['request_name'] + "</td>" +
        "<td> " + value['request_date'] + "</td>" +
        "<td> " + value['delivery_date'] + "</td>" +
        "<td>" + state + "</td>" +
        "<td>" + buttons + "</td>" +
        "<td>" + file_buttons + "</td>" +
        "</tr>");
    });
    }





function get_administrative_request() {
    $.ajax({
                type: 'POST',
                url: '/display_rh_administrative_requests_ajax',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#administrative_requests_table")){
                                $('#administrative_requests_table').DataTable().destroy();
                                $('#administrative_requests_table tbody').html("");
                            }

                     var table_tbody =  $("#administrative_requests_table tbody");

                   administrative_requests_table(response,table_tbody)
                    $("#administrative_requests_table").DataTable(
                        { "order": [[ 2, "desc" ]]}
                    )

                }

            });
}

function get_recup_leave_requests() {
    $.ajax({
                type: 'POST',
                url: '/get_recup_leave_requests',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#off_requests_table")){
                                $('#off_requests_table').DataTable().destroy();
                                $('#off_requests_table tbody').html("");
                            }

                     var table_tbody =  $("#off_requests_table tbody");

                   off_requests_table(response,table_tbody)
                    $("#off_requests_table").DataTable( { "order": [[ 2, "desc" ]]})
                }

            });
}

function off_requests_table(response,table) {
  $.each(response,function(index,value) {
      var chef_prod_validation="";
      var team_leader_validation="";
      var buttons="";
      var state="";
      var requests="";
      var span="";
      var request_details=value['request_details'];
       console.log("request_details");
       console.log(request_details);
          $.each(request_details,function(index,value2) {
            if (index===0){
                span=span+
                    "<div class=\"w-100 d-inline-block v-middle pl-2\">" +
                    "                                        <h5 class=\"text-truncate mb-0 text-capitalize\">"+value2['request_name']+"</h5>" +
                    "                                        <span class=\"mail-desc font-12 text-truncate overflow-hidden text-nowrap d-block\">From " +value2['request_date_start']+" to "+value2['request_date_start']+" </span>" +
                    "                                        <span class=\"time  font-12 text-truncate overflow-hidden text-nowrap d-block\">days N°: "+value2['nbr_day']+"</span>" ;
                if (value['chef_prod_validation']==='accepted' && value['tl_validation']==='accepted' ){


                    span=span+"<div class='text-right'><button type=\"button\" class=\"btn generate-off-attestation-btn\" style='background-color: #F1F1E6;color: #34495E;' id='"+value2['request_name']+"__"+value2['request_date_start']+"__"+value2['request_date_end']+"__"+value2['request_time_start']+"__"+value2['request_time_end']+"__"+value['user_id']+"__"+value['id']+"'><i class=\"ti-download\"></i></button></div>"+
                    "                                    </div>";}
            // span=span+"<div><p class='text-capitalize'>"+value2['request_name']+"</p> &nbsp;<div class=\"badge\" style='background-color: #8F789F; color: whitesmoke;'>"+value2['nbr_day']+"</div>"+value2['request_date_start']+" "+value2['request_date_start']+"</div>";
            } else if (index>0){
                    span=span+
                    "<hr><div class=\"w-100 d-inline-block v-middle pl-2\">" +
                    "                                        <h5 class=\"text-truncate mb-0 text-capitalize\">"+value2['request_name']+"</h5>" +
                    "                                        <span class=\"mail-desc font-12 text-truncate overflow-hidden text-nowrap d-block\">From " +value2['request_date_start']+" to "+value2['request_date_start']+" </span>" +
                    "                                        <span class=\"time  font-12 text-truncate overflow-hidden text-nowrap d-block\">days N°: "+value2['nbr_day']+"</span>" ;


                      if (value['chef_prod_validation']==='accepted' && value['tl_validation']==='accepted' ){
                                span=span+"<div class='text-right'><button type=\"button\" class=\"btn generate-off-attestation-btn\" style='background-color: #F1F1E6;color: #34495E;' id='"+value2['request_name']+"__"+value2['request_date_start']+"__"+value2['request_date_end']+"__"+value2['request_time_start']+"__"+value2['request_time_end']+"__"+value['user_id']+"__"+value['id']+"'><i class=\"ti-download\"></i></button></div>"+
                                "                                    </div>";}

            }
         });
      if (value['chef_prod_validation']==='accepted' && value['tl_validation']==='accepted' && value['state']==='done') {
         chef_prod_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';
         team_leader_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';

         state='<span class=\"badge badge-info px-2 py-1\">Done</span>';

      }
      else if (value['chef_prod_validation']==='accepted' && value['tl_validation']==='accepted' && value['state']==='not done') {
         chef_prod_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';
         team_leader_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';
         state='<span class=\"badge badge-warning px-2 py-1\">Not Done</span>';
      }

      else if(value['chef_prod_validation']==='refused' && value['tl_validation']==='refused') {
         chef_prod_validation= '<span class=\"badge badge-danger px-2 py-1\">Refused</span>';
         team_leader_validation= '<span class=\"badge badge-danger px-2 py-1\">Refused</span>';
      }
       else if (value['chef_prod_validation']==='accepted' && value['tl_validation']==='refused') {
         chef_prod_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';
         team_leader_validation= '<span class=\"badge badge-danger px-2 py-1\">Refused</span>';

      }else if(value['chef_prod_validation']==='refused' && value['tl_validation']==='accepted') {
         chef_prod_validation= '<span class=\"badge badge-danger px-2 py-1\">Refused</span>';
         team_leader_validation= '<span class=\"badge badge-success px-2 py-1\">Accepted</span>';
      }
    table.append("<tr class='font-weight-bold'>" +
        "<td class='text-capitalize'>" + value['user_name'] + "</td>" +
        "<td >" + span+ "</td>" +
        "<td >" + value['request_date'] + "</td>" +
        "<td>" + value['request_date_end'] + "</td>" +
        "<td>" + value['request_date_start'] + "</td>" +
        "<td> " + team_leader_validation + "</td>" +
        "<td> " + chef_prod_validation + "</td>" +
        "<td> " + state + "</td>" +
        "</tr>");

    });

    }

administrative_requests_table()
// $(document).on('click', '.upload_request_btn', function() {
//     var $id = $(this).attr('id');
//     $('#upload-file-btn').click(function () {
//
//         console.log("$id")
//         console.log($id)
//         var form_data = new FormData($('#upload-file')[0]);
//         form_data.append('administrative_requests_id', $id);
//         $.ajax({
//             type: 'POST',
//             url: '/upload_administrative_request',
//             data: form_data,
//             contentType: false,
//             cache: false,
//             processData: false,
//             success: function(data) {
//                 console.log('Success!');
//                 administrative_request()
//                 $('#myModal-upload').modal('hide')
//             },
//         });
//     });
// });

$(document).on('click', '.generate_salary_attestation', function() {
    var $id = $(this).attr('id').split("__");
    var id_request=$id[0];
    var user_id=$id[1];
        var currentRow = $(this).closest("tr");
        var user_name = currentRow.find("td:eq(0)").text();
        var request = currentRow.find("td:eq(1)").text();
        user_name=user_name.replace(/^\s+|\s+$/g, '')
        request=request.replace(/^\s+|\s+$/g, '')


    $('#generate-salary_attestation-btn').click(function () {

        console.log("$id")
        console.log($id)
        var salary_input = $('#salary_input').val();
        $.ajax({
            type: 'POST',
            url: '/upload_salary_request',
            data: {'user_name':user_name,'request':request,'request_id':id_request,'user_id':user_id,'salary':salary_input},
            success: function(data) {
                console.log('Success!');
                get_administrative_request()
                $('#salary_attestationModal').modal('hide')
                    window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });
});


$(document).on('click', '.generate_attestation_travail', function() {
    var $id = $(this).attr('id').split("__");
    var id_request=$id[0];
    var user_id=$id[1];
        var currentRow = $(this).closest("tr");
        var user_name = currentRow.find("td:eq(0)").text();
        var request = currentRow.find("td:eq(1)").text();
        user_name=user_name.replace(/^\s+|\s+$/g, '')
        request=request.replace(/^\s+|\s+$/g, '')

        $.ajax({
            type: 'POST',
            url: '/generate_attestation_travail',
            data: {'user_name':user_name,'request':request,'request_id':id_request,'user_id':user_id},
            success: function(data) {
                console.log('Success!');
                get_administrative_request()
                $('#salary_attestationModal').modal('hide')
                    window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });

});




$(document).on('click', '.generate-off-attestation-btn', function() {
    var $id = $(this).attr('id').split("__");

    var request_name=$id[0];
    var request_date_start=$id[1];
    var request_date_end=$id[2];
    var request_time_start=$id[3];
    var request_time_end=$id[4];
    var user_id=$id[5];
    var request_id=$id[6];

        $.ajax({
            type: 'POST',
            url: '/generate_off_attestation',
            data: {'request_id':request_id,'request_name':request_name,'request_date_start':request_date_start,'request_date_end':request_date_end,'user_id':user_id,'request_time_start':request_time_start,'request_time_end':request_time_end},
            success: function(data) {
                console.log('Success!');
                get_recup_leave_requests()
                // $('#salary_attestationModal').modal('hide')
                    window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });

$(document).on('click', '.accept_attestation', function() {
    var $id = $(this).attr('id');
        $.ajax({
            type: 'POST',
            url: '/accept_attestation',
            data: {'request_id':$id},
            success: function(data) {
                console.log('Success!');
                get_administrative_request()
                // $('#salary_attestationModal').modal('hide')
                //     window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });
$(document).on('click', '.refuse_attestation', function() {
    var $id = $(this).attr('id');
        $.ajax({
            type: 'POST',
            url: '/refuse_attestation',
            data: {'request_id':$id},
            success: function(data) {
                console.log('Success!');
                get_administrative_request()
                // $('#salary_attestationModal').modal('hide')
                //     window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });

$(document).on('click', '.refuse_mission', function() {
    var $id = $(this).attr('id');
        $.ajax({
            type: 'POST',
            url: '/refuse_mission',
            data: {'request_id':$id},
            success: function(data) {
                console.log('Success!');
                get_mission_request()
                // $('#salary_attestationModal').modal('hide')
                //     window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });
$(document).on('click', '.accept_mission', function() {
    var $id = $(this).attr('id');
        $.ajax({
            type: 'POST',
            url: '/accept_mission',
            data: {'request_id':$id},
            success: function(data) {
                console.log('Success!');
                get_mission_request()
                // $('#salary_attestationModal').modal('hide')
                //     window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });
    });

// $(document).on('click', '.generate-Ld-mission-btn', function() {
//         var $id = $(this).attr('id').split("__");
//         var user_id=$id[1];
//         var id_request=$id[0];
//
//         var currentRow = $(this).closest("tr");
//         var user_name = currentRow.find("td:eq(0)").text();
//         var request_name = currentRow.find("td:eq(1)").text();
//         var place_departure = currentRow.find("td:eq(2)").text();
//         var place_arrival = currentRow.find("td:eq(3)").text();
//         var date_departure = currentRow.find("td:eq(4)").text();
//         var date_arrival = currentRow.find("td:eq(5)").text();
//         user_name=user_name.replace(/^\s+|\s+$/g, '')
//         reqrequest_name=request_name.replace(/^\s+|\s+$/g, '')
//         place_departure=place_departure.replace(/^\s+|\s+$/g, '')
//         place_arrival=place_arrival.replace(/^\s+|\s+$/g, '')
//         date_departure=date_departure.replace(/^\s+|\s+$/g, '')
//         date_arrival=date_arrival.replace(/^\s+|\s+$/g, '')
//
//         $.ajax({
//             type: 'POST',
//             url: '/generate_mession_ld',
//             data: {'user_name':user_name,'request_name':request_name,'request_id':id_request,'user_id':user_id,'place_departure':place_departure,'place_arrival':place_arrival,'date_departure':date_departure,'date_arrival':date_arrival},
//             success: function(data) {
//                 console.log('Success!');
//                 get_administrative_request()
//                 $('#salary_attestationModal').modal('hide')
//                     window.location.href = "/static/assets/requests_document/"+data['result']
//             },
//         });
//
// });
$(document).on('click', '.generate-mission-request-btn', function() {
    var $id = $(this).attr('id').split("__");
    var user_id=$id[1];
    var id_request=$id[0];

        var currentRow = $(this).closest("tr");
        var user_name = currentRow.find("td:eq(0)").text();
        var request_name = currentRow.find("td:eq(1)").text();
        var place_departure = currentRow.find("td:eq(2)").text();
        var place_arrival = currentRow.find("td:eq(3)").text();
        var date_departure = currentRow.find("td:eq(4)").text();
        var date_arrival = currentRow.find("td:eq(5)").text();
        user_name=user_name.replace(/^\s+|\s+$/g, '')
        reqrequest_name=request_name.replace(/^\s+|\s+$/g, '')
        place_departure=place_departure.replace(/^\s+|\s+$/g, '')
        place_arrival=place_arrival.replace(/^\s+|\s+$/g, '')
        date_departure=date_departure.replace(/^\s+|\s+$/g, '')
        date_arrival=date_arrival.replace(/^\s+|\s+$/g, '')

        $.ajax({
            type: 'POST',
            url: '/generate_mession_request',
            data: {'user_name':user_name,'request_name':request_name,'request_id':id_request,'user_id':user_id,'place_departure':place_departure,'place_arrival':place_arrival,'date_departure':date_departure,'date_arrival':date_arrival},
            success: function(data) {
                console.log('Success!');
                get_administrative_request()
                $('#salary_attestationModal').modal('hide')
                    window.location.href = "/static/assets/requests_document/"+data['result']
            },
        });

});

})

function mission_requests_table(response,table) {
  $.each(response,function(index,value) {
      var state="";
      var buttons="";
      var file_btn="";
       buttons="" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success accept_mission \"  id=\""+value['id']+"\"><i class=\"fa fa-check\"></i> Accept</span>" +
          "&nbsp;&nbsp;<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger refuse_mission\"  id=\""+value['id']+"\"><i class=\"fa fa-times\"></i> Refuse</span>";

      if (value['progress_state']==='not done') {
         state= '<span class=\"badge badge-warning px-2 py-1\">Not Done</span>';

      }
          else {

          if(value['state'] === "accepted" && value['request_name']==="Ordre de mission LD"){
             state=state+ '<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success generate_attestation_travail \"  id=\"'+value['id']+'\"><i class="fa fa-check"></i> </span>';
             file_btn="<button type=\"button\" class=\"btn generate-mission-request-btn\" style='background-color: #F1F1E6;color: #34495E;' id='"+value['user_id']+"__"+value['id']+"'><i class=\"ti-download\"></i></button>"
          }
          if(value['state'] === "accepted" && value['request_name']==="Ordre de mission CD"){
             state=state+ '<span type=\"button\" class=\"badge px-2 py-1 badge-light-success text-success generate_attestation_travail \"  id=\"'+value['id']+'\"><i class="fa fa-check"></i> </span>';
             file_btn="<button type=\"button\" class=\"btn generate-mission-request-btn\" style='background-color: #F1F1E6;color: #34495E;' id='"+value['user_id']+"__"+value['id']+"'><i class=\"ti-download\"></i></button>"
          }
          else if(value['state'] === "refused"){
              state=state+ '<span type=\"button\" class=\"badge px-2 py-1 badge-light-danger text-danger \"  id=\"'+value['id']+'\"><i class=\"fa fa-times\"></i> </span>'

          }
          state=state+'<span class=\"badge badge-success px-2 py-1\">Done</span>' ;
      }


      table.append("<tr class='font-weight-bold'>" +
        "<td>" + value['user_name'] + "</td>" +
        "<td class='text-center'>" + value['request_name'] + "</td>" +
        "<td> " + value['request_date'] + "</td>" +
        "<td> " + value['place_of_arrival'] + "</td>" +
        "<td> " + value['place_of_departure'] + "</td>" +
        "<td> " + value['request_date_start'] + "</td>" +
        "<td> " + value['request_date_end'] + "</td>" +
        "<td> " + value['delivery_date'] + "</td>" +
        "<td>" + state + "</td>" +
        "<td>" + buttons + "</td>" +
        "<td>" + file_btn + "</td>" +
        "</tr>");
    });
    }





function get_mission_request() {
    $.ajax({
                type: 'POST',
                url: '/get_mission_requests',
                success: function (response) {
                // var data=JSON.parse(response)

                    if($.fn.DataTable.isDataTable("#mission_requests_table")){
                                $('#mission_requests_table').DataTable().destroy();
                                $('#mission_requests_table tbody').html("");
                            }

                     var table_tbody =  $("#mission_requests_table tbody");

                   mission_requests_table(response,table_tbody)
                    $("#mission_requests_table").DataTable({ "order": [[ 2, "desc" ]]})
                }

            });
}



