$(document).ready(init());


$('#backconfirm').click(function(){
    
    if ($('#title').val()==="") {
      // invalid
      $('#title').next('.help-inline').show();
      return false;
    }
    else {
      // submit the form here
      // $('#InfroText').submit();
      
      return true;
    }           
});

$('#btnpickup').click(function(){	
	$.ajax({		
		url:  "/queue/pickup/" +  $('#pickup_code').html(),
		dataType: "json",
		type: "POST",
		data: {},
		success: function(data) {
					if(data.success){
						$('#message').html(data.message);
						trans_id = data.trans_id;
						$('#first').attr('src', get_display_number(trans_id.substring(0,1)));
						$('#second').attr('src', get_display_number(trans_id.substring(1,2)));
						$('#third').attr('src', get_display_number(trans_id.substring(2,3)));
					}else{
						$('#message').html("Error");
					}																				
				 }
	});
});

function init(){
	
}

function get_display_number(display_number){
	var image_path = '/jakc_queue/static/src/images/';
	return image_path + display_number + '_100px.png';
}

function check_last_counter(value){
	$.ajax({		
		url:  "/queue/pickupchecklast/" +  $('#pickup_code').html(),
		dataType: "json",
		type: "POST",
		data: {},
		success: function(data) {
					if(data.success){
						
					}else{
						$('#message').html("Error");
					}																				
				 }
	});
}

function pickup_app(value){	
	var pickuplist = $('#pickuplist');
	var pickupapp = $('#pickupapp');
	
	if (pickupapp.is(':hidden'))
	{
		
		$('#pickup_code').html(value);		
		pickupapp.show("slow");
		pickuplist.hide("slow");	  
	}

}

function pickup_list(value){	
	var pickuplist = $('#pickuplist');
	var pickupapp = $('#pickupapp');
	
	if (pickuplist.is(':hidden'))
	{
		pickuplist.show("slow");
		pickupapp.hide("slow");	  
	}
}

function on_change_type(type_id){
	console.log('Change Type ' + type_id);
}


function load_user(){
	$.ajax({		
				url:  "/queue/dispcounter/" +  $('#pickupid').val(),
				dataType: "json",
				type: "POST",
				data: {},
				success: function(data) {
						customer = data.results[0];
																			
					}
			   });
}

