// document.getElementById("searchboxinput").onclick = function () {
// 	var result = document.getElementsByClassName("section-result");
// 	alert("ClassName 為 section-result 的物件共有"+result.length+"個");
// 	for(var i=0; i<result.length; i++) {
// 	   result[i].addEventListener("mouseover",function(e){});
// 	};
// };
/// 做出來了!!  在元素生成之前先幫它加上事件，等它生成後就能直接用了
var delay=500, setTimeoutConst; 
// mouseenter、mouseleave，在鼠標滑到該元素時，不會對其子元素也發生監聽
// mouseover、mouseout，   在鼠標滑到該元素時，會對其子元素也發生監聽
// mouseover滑鼠放在上面多久就觸發幾次、改用mouseenter
$('#pane').on('mouseenter', '.section-result', function(e){// 傳入function的第一個參數是event物件
  var data_index = this.getAttribute('data-result-index'); // this, 目前的元素
  var store_name = this.getAttribute('aria-label');
  // this.setAttribute('id', 'storeid_'+data_index);
  storeid = 'storeid_' + data_index;
  tag = '<h1><a id="' + storeid + '" href="#" title="" >風險評估表</a></h1>';
  if (document.getElementById(storeid) === null){
    storeinfo = test_fun(data_index, store_name); // API，從資料庫取得圖片URL
    var imgurl = 'https://i.imgur.com/MoqLWVl.png'; // 若資料庫沒此店家的圖片URL，預設顯示"無資料"圖片
    var parsedObj = JSON.parse(storeinfo); // 將JSON字串剖析為 JavaScript 物件
    if (parsedObj.img){ 
      imgurl = parsedObj.img; // 資料庫有資料才更新imgurl
    }   
    $(this).append(tag);
    $('#'+storeid).tooltip({ 
      content: '<img src="' + imgurl + '" />' 
    });
  };

  // mouseenter要等500ms後才執行裡面Function
  // 若在500ms內就將滑鼠移開，就會觸發mouseleave事件，直接將原本設的Timeout清除掉-->不會執行timeout設的function
  // 效果是"要將滑鼠停在框框內500ms才會觸發function，否則不會"
  setTimeoutConst = window.setTimeout(function(e){ 
       // alert("第" + data_index + '筆,' + store_name);   
     }, delay);   
});
$('#pane').on('mouseleave', '.section-result', function(e){// 傳入function的第一個參數是event物件
  clearTimeout(setTimeoutConst);
});


var url_route = 'https://database-api-tibame.herokuapp.com/' // route 沒有設定允許CROS，所以呼叫會錯誤
var url_api = 'https://database-api-tibame.herokuapp.com/api'
// var url_local = 'https://bd35a204.ngrok.io'
// var url_api_local = 'https://bd35a204.ngrok.io/api'

// 要如何以店家中文名稱當作Key找到資料?????
function test_fun(storeid, store_name) {
  var storeinfo;
  $.ajax({
    // $.ajax 方法預設是async:true 啟動非同步方法，就是不會等 $.ajax 執行完成才return ，
    // 而是一開始就直接return了，所以會return undefined。
      async: false, // 採用同步的方法來請求，需等請求得到回應後才return，將async設成false
      type: 'GET',
      url: url_api,
      data:"storeid=" + storeid,
      // dataType: "json", // 若不指定類型，回傳的會是一個string
      // crossDomain:true,
      success: function(msg) {
        storeinfo = msg;
        // s = "第" + storeid + '筆,' + store_name + '\n' + msg
        // alert(s);
        // alert(msg); // typeof msg是string
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log('get api error，Status：' + textStatus);  
        console.log(jqXHR.responseText);
        storeinfo = 'error';
      } 
  });
  return storeinfo;
}
function test_return_json(e){
  $.ajax({
    type: "GET",
    dataType: "json",  // 指定為json類型，回傳的會是一個json格式的object
    url: url_api,
    data:"storeid=2",
    // headers : {'Access-Control-Allow-Headers:':'*'}, // server要加，這裡不用加
    success: function(msg) {
      console.log('aa');
      console.log(msg); // object要獨立寫在console.log()裡，才會顯示object內容{id_store: 2, id_category: 1,…}
      // console.log('msg' + msg); // 若寫console.log(字串+object);--->會顯示'字串'[object Object]
      alert('return json：' + typeof msg);  // typeof msg是 object，若用alert，無法顯示object內容，會顯示[object Object]
      alert(msg);
    },
    error: function (jqXHR, textStatus, errorThrown) {
        console.log('get api error');  
        console.log(jqXHR.responseText);  
     },  
    complete: function(xhr, textStatus) {
        console.log('get api finished status：' + xhr.status.toString());
    }   
  })
}
function test_notallow_CROSS(e){
  $.ajax({
      type: 'GET',
      url: url_route,
      // dataType: "json", // 若不指定類型，回傳的會是一個string
      // crossDomain:true,
      success: function(msg) {
          alert('return string：' + msg);
      },
      error: function (jqXHR, textStatus, errorThrown) {
         console.log('get route error，Status：' + textStatus);  
         console.log(jqXHR.responseText);
      },  
      complete: function(xhr, textStatus) {
        console.log('get route finished status：' + xhr.status.toString());
      }     
  });
}
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
