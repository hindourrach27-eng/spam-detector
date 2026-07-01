$(function() {

    $('.demo').each(function() {
        //
        // Dear reader, it's actually very easy to initialize MiniColors. For example:
        //
        //  $(selector).minicolors();
        //
        // The way I've done it below is just for the demo, so don't get confused
        // by it. Also, data- attributes aren't supported at this time...they're
        // only used for this demo.
        //
        $(this).minicolors({
            control: $(this).attr('data-control') || 'hue',
            defaultValue: $(this).attr('data-defaultValue') || '',
            format: $(this).attr('data-format') || 'hex',
            keywords: $(this).attr('data-keywords') || '',
            inline: $(this).attr('data-inline') === 'true',
            letterCase: $(this).attr('data-letterCase') || 'lowercase',
            opacity: $(this).attr('data-opacity'),
            position: $(this).attr('data-position') || 'bottom left',
            swatches: $(this).attr('data-swatches') ? $(this).attr('data-swatches').split('|') : [],
            change: function(value, opacity) {
                if (!value) return;
                if (opacity) value += ', ' + opacity;
                if (typeof console === 'object') {
                    console.log(value);
                }
            },
            theme: 'bootstrap'
        });

    });


    $('#btn_show_planning_form').click(function(){
    $('#btn_show_planning_form').hide();
    $('#show_planning_form').show();

        });


// $(document).on('click', '.add_user_timing', function() {
    $('#close_shift_table_modal').click(function(){
          window.location.href = "";

        });


    $('#add_new_shift_btn').click(function(){
        var shift_name = $('#shift_name').val();
        var start_time = $('#start_time').val();
        var end_time =  $('#end_time').val();
        var color =  $('#text-field').val();
        var entity_id =  $('#entity_id').val();

      $.ajax({
                type: 'POST',
                url: '/add_shift',
                data:{'shift_name':shift_name,'start_time':start_time,'end_time':end_time,'color':color,'entity_id':entity_id},
                success: function (response) {
                // var data=JSON.parse(response)
                $("#toast_msg").show()
                    setTimeout(function(){
			   $("#toast_msg").hide()
               //                      document.getElementById("alert").style.display = 'none';

			}, 2000);
                    $('#entities_users_add').val(null).trigger("change");

                    // display_teams_mailer();
                     $('#add_team_mailer_form_div').hide();
                     $('#show_add_team_mailer_btn').show();
                }
            });


 });


    $('input:radio[name="working_off_radio"]').change(
    function(){
        console.log("++++++++++++++++++++")
        // console.log($(this).val())
        if ($(this).is(':checked') && $(this).val() == 'working') {
           // console.log($(this).val())
             $('#users_list_div').show();
             $('#shift_list_div').show();

        }
        else if ($(this).is(':checked') && $(this).val() == 'off') {
             $('#users_list_div').show();
             $('#shift_list_div').hide();
        }
    });





 var  team_leader_planning=   function () {
           $.ajax({
                type: 'POST',
                url: '/display_employer_planning',
                success: function (response) {
                // var data=JSON.parse(response)
                //     $("#our_table").DataTable()
                    if($.fn.DataTable.isDataTable("#our_table")){
                                $('#our_table').DataTable().destroy();
                                $('#our_table thead').html("");
                                $('#our_table tbody').html("");
                            }

                     var table_tbody =  $("#our_table tbody");
                     var table_thead =  $("#our_table thead");


                    draw_planning_table_thead(response,table_thead);

                    draw_planning_table_tbody(response,table_tbody);

                    // table_thead.append("<tr>");
                    $("#our_table").DataTable()
                }

            });
    }



     var isMouseDown = false;

      setTimeout(function () {

      $("#our_table").on("mousedown", "td",function () {
         isMouseDown = true;
         $(this).toggleClass("highlighted");
         return false; // prevent text selection
     }).on("mouseover", "td",function () {
         if (isMouseDown) {
             $(this).toggleClass("highlighted");
         }
     }).bind("selectstart", function () {
         return false; // prevent text selection in IE
     });
     $(document).mouseup(function () {
         isMouseDown = false;
         // $("#my-event").modal('show');
     });

        $('#Spremi').click(function(){
         var $heads = $('#our_table thead th');
         //iterate over each selected item
         var array = $('#our_table td.highlighted').map(function(){
             var $this = $(this);
             //for each item find the first td in the same row and the header element at the same index
             return $this.parent().children().eq(0).text() + ' ' + $heads.eq($this.index()).text();
         }).get()
         console.log(array)
     })



      });

   //    $("#our_table").on("click", "td", function() {
   //   // alert($( this ).text());
   //    $(this).toggleClass("highlighted");
   // });


	$(document).on('click', '.add_user_timing', function() {
        var shift_id= $(this).attr('id');
         var $heads = $('#our_table thead th');
         //iterate over each selected item
         var array = $('#our_table td.highlighted').map(function(){
             var $this = $(this);
             //for each item find the first td in the same row and the header element at the same index
             return $this.parent().children().eq(0).text().trim() + ' ' + $heads.eq($this.index()).text().trim();
         }).get()
         // console.log(array)
         // console.log("shift_id")
         // console.log(shift_id)
   			$.ajax({
                type: 'POST',
                url: '/add_user_timing',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'users_dates_list':array,"shift_id":shift_id},
                success: function (response) {
                     team_leader_planning() ;
                      // $("#add-new-timing").modal('hide');
			          $("#toast").show()
                      setTimeout(function(){
                          $("#toast").hide()
                       }, 2000);

                }
            });
    });
    $("#clean_table").click(function () {
        $('#our_table td.highlighted').map(function(){
             $(this).removeClass("highlighted");
        });
    })
 $("#search_date").click(function () {
     	$.ajax({
                type: 'POST',
                url: '/display_employer_planning',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'daterange_planning':"true",'date_range':$('#date_range').val()},
                success: function (response) {

                         if($.fn.DataTable.isDataTable("#our_table")){
                                $('#our_table').DataTable().destroy();
                                $('#our_table thead').html("");
                                $('#our_table tbody').html("");
                            }

                     var table_tbody =  $("#our_table tbody");
                     var table_thead =  $("#our_table thead");


                    draw_planning_table_thead(response,table_thead);

                    draw_planning_table_tbody(response,table_tbody);

                    // table_thead.append("<tr>");
                    $("#our_table").DataTable()

                      // $("#add-new-timing").modal('hide');
			          $("#toast").show()
                      setTimeout(function(){
                          $("#toast").hide()
                       }, 2000);

                }
            });

 });

 $("#prev").click(function () {
     var $heads = $('#our_table thead th');
      var $date=$heads.eq(7).text()


     	$.ajax({
                type: 'POST',
                url: '/display_employer_planning',
                data: {'prev':"true",'date':$date},
                success: function (response) {

                         if($.fn.DataTable.isDataTable("#our_table")){
                                $('#our_table').DataTable().destroy();
                                $('#our_table thead').html("");
                                $('#our_table tbody').html("");
                            }

                     var table_tbody =  $("#our_table tbody");
                     var table_thead =  $("#our_table thead");


                    draw_planning_table_thead(response,table_thead);

                    draw_planning_table_tbody(response,table_tbody);

                    // table_thead.append("<tr>");
                    $("#our_table").DataTable()






                      // $("#add-new-timing").modal('hide');
			          $("#toast").show()
                      setTimeout(function(){
                          $("#toast").hide()
                       }, 2000);

                }
            });

 });

$("#next").click(function () {
     var $heads = $('#our_table thead th');

     var $date=$heads.eq(7).text()
    console.log($date)

     	$.ajax({
                type: 'POST',
                url: '/display_employer_planning',
                data: {'next':"true",'date':$date},
                success: function (response) {

                         if($.fn.DataTable.isDataTable("#our_table")){
                                $('#our_table').DataTable().destroy();
                                $('#our_table thead').html("");
                                $('#our_table tbody').html("");
                            }

                     var table_tbody =  $("#our_table tbody");
                     var table_thead =  $("#our_table thead");


                    draw_planning_table_thead(response,table_thead);

                    draw_planning_table_tbody(response,table_tbody);

                    // table_thead.append("<tr>");
                    $("#our_table").DataTable()






                      // $("#add-new-timing").modal('hide');
			          $("#toast").show()
                      setTimeout(function(){
                          $("#toast").hide()
                       }, 2000);

                }
            });

 });

$(document).on('click', '.users_off', function() {
    var $heads = $('#our_table thead th');
         //iterate over each selected item
         var array = $('#our_table td.highlighted').map(function(){
             var $this = $(this);
             //for each item find the first td in the same row and the header element at the same index
             return $this.parent().children().eq(0).text() + ' ' + $heads.eq($this.index()).text();
         }).get()
         console.log(array)
   			$.ajax({
                type: 'POST',
                url: '/add_users_off',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'users_dates_list':array},
                success: function (response) {
                    team_leader_planning() ;
                      // $("#add-new-timing").modal('hide');
			          $("#toast").show()
                      setTimeout(function(){
                          $("#toast").hide()
                       }, 2000);

                }
            });

});
 $("#shift_management").click(function () {
shift_table()

 });





 $(document).on('click', '.delete_shift', function() {
  $(this).parents("tr");
            var $_id = $(this).attr("id");
   			$.ajax({
                type: 'POST',
                url: '/delete_shift',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'shift_id':$_id},
                success: function (response) {
                     // $("#edit-shift").modal('hide');
			        $("#toast_delete").show();
                    setTimeout(function(){
                     $("#toast_delete").hide();
                    }, 2000);
                    shift_table();
                }
            });


	})






        // $("#our_table").DataTable()
        team_leader_planning() ;
$('.daterange').daterangepicker();
editShift();
})

 function get_calendar_data() {
     $.ajax({
                type: 'POST',
                url: '/get_calendar_data',
                success: function (response) {
                // var data=JSON.parse(response)
                $("#calendar").fullCalendar( 'addEventSource', response )
                }
            });
 }
   function draw_shift_table_tbody(response,table) {

            $.each(response,function(index,value) {

                table.append("<tr>" +
                    "<td class='text-capitalize'>" + value.shift_name+ "</td>" +
                    "<td>" + value.timeStart+ "</td>" +
                    "<td>" + value.timeEnd+ "</td>" +
                    "<td> <span class='badge' style='background-color: " + value.color+ ";width: 50px;height: 20px;'><p hidden>" + value.color+ "</p></span> </td>" +
                    "<td>" + value.entity_name+ "</td>" +
                    "<td>" +"<span id='"+ value.id+ "_"+value.shift_entity+"' class='edit_shift' data-target='#edit-shift' data-toggle='modal'><i class=\"mr-2 mdi mdi-table-edit\"></i></span> <span id='"+ value.id+ "' class='delete_shift'><i class=\"mr-2 mdi mdi-delete\"></i></span>"+ "</td>" +
                    "</tr>");


                    });

    }


    function draw_planning_table_thead(response,table) {
        var rows=""

                    $.each(response[0]['date'],function(index,value) {

                       rows=rows+"<th > " + value[0] +"<br>"+value[1] +"</th>";
                    });
               table.append("<tr style='font-size: 11px; ' class='text-center'> <th>Users</th>"+rows+"</tr>");

                };

   function draw_planning_table_tbody(response,table) {
            $.each(response[0]['users'],function(index,value) {
                                var col=""
    var user_shifts=value.user_shifts
    $.each(user_shifts,function(index,value2) {
        col=col+"<td ><span class=\"badge badge-pill user_day_plan\" style=\"background-color: "+value2.shift_color+";padding-top: 10px;padding-left: 15px;padding-right: 15px;\" id=\""+value2.Presence_planning_data_id+"\"><h6 style=\"color: whitesmoke;\" > "+value2.shift_name+"</h6> </span></td>"
    })
    table.append("<tr>" +
        "<td>" + value.user_full_name+ "</td>" + col +
        "</tr>");


                    });

    }

    function editShift() {
	$(document).on('click', '.edit_shift', function() {
    // $('.update_entity_span').on('click', function(event) {
	        $(this).parents("tr");
            var $_id = $(this).attr("id").split('_');
            var id_shift=$_id[0]
            var entity_id=$_id[1]
            // var $_rh_id=$_id[2]
            console.log("id+++++++++++++++++")
            console.log($_id)
            console.log("+++++++++++++++++")
            var currentRow = $(this).closest("tr");
            var shift_name = currentRow.find("td:eq(0)").text();
            var time_start = currentRow.find("td:eq(1)").text();
            var time_end = currentRow.find("td:eq(2)").text();
            var color = currentRow.find("td:eq(3)").text();
            var entity = currentRow.find("td:eq(4)").text();
            shift_name=shift_name.replace(/^\s+|\s+$/g, '')
            time_start=time_start.replace(/^\s+|\s+$/g, '')
            time_end=time_end.replace(/^\s+|\s+$/g, '')
            color=color.replace(/^\s+|\s+$/g, '')
            entity=entity.replace(/^\s+|\s+$/g, '')
            console.log(shift_name)
            // console.log(col1)
            // console.log(col2)
            // console.log(col3)
            // console.log(col4)
            // console.log("input +++++++++++++++++")
        $("#edit_shift_name").val(shift_name) ;
		    // document.getElementById("chef_prod_update").value =col3;
        $("#edit_color").val(color);
        $("#edit_start_time").val(time_start);
        $("#edit_end_time").val(time_end);
        // $("#edit_end_time").val(time_end);
        // $("#edit_entity_id").val(entity);
		    // document.getElementById("respo_rh_update").value =col4;
		    // element.value = col3;
         $("#edit_entity_id option[value='"+entity_id+"']").remove();
            //$("#entity_update_team").val(2).remove();
        $('#edit_entity_id').append(`<option value="`+entity_id+`" selected>`+entity+`</option>`);



		// $("#update_entity_btn").click(function(){
         $("#edit_shift_btn").off('click').on('click', function(event){
            var $shift_name =$("#edit_shift_name").val();
            var $color= $("#edit_color").val();
            var $end_time =  $("#edit_start_time").val();
            var $start_time =  $("#edit_end_time").val();
            var entity_id =  document.getElementById('edit_entity_id').value//$("#edit_entity_id").val();
            // console.log($chef_prod_update)
            // console.log($respo_rh_update)
            // console.log($date_creation_update)
            console.log("+++++++++++++++++");
            console.log(entity_id);
            console.log("+++++++++++++++++");
   			$.ajax({
                type: 'POST',
                url: '/update_shift',
                // data: {arr: [$entity_name_update,$chef_prod_update,$date_creation_update,$respo_rh_update,$_id ]},
                data: {'shift_id':id_shift,'shift_name':$shift_name,"time_start":$start_time,"time_end":$end_time,"entity_id":entity_id,'color_code':$color},
                success: function (response) {
                     $("#edit-shift").modal('hide');
			        $("#toast_update").show()
                    setTimeout(function(){
                     $("#toast_update").hide()
                    }, 2000);
                    console.log("nbr ex");
                    shift_table();
                }
            });


		});
	})
}

 function shift_table(){
     $.ajax({
                type: 'POST',
                url: '/user_entities_shifts',
                       success: function (response) {
                // var data=JSON.parse(response)
                //     $("#our_table").DataTable()
                    if($.fn.DataTable.isDataTable("#shift_table")){
                                $('#shift_table').DataTable().destroy();
                                $('#shift_table tbody').html("");
                            }

                     var table_tbody =  $("#shift_table tbody");

                    draw_shift_table_tbody(response,table_tbody);

                    // table_thead.append("<tr>");
                    $("#shift_table").DataTable()
                        // $(document ).on( "click", "#shift_table td", function() {
                        //    $("#shift_table td").click(function (e) {


                }
            });
 }




    // $('#shift_table2 td').on('click', function(e) {
    //                                 e.preventDefault(); // <-- consume event
    //                                 e.stopImmediatePropagation();
    //
    //                                 $this = $(this);
    //
    //                                 if ($this.data('editing')) return;
    //
    //                                 var val = $this.text();
    //
    //                                 $this.empty()
    //                                 $this.data('editing', true);
    //                                 console.log()
    //                                 // if ($this.parent().children().eq()) {
    //                                 if ($this.index()===0) {
    //                                     $('<input type="text" class="editfield form-control" name="shift_name" id="shift_name"/>').val(val).appendTo($this);
    //                                 }
    //                                  else if ($this.index()===1) {
    //                                     $('<input type="time" class="editfield form-control" name="shift_timeStart" id="shift_timeStart"/>').val(val).appendTo($this);
    //                                 }
    //                                   else if ($this.index()===2) {
    //                                     $('<input type="time" class="editfield form-control" name="shift_timeEnd" id="shift_timeEnd"/>').val(val).appendTo($this);
    //
    //                                 }
    //
    //                                   else if ($this.index()===3) {
    //                                       // $('<input>').attr({type: 'text', id: 'text-field', name: 'bar',value:val.trim(),class:'form-control editfield demo'}).appendTo($this);
    //                                       // $("<input type=\"text\" id=\"text-field\" class=\"form-control demo editfield\" value=\""+val+"\"/>").val(val).appendTo($this);
    //                                       // $this.after("<input type=\"text\" id=\"text-field\" class=\"form-control demo editfield\" value=\""+val+"\"/>");
    //                                     // var $input=$('<input type="text" id="text-field" class="form-control editfield" />').val(val);
    //                                             // $input.toggleClass('demo');
    //                                           // ($this).append($input);
    //                                           // ($this).html($($input));
    //                                        $('<input type="text" id="text-field"  className="demo form-control editfield" />').val(val).appendTo($this);
    //                                             // var textfield = document.createElement("input");
    //                                             // textfield.type="text";
    //                                             // textfield.value = val;
    //                                             // textfield.className = "demo";
    //                                             // ($this).append(textfield);
    //                                 }
    //                                     else if ($this.index()===4) {
    //
    //                                     $(' <select class="select2 form-control" multiple="multiple" style="height: 36px; width: 100%;" id="shift_entity_id">' +
    //                                         '                                    <option>Select</option>' +
    //                                         '                                    {% for entity in entities_list %}' +
    //                                         '                                    <option value="{{entity.id}}">{{entity.name}}</option>' +
    //                                         '                                    {% endfor %}' +
    //                                         '                                </select>').val(val).appendTo($this);
    //                                 }
    //
    //                         });
    //
    //                             putOldValueBack = function () {
    //                                 $("#shift_table .editfield").each(function(){
    //                                     $this = $(this);
    //                                     var val = $this.val();
    //                                     var td = $this.closest('td');
    //                                     td.empty().html(val).data('editing', false);
    //
    //                                 });
    //                             }
    //
    //                             $(document).click(function (e) {
    //                                 putOldValueBack();
    //                             });