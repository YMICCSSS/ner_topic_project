document.getElementById("searchboxinput").onclick = function () {
	var result = document.getElementsByClassName("section-result");
	alert("ClassName 為 section-result 的物件共有"+result.length+"個");

	for(var i=0; i<result.length; i++) {
		var element = result[i]
	// alert("for 第" + i + result[i].getAttribute('aria-label'));
	result[i].addEventListener("mouseover",function(e){
		console.log(e); // 傳入function的第一個參數是event物件
		var eventtype = e.type // this, 目前的元素
		url = 'https://7fba8f29.ngrok.io/api?storeid=1'
		alert("第" + this.getAttribute('data-result-index') + '筆,' + this.getAttribute('aria-label'));
		test_fun(e,url)
		});
	};
};
/// 做出來了!!  在元素生成之前先幫它加上事件，等它生成後就能直接用了
$('#pane').on('mouseover', '.section-result', function(e){
	alert("第" + this.getAttribute('data-result-index') + '筆,' + this.getAttribute('aria-label'));
    // alert("pane on handler called.");
});
// $(document).on('mouseover', '.section-result', function(){
// 	alert("on handler called.");
// });

function test_fun(e,url) {
	$.ajax({
  type: "GET",
  dataType: "json",
  url: url,
  headers : {'Access-Control-Allow-Headers:':'*'},
  success: function(data) {
    console.log('bbb');
    var pic = document.getElementById("pic_api")
    console.log(data);
  },
  error: function (jqXHR, textStatus, errorThrown) {  
       console.log(jqXHR.responseText);  
   },  
  complete: function(xhr, textStatus) {
      console.log(xhr.status);
  }   
})
}

var url = 'https://database-api-tibame.herokuapp.com/api?storeid=2'
$.ajax({
  type: "GET",
  dataType: "json",
  url: url,
  headers : {'Access-Control-Allow-Headers:':'*'},
  success: function(data) {
    console.log('aa');
    console.log(data);
  },
  error: function (jqXHR, textStatus, errorThrown) {
  		console.log('bb');  
       console.log('bb'+jqXHR.responseText);  
   },  
  complete: function(xhr, textStatus) {
  		console.log('cc');
      console.log(xhr.status);
  }   
})

// document.getElementById("searchboxinput").addEventListener("change", function(e) {
//     fun_alert('change_, ' + e);
// });
// document.getElementById("searchbox_form").addEventListener("submit", function(e) {
//     fun_alert('submit, ' + e);
// });
// document.getElementById("searchbox_form").onsubmit = function(){
// 	fun_alert('onsubmit, ' + e);
// };

// document.querySelector('body').addEventListener('click', function(event) {
//   fun_alert('body, ' + event);
// });
// document.getElementById("searchbox_form").addEventListener("submit", myFunction);

// function myFunction() {
//   alert("The form was submitted");
// }
// window.onload = fun_alert('aaa');
// document.body.addEventListener("change", function(e) {
//     fun_alert('change_1, ' + e);
// });
// document.addEventListener("DOMContentLoaded", function(e) {// 當 document 結構已解析完成才會執行
//   fun_alert('DOMContentLoaded, ' + e);
// }, false);
// $(document).ajaxComplete(function(event, xhr, options) {
// 	fun_alert('ajaxComplete, ' + event);
// });

// function fun_alert(txt) {
// 	alert(txt)
// }
// window.addEventListener('load', (event) => {
//   alert('page is fully loaded');
// });
