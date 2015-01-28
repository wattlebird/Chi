(function(){
    $(document).ready(function (){
        $(".userlink").each(function (i,itm){
            $.getJSON("http://api.bgm.tv/user/"+$(this).attr("data"), function (res){
                $(this).text(res.nickname);
            })
        });
        $(".userblock").each(function (i, itm){
            $.getJSON("http://api.bgm.tv/user/"+$(this).attr("data"),function (res) {
                $(this).children("img").attr("src", res.avatar.large);
            });
        });
        $("#candidate-switch").click(function (){
            $(this).hide()
        })
    });
})();