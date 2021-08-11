$(document).ready(init());

function init(){	
	setInterval(function(){refresh_counter()},3000);
	
}

function fill_display_code(){
	var displaycode  = $('#displaycode').val();	
	$('#displaycodefirst').attr('src', get_display_number(displaycode.substring(0,1)));
	$('#displaycodesecond').attr('src', get_display_number(displaycode.substring(1,2)));
	$('#displaycodethird').attr('src', get_display_number(displaycode.substring(2,3)));					
}

function get_counter_number(counter_number){
	var image_path = '/jakc_queue/static/src/images/';
	return image_path + counter_number + '_300x600.png';
}
		      		
function get_display_number(display_number){
	var image_path = '/jakc_queue/static/src/images/';
	return image_path + display_number + '_100px.png';
}
		      				      		
function refresh_counter(){
	console.log('Refresh Counter');
	fill_display_code()
	var displaycode  = $('#displaycode').val();
	$.ajax({
		url:  "/queue/display/" + displaycode,
		dataType: "json",							
		data: {},
		success: function(trans) {					
					if (trans.success == true){
						trans_id = trans.trans_id;
						$('#counternumber').html(trans.trans_id);						
						$('#first').attr('src', get_counter_number(trans_id.substring(0,1)));
						$('#second').attr('src', get_counter_number(trans_id.substring(1,2)));
						$('#third').attr('src', get_counter_number(trans_id.substring(2,3)));					
					}else{
						$('#first').attr('src', get_counter_number(0));
						$('#second').attr('src', get_counter_number(0));
						$('#third').attr('src', get_counter_number(0));											
					}						
				}
	});
}	
				
function cache_clear()
{	
	window.location.reload(true);					
}   