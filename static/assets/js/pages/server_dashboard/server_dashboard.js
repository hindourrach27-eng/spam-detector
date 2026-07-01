$( document ).ready(function() {
    var team_id_param = null
     window.team_id_param2 = null;
$(document).on("click", ".btn_search_server", function () {
   $('#modal-search').modal('hide');
   console.log("team_id_param");
   console.log(team_id_param);
   var start =document.getElementById("date_start").value
   var end =document.getElementById("date_end").value
  servers= document.getElementById("textarea-servers").value;
          $.ajax({
                type: 'POST',
                url: '/search_servers_by_team',
                data: {arr: [start,end,team_id_param,servers]},
                  success : function(response) {
                    var data=JSON.parse(response)

                      // var div=document.getElementById("container1")
                      // div.innerHTML=""
                                 var table = $('#table'+team_id_param+' tbody');


                                 table.empty();
                                $.each(data,function(index,value) {

                                    console.log("+++++++++++++++++++++++")
                                    console.log(index)

                                    draw_table(value,table)


                                    });
                  }
                  });

        });



$('input[type=radio][name=Radio]').change(function() {
      console.log("team_id_param");
      console.log(team_id_param2);
      var start =document.getElementById("date_start").value
        var end =document.getElementById("date_end").value
    var label;
    if (this.value == 'spam') {
                label= "spam";

    }
    else if (this.value == 'inbox') {
             label= "inbox";

    }
      $.ajax({
                type: 'POST',
                url: '/search_server_by_state',
                data: {arr: [start,end,team_id_param,label]},
                  success : function(response) {
                    var data=JSON.parse(response)
                                 var table = $('#table'+team_id_param2+' tbody');
                                 table.empty();
                                 console.log(data)
                      if (data.length!=0){    $.each(data,function(index,value) {
                                    draw_table(value,table)
                                    console.log(value)
                                    });}

                  }
                  });
});

$(document).on("click", ".search-servers", function () {
    // $('#modal-search-server').modal('show');
    // document.getElementById("modal-search-server").style.display='block';
                var id = $(this).attr("id");
                team_id_param=id;
   console.log("team_id_param");
   console.log(team_id_param);

        });
$(document).on("click", ".delete", function () {
            $(this).parents("tr").remove();
            $(".add-new").removeAttr("disabled");
            var id = $(this).attr("id");
            var string = id;
            $.post("/ajax_delete_server", {string: string}, function (data) {
                $("#displaymessage").html(data);
                $("#displaymessage").show();
            });
        });
 $(document).on("click", ".server-list", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_servers',
                data: {arr: [id,start,end]},
                  success : function(data) {
                    console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container-servers-list")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["name"]+"  <br>";
                        div.innerHTML +="----------------------------  <br>";
                                    });
                  }
                  });
        });
  $(document).on("click", ".ips-list", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_ips',
                data: {arr: [id,start,end]},
                  success : function(data) {
                    console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container-ips-list")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["ip"]+"  <br>";
                        div.innerHTML +="----------------------------  <br>";

                                    });
                  }
                  });
        });

 $(document).on("click", ".inbox-server", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_inbox_server',
                data: {arr: [id,start,end]},
                  success : function(data) {
                    console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container1")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["name"]+"  <br>";

                                    });
                  }
                  });
        });

  $(document).on("click", ".inbox-ip", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_inbox_ip',
                data: {arr: [id,start,end]},
                  success : function(data) {
                      console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container2")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["ip"]+" : "+value["server_name"]+" <br>";

                                    });
                  }
                  });
        });

   $(document).on("click", ".servers-passed", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_servers_passed',
                data: {arr: [id,start,end]},
                  success : function(data) {
                      console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container-servers-passed")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["name"]+" <br>";
                        div.innerHTML +="------------------- <br>";

                                    });
                  }
                  });
        });

    $(document).on("click", ".servers-15ToPassed", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_servers_15ToPassed',
                data: {arr: [id,start,end]},
                  success : function(data) {
                      console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container-servers-15-ToPassed")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["ip"]+" : "+value["name"]+" <br>";
                        div.innerHTML +="------------------- <br>";
                                    });
                  }
                  });
        });


    $(document).on("click", ".spam-server", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_spam_server',
                data: {arr: [id,start,end]},
                  success : function(data) {
                    console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container1spam")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["name"]+"  <br>";

                                    });
                  }
                  });
        });
$(document).on("click", ".spam-ip", function () {
            var id = $(this).attr("id");
            console.log("id")
            console.log(id)
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
               $.ajax({
                type: 'POST',
                url: '/list_spam_ip',
                data: {arr: [id,start,end]},
                  success : function(data) {
                      console.log(data)
                       var data=JSON.parse(data)
                      var div=document.getElementById("container2spam")
                      div.innerHTML=""
                       $.each(data,function(index,value) {
                        div.innerHTML +=value["ip"]+" : "+value["server_name"]+" <br>";

                                    });
                  }
                  });
        });

$(document).on("click", ".update", function () {
            $(this).parents("tr");
            var id = $(this).attr("id");
            var currentRow = $(this).closest("tr");
            var col1 = currentRow.find("td:eq(2)").text(); // get current row 1st TD value
            //var date_p = document.getElementById('date_p').innerText ;
            console.log("+++++++++++++++++++++++++++")

            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
            $.ajax({
                type: 'POST',
                url: '/update_payment_date',
                data: {arr: [id, col1,start,end]},
                  success : function(data) {
                        var data=JSON.parse(data)
                      var idd=id.split("/")
                            console.log('#table'+idd[1]+' tbody')
                                 var table = $('#table'+idd[1]+' tbody');

                                 table.empty();
                                $.each(data,function(index,value) {

                                 draw_table(value,table)

                                    });
                                         $("#table"+idd[1]).DataTable();
                                         $('#table'+idd[1]+' tbody').addClass("search");


                    $('#filter'+idd[1]).keyup(function() {
                        var rex = new RegExp($(this).val(), 'i');
                        // var $t = $(this).children(":eq(4))");
                        $('.search tr ').hide();

                        //Recusively filter the jquery object to get results.
                        $('.search tr ').filter(function(i, v) {
                          //Get the 3rd column object here which is userNamecolumn
                            var $t = $(this).children(":eq(" + "3" + ")");
                            return rex.test($t.text());
                        }).show();
                    });
    $('#filter_select'+idd[1]).keyup(function() {
                        var rex = new RegExp($(this).val(), 'i');
                        // var $t = $(this).children(":eq(4))");
                        $('.search tr ').hide();

                        //Recusively filter the jquery object to get results.
                        $('.search tr ').filter(function(i, v) {
                          //Get the 3rd column object here which is userNamecolumn
                            var $t = $(this).children(":eq(" + "9" + ")");
                            return rex.test($t.text());
                        }).show();
                    });



                }
            });
        });
 function draw_table(value,table) {
     var spanchart ="";
     value['server_state'].forEach(function(stat){
         if (stat === 1){
             spanchart += "<span style=\"border-left: 6px solid #009100;border-right: 2px solid #f7f7f7; height: 15px;\"></span>";
         }if (stat === 0){
             spanchart +=  "<span style=\"border-left: 6px solid #ff1c00;height: 15px;border-right: 2px solid #f7f7f7;\"></span>";
         }if (stat === null){
             spanchart += "<span style=\"border-left: 6px solid #868686;height: 15px;border-right: 2px solid #f7f7f7;\"></span>";
         }
     });
           if (value['etat'] === 'black') {
                                    table.append("<tr style=\"color: aliceblue; background-color: #5a5959;\">" +
                                        "<td class=\"text-capitalize\"> <span class=\"show_chart\" data-toggle=\"modal\" data-target=\"#bs-example-modal-lg\"  id='"+value['server_state__']+"' > " + value['server_name'] + "</span></td>" +
                                        "<td>" + value['date_entree'] + "</td>" +
                                        "<td>" + value['date_paiement'] + "</td>" +
                                        "<td>" + value['server_period'] + "</td>" +
                                        "<td>" + value['send'] + "</td>" +
                                        "<td>" + value['total_send'] + "</td>" +
                                        "<td>" + value['avg'] + "</td>" +
                                        "<td><div>" + spanchart + "</div></td>" +
                                        "<td>" + value['etat_msg'] + "</td>" +
                                        "<td><span  class='update' id='" + value['id'] + "/"+value['team_id']+"'> <i class=\"mr-2 mdi mdi-reload\" style=\"color: #7AB8F9 ;\"></i></span> <span  class='delete' id='" + value['id'] + "'> <i class=\"fa fa-trash \" style=\"color: #FB2358 ;font-size: 1em;\"></i></span> </td></tr>");

                                }
                                    else if(value['etat'] === 'red') {
                                    table.append("<tr>" +
                                         "<td class=\"text-capitalize\" style=\" color: red;\">  <span class=\"show_chart\" data-toggle=\"modal\" data-target=\"#bs-example-modal-lg\"  id='"+value['server_state__']+"' > " + value['server_name'] + "</span></td>" +
                                        "<td>" + value['date_entree'] + "</td>" +
                                        "<td>" + value['date_paiement'] + "</td>" +
                                        "<td>" + value['server_period'] + "</td>" +
                                        "<td>" + value['send'] + "</td>" +
                                        "<td>" + value['total_send'] + "</td>" +
                                        "<td>" + value['avg'] + "</td>" +
                                        "<td><div>" + spanchart + "</div></td>" +
                                        "<td>" + value['etat_msg'] + "</td>" +
                                        "<td> <span  class='delete' id='" + value['id'] +"'> <i class=\"fa fa-trash \" style=\"color: #FB2358;font-size: 1em; margin-left: 25px;\"></i></span></td></tr>");
                                }
                                    else if(value['etat'] === 'orange') {
                                    table.append("<tr>" +
                                        "<td class=\"text-capitalize\" style=\" color: #d06032;\"> <span class=\"show_chart\" data-toggle=\"modal\" data-target=\"#bs-example-modal-lg\"  id='"+value['server_state__']+"' > " + value['server_name'] + "</span></td>" +
                                        "<td>" + value['date_entree'] + "</td>" +
                                        "<td>" + value['date_paiement'] + "</td>" +
                                        "<td>" + value['server_period'] + "</td>" +
                                        "<td>" + value['send'] + "</td>" +
                                        "<td>" + value['total_send'] + "</td>" +
                                        "<td>" + value['avg'] + "</td>" +
                                        "<td><div>" + spanchart + "</div></td>" +
                                        "<td>" + value['etat_msg'] + "</td>" +
                                        "<td> <span  class='delete' id='" + value['id'] +"'> <i class=\"fa fa-trash \" style=\"color: #FB2358;font-size: 1em; margin-left: 25px;\"></i></span></td></tr>");
                                }
                                    else if(value['etat'] === 'green') {
                                    table.append("<tr>" +
                                        "<td class=\"text-capitalize\" style=\" black;\">  <span class=\"show_chart\" data-toggle=\"modal\" data-target=\"#bs-example-modal-lg\"  id='"+value['server_state__']+"' > " + value['server_name'] + "</span></td>" +
                                        "<td>" + value['date_entree'] + "</td>" +
                                        "<td>" + value['date_paiement'] + "</td>" +
                                        "<td>" + value['server_period'] + "</td>" +
                                        "<td>" + value['send'] + "</td>" +
                                        "<td>" + value['total_send'] + "</td>" +
                                        "<td>" + value['avg'] + "</td>" +
                                        "<td><div>" + spanchart + "</div></td>" +
                                        "<td>" + value['etat_msg'] + "</td>" +
                                        "<td> <span  class='delete' id='" + value['id'] +"'> <i class=\"fa fa-trash \" style=\"color: #FB2358;font-size: 1em; margin-left: 25px;\"></i></span></td></tr>");
                                }
    }

      $(document).on("click", ".show_table", function () {
            $(this).parents("tr");

            var id = $(this).attr("id");
            window.team_id_param2=id;
            var start =document.getElementById("date_start").value
            var end =document.getElementById("date_end").value
            var arr = [start,end,id];

            console.log(arr)
           $.ajax({
                    type:'POST',
                    url: 'get_server_datatable',
                    data:{arr:arr},
                    success : function(data) {
                        var data=JSON.parse(data)
                            console.log('#table'+id+' tbody')
                                 var table = $('#table'+id+' tbody');


                                 table.empty();
                                $.each(data,function(index,value) {

                                    console.log("+++++++++++++++++++++++")
                                    console.log(index)

                                    draw_table(value,table)


                                    });
                        $("#table"+id).DataTable();
                        $('#table'+id+' tbody').addClass("search");

                    $('#filter'+id).keyup(function() {
                        var rex = new RegExp($(this).val(), 'i');
                        // var $t = $(this).children(":eq(4))");
                        $('.search tr ').hide();

                        //Recusively filter the jquery object to get results.
                        $('.search tr ').filter(function(i, v) {
                          //Get the 3rd column object here which is userNamecolumn
                            var $t = $(this).children(":eq(" + "3" + ")");
                            return rex.test($t.text());
                        }).show();
                    });
                    $('#filter_select'+id).keyup(function() {
                        var rex = new RegExp($(this).val(), 'i');
                        // var $t = $(this).children(":eq(4))");
                        $('.search tr ').hide();

                        //Recusively filter the jquery object to get results.
                        $('.search tr ').filter(function(i, v) {
                          //Get the 3rd column object here which is userNamecolumn
                            var $t = $(this).children(":eq(" + "8" + ")");
                            return rex.test($t.text());
                        }).show();
                    });


                }
        });

        });
    $(document).on("click", ".show_chart", function () {
     var d = $(this).attr("id");

         d=d.split(";")
         var data=[];
         $.each(d,function(index,value) {

             var line=value.split(",")


             if (index===0){
                 data.push([line[0],line[1]])
             }
             else if (index<d.length){
                  data.push([line[1],line[2]])
             }
           else if (index>d.length){

             }


         });
   console.log(data)

    document.getElementById('container').innerHTML = "";
anychart.onDocumentReady(function () {
    //create area chart
    var chart = anychart.column();

    //turn on chart animation
    chart.animation(true);

    //set container id for the chart
    chart.container('container');

    var series = anychart.data.mapAsTable(data);
    for (var i in series) {
        chart.column(series[i]);
    }

    //initiate chart drawing
    chart.draw();
});
var currentRow = $(this).closest("tr");
            var server_name = currentRow.find("td:eq(0)").text();
    document.getElementById("server_name").innerHTML=server_name;
    document.getElementById("bs-example-modal-lg").style.display='block';

  });
$(document).ready(function(){
  $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#myTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});
});
