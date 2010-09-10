
$(function() {
	$(document).ready(function(){
		$(".submit").click(function() {
			var v = $("#commentForm").validate();
			if (!$("#commentForm").valid())
				return false;
			var blogid = $("input#blogid").val();
			var name = $("input#cname").val();
			var email = $("input#cemail").val();
			var url = $("input#curl").val();
			var comment = $("textarea#ccomment").val();
			var recaptcha_response_field = $("input#recaptcha_response_field").val();
			var recaptcha_challenge_field = $("input#recaptcha_challenge_field").val();
			var dataString = 'name='+ name + '&email=' + email + '&url=' + url + '&comment=' + comment + '&recaptcha_response_field=' + recaptcha_response_field + '&recaptcha_challenge_field=' + recaptcha_challenge_field + '&blog_id=' + blogid;
				//alert (dataString);return false;
			$.ajax({
				type: "POST",
				url: "/blog/addcomment",
				data: dataString,
				success: function(result) {
					if(result == "1") {
						var new_comment = "<div class='feedbackItem'><div class='feedbackListSubtitle'><div class='feedbackManage'></div><a href='";
						new_comment += $("input#curl").val();
						new_comment += "'><b>"
						new_comment += $("input#cname").val()
						new_comment += "</b></a>&nbsp;刚刚回复了：</div><div class='feedbackCon'>"
						new_comment += $("textarea#ccomment").val().replace(/\n/g, '<br />')
						new_comment += "</div></div>"
						
						$('#commentList').append(new_comment);
						$('#message').html("<font color=green>非常感谢您的评论！</font>");
						$("textarea#ccomment").focus();
						$("textarea#ccomment").val('');
						//$("#commentForm")[0].reset();
						Recaptcha.reload();
					}
					else if(result == "0") {
						$('#message').html("<font color=red>验证码错误</font>");
						Recaptcha.reload();
					}
					else {
						$('#message').html("<font color=red>检查一下哪里弄错了</font>");
					}
				}
			});
			return false;
		});
		
	});
});


function ReplyComment(author) {
	$("#ccomment").focus();
	$("#ccomment").val("@" + author + "\n" + $("#ccomment").val());
};

function QueteComment(author, content) {
	$("#ccomment").focus();
	$("#ccomment").val($("#ccomment").val() + "『" + author + "』 曾经说过：" + content + "\n===\n");
};