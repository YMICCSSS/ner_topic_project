// Saves options to chrome.storage
function save_options() {
  var ProgramDate = document.getElementById('ProgramDate').value;
  var ProgramSit = document.getElementById('ProgramSit').value;
  var tselect = document.getElementById('TicketNumber');
  var TicketNumber = tselect.options[tselect.selectedIndex].value;

  chrome.storage.local.set({
    'ProgramDate': ProgramDate,
    'TicketNumber': TicketNumber,
    'ProgramSit': ProgramSit,
  }, function() {
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(() => {
      status.textContent = '';
    }, 750);
  });
}
// Restores select box and checkbox state using the preferences stored in chrome.storage.
function restore_options() {
  chrome.storage.local.get(['ProgramDate','TicketNumber','ProgramSit'], items => {
    if (items) {
      document.getElementById('ProgramDate').value = items.ProgramDate;
      document.getElementById('ProgramSit').value = items.ProgramSit;
      document.getElementById('TicketNumber').selectedIndex = items.TicketNumber;
    }
  });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);
// $('#btn').on('click', function(){alert('测试')});
document.getElementById('save').addEventListener("mouseover",()=> {
  var picture = document.getElementById("pic")
  picture.src='https://cdn.iconscout.com/icon/premium/png-256-thumb/url-14-650251.png' 
  picture.style.display="block";//block, none
  // document.getElementById('pic').css("display","block");
});
document.getElementById('save').addEventListener("mouseout",()=> {
  // alert('mouseout');
  // document.getElementById('pic').css("display","none");
  document.getElementById("pic").style.display="none";
});

var url = 'https://database-api-tibame.herokuapp.com/api?storeid=2'
console.log('aaa');
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
       alert(jqXHR.responseText);  
   },  
  complete: function(xhr, textStatus) {
      console.log(xhr.status);
  }   
})

// $.ajax({url: url,
//   headers : {'Access-Control-Allow-Headers:':'*'}, 
//   success: function(result){
//     console.log('ccc');
//     console.log(result);
//     // $("#div1").html(result);
//   },
//   error: function (jqXHR, textStatus, errorThrown) {  
//        alert(jqXHR.responseText);  
//    },  
//   complete: function(xhr, textStatus) {
//       console.log(xhr.status);
//   }   
// })
