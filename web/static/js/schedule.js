/**
* 针对修改不同版块，修改模态框的标题
*/
$(".editor").on("click", (e)=> {
    let $target = $(e.target);
    // let title = $target.siblings("legend").text();
    // $("#scheduleModal").text(title);
    let $card = $target.parent().parent().parent();
    let remind_date = $card.children(".card-title").text();
    let detail = $card.children(".schedule-detail").text();
    let id = $card.children(".card-title").attr("data-id");
    
    $("#schedule-id").val(id);
    $("#remind_date").val(remind_date);
    $("#content").val(detail);
    
    $("#scheduleModal").modal('show');

});


$("#new-schedule").click( (e) => { 
    clear_modal();
    $("#scheduleModal").modal('show');
});


function clear_modal(){
    $("#schedule-id").val(-1);
    $("#remind_date").val("");
    $("#content").val("");
}

/**
 * 在dom中移除某一card
 * @param {int} id 该日程的id
 */
function remove_card(id){
    let target = $(`.card-title[data-id=${id}]`).parent().parent();
    if(target.length){
        target.remove();
    }
}
