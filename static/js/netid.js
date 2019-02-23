$(document).ready ( function(){
	access_token = getQueryVariable('access_token')
	if(access_token!='none'){
		$.post('../api/netid',{'access_token':access_token},function(data){
			window.location.replace('/')
		}).fail(function(err){
			alert('Critical Failure: Should not reach this message')
			window.location.replace('/')
		})
	}
	else{
		alert('Improper Access')
		window.location.replace("../")
	}
})

function getQueryVariable(variable) {
    var query = window.location.hash.substring(1);
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
        }
    }
    return 'none';
}