$(document).ready(function ($) {

         $(document).on("click", "#get_page_data_btn", function ()  {
            var data = $('[name="duallistbox_demo1[]"]').val()
            //alert(data);
            //      $(this).prop("disabled", true);
      // add spinner to button
      // $(this).html(
      //   '<span class="spinner-grow text-primary" role="status" aria-hidden="true" style="margin-right: 10px;" ></span> Processing...'
      // );
      // $(this).css('background-color','white');
            document.getElementById("spinner").style.display='block';

      var table = $('#MyTable tbody');
            $.ajax({
                url: '/get_urls',
                data: {'urload': JSON.stringify(data)},
                type: 'GET',
                success: function (response) {
                 var data=JSON.parse(response)
            console.log(data);
                    // window.location.href = "pages_results";
                    $.each(data,function(index,value) {

                                 draw_table(value,table,index);

                                    });
                  // document.getElementById("ok").innerHTML = 'Submit data';
                                document.getElementById("spinner").style.display='none';

$("#MyTable").DataTable();
                    console.log(response);
                },
                error: function (error) {
                    console.log(error);
                }
            })


      //return false;
        });

    // --------
     $(document).on("click", "#get-top-chart-table", function () {
              $.ajax({
                type: 'POST',
                url: '/top_charts',
                // data: {empty_arr:''},
                  success : function(data) {
                     // var data=JSON.parse(data)
                     //             table.empty();
                               var table = $("#top_chart_table tbody");
                                $.each(data,function(index,value) {
                                 top_chart_table(index,value,table)
                                    });
                           $("#top_chart_table").DataTable();
                  }
                  });

        });
            $(document).on("click", "#first_search", function () {
              $.ajax({
                type: 'POST',
                url: '/search_get_url',
                data: {'query':$('#query').val(),'lang':$('#inputState').val(),'start':$('#start').val(),'stop':$('#stop').val(),'country':$('#myInput').val()},
                  success : function(data) {
                    $("#urls_div").html(data)

                  }
                  });

        });
    // --------
  $(document).on("click", "#search_top_chart", function () {
            var year =document.getElementById("top_chart_year").value
                $.ajax({
                type: 'POST',
                url: '/top_charts',
                data: {arr: [year]},
                  success : function(data) {
                     // var data=JSON.parse(data)
                     //             table.empty();
                               var table = $("#top_chart_table tbody");
                                $.each(data,function(index,value) {
                                 top_chart_table(index,value,table)
                                    });
                           $("#top_chart_table").DataTable();
                  }
                  });

        });


   $(document).on("click", "#get_related_queries-btn", function () {
                   var search_option =document.getElementById("search_option").value
            var query =document.getElementById("query-search").value
       console.log(search_option)
       console.log(query)
              $.ajax({
                type: 'POST',
                url: '/related_queries',
               data: {arr:[search_option,query]},
                  success : function(data) {
                     var data=JSON.parse(data)
                     //             table.empty();
                               var table = $("#related_queries_table tbody");
                                $.each(data,function(index,value) {
                                   $.each(value,function(index,value) {
                                 top_chart_table(index,value,table)
                                    });
                                });
                           $("#related_queries_table").DataTable();
                  }
                  });

        });


   $(document).on("click", "#daily_search_btn_search", function () {
              $.ajax({
                type: 'POST',
                url: '/top_charts',
                // data: {empty_arr:''},
                  success : function(data) {
                     // var data=JSON.parse(data)
                     //             table.empty();
                               var table = $("#daily_search_table tbody");
                                $.each(data,function(index,value) {
                                 top_chart_table(index,value,table)
                                    });
                           $("#daily_search_table").DataTable();
                  }
                  });

        });

      $(document).on("click", ".search-top-chart", function () {
          var id = $(this).attr("id");
          console.log(id)
        var q=document.getElementById('query');
        q.value=id
        $('#top_chart_modal').modal('hide');
        $('#related_queries_modal').modal('hide');
        $('#daily_search_modal').modal('hide');

        });


  /*execute a function when someone clicks in the document:*/
        /*An array containing all the country names in the world:*/
var countries = [ "countryMR","countryFR","countryCA","countryGB"];
/*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/
autocomplete(document.getElementById("myInput"), countries);
        // Keyup event
        $("#query").keypress(function(){
 var dInput = this.value;
 $.ajax({
                url: '/query_seggestions',
                data: dInput,
                type: 'POST',
                success: function (response_data) {
                  //  window.location.href = "query_seggestions";
                    console.log(response_data);
$("#query_input").empty()
                    for (let i =0;i<response_data.length;i++){


$('#query_input').append(`<option value="${response_data[i]["title"]}">

                                  </option>`);

                    }

                },
                error: function (error) {
                    console.log(error);
                }
            })
});


        // new ClipboardJS('.btn');

            $("#top_chart_table").DataTable();
            $("#related_queries_table").DataTable();

    //
    // animateElements();
    // $(window).scroll(animateElements);

    var availableTags = [
    ];
    $( "#tags" ).autocomplete({
      source: availableTags
    });

 $(document).on("click", ".select", function(){

        var id_value = $(this).attr("id");
 console.log(id_value)
document.getElementById("query").value =id_value;
    });



// ***********
          var demo1 = $('select[name="duallistbox_demo1[]"]').bootstrapDualListbox();


        // +++++++++++++++++
        	$(".btn-group .btn").click(function(){
		var inputValue = $(this).find("input").val();
		if(inputValue != 'all'){
			var target = $('table tr[data-status="' + inputValue + '"]');
			//var data = $('table tr[data-status="' + inputValue + '"]').text();

			//for (var i = 0, row; row = table.rows[i]; i++)

        var test = $('table tr[data-status="' + inputValue + '"] td[id="clipboardExample1]"').text();
        console.log(test)
        //console.log(document.getElementById('clipboardExample1').value);
        var dict={};
        var liste=[];
        $('#MyTable tr[data-status="' + inputValue + '"]').each(function() {
        var text=$(this).find("#clipboardExample1").html();
        dict={
        "text":$(this).find("#clipboardExample1").html(),
        "label":$(this).find("#label").text()
        }
        liste.push(dict)

        });
        console.log(liste);
			$.ajax({
                url: '/upload_text',
                data: {'load_data': JSON.stringify(liste)},
                type: 'GET',
                success: function (response) {
                   // window.location.href = "pages_results";
                    console.log(response);
                },
                error: function (error) {
                    console.log(error);
                }
            })
           // console.log(liste)
			//console.log(data2)

			$("table tbody tr").not(target).hide();
			target.fadeIn();
		} else {
			$("table tbody tr").fadeIn();
		}
	});
              var bs = $.fn.tooltip.Constructor.VERSION;
             var str = bs.split(".");
            if(str[0] == 4){
                $(".label").each(function(){
        	    var classStr = $(this).attr("class");
                var newClassStr = classStr.replace(/label/g, "badge");
                $(this).removeAttr("class").addClass(newClassStr);
        });
    }



var objDiv = document.getElementById("table_div");
objDiv.scrollTop = objDiv.scrollHeight;
});


function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      var query= document.getElementById("query")
      closeAllLists(e.target);
  });
}



function trim (el) {
    el.value = el.value.replace(/(^\s*)|(\s*$)/gi, ""). // removes leading and trailing spaces
        replace(/[ ]{2,}/gi, " ").       // replaces multiple spaces with one space
        replace(/\n +/, "\n");           // Removes spaces after newlines
    return;
}

// function animateElements() {
//         $('.progressbar').each(function () {
//             var elementPos = $(this).offset().top;
//             var topOfWindow = $(window).scrollTop();
//             var percent = $(this).find('.circle').attr('data-percent');
//             var animate = $(this).data('animate');
//             console.log("++++++++++++++++++++++++++++++++++++++++")
//             console.log(percent)
//             if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
//                 $(this).data('animate', true);
//                 $(this).find('.circle').circleProgress({
//                     // startAngle: -Math.PI / 2,
//                     value: percent/ 100,
//                     size : 400,
//                     thickness: 15,
//                     fill: {
//                         color: '#B20000'
//                     }
//                 }).on('circle-animation-progress', function (event, progress, stepValue) {
//                     $(this).find('strong').text((stepValue*100).toFixed(0) + "%");
//                 }).stop();
//             }
//         });
//     }
function top_chart_table(index,value,table) {
     table.append("<tr><td>" + index + "</td>" +
      "<td>" + value + "</td>"+
       "<td><span  class='search-top-chart' id='" + value+ "'> <i class=\"fa fa-search fa-sm\" style=\"color:#ff8000;\"></i></span>  </td></tr>");

}
 function draw_table(value,table,index) {
    console.log(value['predict_status'])
    console.log(value['predict_result'])
     var td ='';
        if (value['predict_status']=="Inbox"){
            td='<td><span class="badge badge-success" >Inbox</span></td>'
        }
        else if (value['predict_status']=="Spam"){
            td='<td><span class="badge badge-danger" >Spam</span></td>'
        }
        else if (value['predict_status']=="None"){
            td='<td><span class="badge badge-warning">None</span></td>'
        }
       console.log(td)
         table.append(
        '<tr data-status="'+value['predict_status']+'">' +
             '<td> ' +(index+1)+'</td>'+
            '<td> ' +value['url']+'</td>'+
             '<td>  <textarea class="form-control" rows="2" id="clipboardExample'+(index+1)+'" style="height: 50px;" value="'+value['text']+'">'+value['text']+'</textarea>' +
             ' <div class="mt-3"> <button type="button" class="btn btn-link btn-clipboard" data-clipboard-action="copy" id="bar'+(index+1)+'" data-clipboard-target="#clipboardExample'+(index+1)+'" style="margin-left: 500px; color: #581845; font-size: 15px;" ><b>Copy</b></button>' +
             ' </div></td>'+td+
             ' <td> <div class="col text-right align-self-center">' +
             '<div data-label="'+(value["predict_result"]*100).toFixed(2)+'" class="css-bar mb-0 css-bar-info css-bar-88">%</div></div></td></tr>');


}