$(document).ready(init());

function init(){
	
}
function runEffect() {
    setTimeout(function(){
        var selectedEffect = 'blind';
        var options = {};
        $('#message').hide();
     }, 5000);
}

function request_app(value){	
	$.ajax({
		url:  "/queue/app/" + value,
		dataType: "json",							
		data: {},
		success: function(data) {
					if(data.success == true){
						$('#message').show();
						$('#message').html(data.message);
						runEffect();
					}else{
						$('#message').html("Request Error");
					}
				}
	});
}
