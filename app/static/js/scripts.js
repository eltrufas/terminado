$(document).ready(function() {
	$('#is_instructor').click(function() {
		if($('#mail-field').is(":visible")) {
			$('#mail-field').hide()
		} else {
			$('#mail-field').show()
		}
	})

	$('#aprobado').click(function() {
		if($('#rejected_field').is(":visible")) {
			$('#rejected_field').hide()
		} else {
			$('#rejected_field').show()
		}
	})
})
