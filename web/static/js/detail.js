$(".editor").on("click", (e)=> {
    let $target = $(e.target);
    let title = $target.siblings("legend").text();
    $("#modifiyInfoModalLabel").text("操作 " + title);
    $("#modifiyInfoModal").modal('show');
});