$(document).ready(function() {
	$('#is_instructor').click(function() {
		if($('#mail-field').is(":visible")) {
			$('#mail-field').hide()
		} else {
			$('#mail-field').show()
		}
	})
})