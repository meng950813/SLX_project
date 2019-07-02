/*
* 
*/
var NETWORKCONFIG = {
    "layout": 0, // 0: 力引导布局, 1: 圆布局
    "calculating": true,
    "node_size": 15,
    "special": false,
    "node_charge": -300,
    "link_strength": 0.5,
    "line_style": "0"
}


var container = d3.select("#container");

var brush_svg = container.append("g")
        .attr("class", "brush-svg")
        .style("display", "none");

var network_graph = d3.select("#network-graph");

var defs_layout = network_graph.append("defs");

var temp_layout = network_graph.append("g")
        .attr("class", "temp-layout");

var link_layout = network_graph.append("g")
        .attr("class", "link-layout");

var text_layout = network_graph.append("g")
        .attr("class", "text-layout");

var node_layout = network_graph.append("g")
        .attr("class", "node-layout");

// 颜色比例尺
var color = d3.scaleOrdinal(d3.schemeCategory10);

// 初始化配色条
var color_bar = d3.select("#color-bar");
for (var i = 0; i <= 1; i += 0.01) {
    color_bar.append("div")
        .attr("class", "color-item")
        .style("background-color", d3.interpolateSinebow(i));
}

/*
* 
*/

// 屏蔽右键菜单
document.oncontextmenu = function(ev) {
	ev.preventDefault();
}

// 圆内文字切分
function textBreaking(d3text, text) {
    var len = 0;
    try {
        len = text.length;
    } catch(error) {
        console.log("Warning: nodes缺少name标签！");
        return;
    }
    if (len <= 4) {
        d3text.append("tspan")
            .attr("x", 0)
            .attr("y", 2)
            .text(text);
    } else {
        var top_text = text.substring(0, 4);
        var mid_text = text.substring(4, 9);
        var bot_ext = text.substring(9, len);
        var top_y = -9;
        var mid_y = 2;
        var bot_y = 10;
        if (len < 10) {
            top_y += 5;
            mid_y += 5;
        } else {
            bot_ext = text.substring(9, 11) + "...";
        }

        d3text.text("");
        d3text.append("tspan")
            .attr("x", 0)
            .attr("y", top_y)
            .text(function () {
                return top_text;
            });
        d3text.append("tspan")
            .attr("x", 0)
            .attr("y", mid_y)
            .text(function () {
                return mid_text;
            });
        d3text.append("tspan")
            .attr("x", 0)
            .attr("y", bot_y)
            .text(function () {
                return bot_ext;
            });
    }
}

// 生成关系连线路径
function genLinkPath(link, line_style) {
    var path = null;
    var sx = link.source.x;
    var sy = link.source.y;
    var tx = link.target.x;
    var ty = link.target.y;
    var dx = (tx - sx) / 8;
    var dy = (ty - sy) / 8;
    var x1 = sx + dx;
    var y1 = sy + dy;
    var x2 = sx + dx * 2;
    var y2 = sy + dy * 2;
    var x3 = sx + dx * 3;
    var y3 = sy + dy * 3;
    var x4 = sx + dx * 4;
    var y4 = sy + dy * 4;
    var x7 = sx + dx * 7;
    var y6 = sy + dy * 6;
    if (line_style === "0") {
        path = "M" + sx + "," + sy + " L" + tx + "," + ty;
    }
    else if (line_style === "1") {
        path = "M " + sx + "," + sy + " C" + x1 + "," + y2 + " " + x2 + "," + y3 + " " + x4 + "," + y4 + " S" + x7 + "," + y6 + " " + tx + "," + ty;
    }
    else if (line_style === "2") {
        path = "M " + sx + "," + sy + " L" + x4 + "," + sy + " " + " L" + x4 + "," + ty + " L" + tx + "," + ty;
    }
    else if (line_style === "3") {
        path = "M " + sx + "," + sy + " L" + sx + "," + y4 + " " + " L" + tx + "," + y4 + " L" + tx + "," + ty;
    }
    return path;
}

// 获取文字位置
function getLineTextDx(link) {
    var sx = link.source.x;
    var sy = link.source.y;
    var tx = link.target.x;
    var ty = link.target.y;
    var distance = Math.sqrt(Math.pow(tx - sx, 2) + Math.pow(ty - sy, 2));
    var text_length = 0;
    try {
        var text_length = link.label.length;
    } catch(error) {
        console.log("Warning: links缺少label标签！");
    }
    
    var dx = (distance - 3 * text_length) / 2;
    return dx;
}



var data_test ={
        "nodes": [
                {"id": 0, "name": "孙晓丹", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": "杰青"},
                {"id": 1, "name": "蔡强", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 2, "name": "李恒德", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 3, "name": "邵洋", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 4, "name": "陈娜", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 5, "name": "章晓中", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 6, "name": "姚可夫", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 7, "name": "张华伟", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 8, "name": "陈祥", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 9, "name": "刘源", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 10, "name": "李言祥", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 11, "name": "郭志鹏", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 12, "name": "董洪标", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 13, "name": "黄正宏", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 14, "name": "盖国胜", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 15, "name": "齐龙浩", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 16, "name": "康飞宇", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 17, "name": "万春磊", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 18, "name": "龚江宏", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 19, "name": "谢志鹏", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "长江学者"},
                {"id": 20, "name": "张政军", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 21, "name": "潘伟", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 22, "name": "康进武", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": "杰青"},
                {"id": 23, "name": "巩前明", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": ""},
                {"id": 24, "name": "韩志强", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 0,
                "label": ""},
                {"id": 25, "name": "熊守美", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": ""},
                {"id": 26, "name": "柳百成", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": ""},
                {"id": 27, "name": "沈厚发", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 28, "name": "吕瑞涛", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 29, "name": "荆涛", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 30, "name": "刘剑波", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 31, "name": "赖文生", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 32, "name": "柳百新", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 33, "name": "沈洋", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 34, "name": "李明", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 35, "name": "林元华", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 36, "name": "南策文", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 37, "name": "王秀梅", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 3,
                "label": "杰青"},
                {"id": 38, "name": "李龙土", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "杰青"},
                {"id": 39, "name": "李敬锋", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 40, "name": "王轲", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 41, "name": "李亮亮", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 42, "name": "周济", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 43, "name": "王晓慧", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 44, "name": "褚祥诚", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 45, "name": "李文珍", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 46, "name": "李正操", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": "院士"},
                {"id": 47, "name": "林红", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "院士"},
                {"id": 48, "name": "马静", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "院士"},
                {"id": 49, "name": "唐子龙", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 50, "name": "凌云汉", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 51, "name": "徐贲", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 52, "name": "刘伟", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 53, "name": "韦进全", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 54, "name": "刘光华", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 55, "name": "许庆彦", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 56, "name": "韦丹", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 57, "name": "潘峰", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 58, "name": "吴晓东", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 59, "name": "翁端", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2,
                "label": "杰青"},
                {"id": 60, "name": "苗伟", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2, "label": ""},
                {"id": 61, "name": "宋成", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2, "label": ""},
                {"id": 62, "name": "曾飞", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 2, "label": ""},
                {"id": 63, "name": "曾照强", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": ""},
                {"id": 64, "name": "司文捷", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 1,
                "label": ""},
                {"id": 65, "name": "伍晖", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4, "label": ""},
                {"id": 66, "name": "冉锐", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4, "label": ""},
                {"id": 67, "name": "赵凌云", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4,
                "label": ""},
                {"id": 68, "name": "钟敏霖", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4,
                "label": ""},
                {"id": 69, "name": "汪长安", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4,
                "label": ""},
                {"id": 70, "name": "岳振星", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4,
                "label": "杰青"},
                {"id": 71, "name": "庄大明", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 4,
                "label": "杰青"},
                {"id": 72, "name": "朱宏伟", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": ""},
                {"id": 73, "name": "杨金龙", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": ""},
                {"id": 74, "name": "张文征", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": ""},
                {"id": 75, "name": "杨志刚", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": ""},
                {"id": 76, "name": "于荣", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5, "label": ""},
                {"id": 77, "name": "朱静", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5, "label": ""},
                {"id": 78, "name": "钟虓龑", "code": "0805", "school": "清华大学", "insititution": "材料学院", "class": 5,
                "label": ""}],

        "links": [
            {"source": 1, "target": 0, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 2, "target": 1, "paper": 0, "patent": 1, "project": 1, "weight": 2, "label": "同事"},
            {"source": 4, "target": 3, "paper": 0, "patent": 6, "project": 0, "weight": 6, "label": "同事"},
            {"source": 5, "target": 4, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 6, "target": 4, "paper": 1, "patent": 11, "project": 2, "weight": 14, "label": "同事"},
            {"source": 8, "target": 7, "paper": 0, "patent": 18, "project": 0, "weight": 18, "label": "同事"},
            {"source": 9, "target": 8, "paper": 1, "patent": 18, "project": 1, "weight": 20, "label": "同事"},
            {"source": 10, "target": 8, "paper": 4, "patent": 15, "project": 1, "weight": 20, "label": "同事"},
            {"source": 12, "target": 11, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 14, "target": 13, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 15, "target": 14, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 16, "target": 14, "paper": 0, "patent": 3, "project": 0, "weight": 3, "label": "师徒"},
            {"source": 18, "target": 17, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "师徒"},
            {"source": 19, "target": 18, "paper": 0, "patent": 0, "project": 2, "weight": 2, "label": "师徒"},
            {"source": 20, "target": 18, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 21, "target": 18, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 23, "target": 22, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "师徒"},
            {"source": 23, "target": 3, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 23, "target": 6, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 24, "target": 11, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "师徒"},
            {"source": 25, "target": 11, "paper": 5, "patent": 0, "project": 3, "weight": 8, "label": "师徒"},
            {"source": 26, "target": 24, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "师徒"},
            {"source": 25, "target": 24, "paper": 1, "patent": 0, "project": 1, "weight": 2, "label": "师徒"},
            {"source": 27, "target": 24, "paper": 1, "patent": 0, "project": 1, "weight": 2, "label": "师徒"},
            {"source": 13, "target": 0, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "师徒"},
            {"source": 28, "target": 13, "paper": 3, "patent": 14, "project": 1, "weight": 18, "label": "师徒"},
            {"source": 16, "target": 13, "paper": 6, "patent": 23, "project": 4, "weight": 33, "label": "师徒"},
            {"source": 29, "target": 26, "paper": 5, "patent": 0, "project": 3, "weight": 8, "label": "师徒"},
            {"source": 16, "target": 0, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 16, "target": 15, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "师徒"},
            {"source": 28, "target": 16, "paper": 3, "patent": 14, "project": 1, "weight": 18, "label": "师徒"},
            {"source": 27, "target": 22, "paper": 0, "patent": 2, "project": 1, "weight": 3, "label": "师徒"},
            {"source": 26, "target": 22, "paper": 1, "patent": 0, "project": 1, "weight": 2, "label": "师徒"},
            {"source": 25, "target": 22, "paper": 2, "patent": 0, "project": 1, "weight": 3, "label": "师徒"},
            {"source": 31, "target": 30, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "师徒"},
            {"source": 32, "target": 31, "paper": 1, "patent": 0, "project": 4, "weight": 5, "label": "师徒"},
            {"source": 34, "target": 33, "paper": 0, "patent": 6, "project": 0, "weight": 6, "label": "同事"},
            {"source": 35, "target": 34, "paper": 0, "patent": 7, "project": 0, "weight": 7, "label": "同事"},
            {"source": 36, "target": 34, "paper": 0, "patent": 7, "project": 1, "weight": 8, "label": "同事"},
            {"source": 32, "target": 2, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 37, "target": 2, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 2, "target": 0, "paper": 1, "patent": 0, "project": 2, "weight": 3, "label": "同事"},
            {"source": 39, "target": 38, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 39, "target": 36, "paper": 0, "patent": 0, "project": 4, "weight": 4, "label": "同事"},
            {"source": 40, "target": 39, "paper": 1, "patent": 0, "project": 4, "weight": 5, "label": "同事"},
            {"source": 41, "target": 3, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 42, "target": 38, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 38, "target": 36, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 43, "target": 38, "paper": 0, "patent": 14, "project": 1, "weight": 15, "label": "同事"},
            {"source": 44, "target": 38, "paper": 5, "patent": 0, "project": 1, "weight": 6, "label": "同事"},
            {"source": 45, "target": 26, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 10, "target": 7, "paper": 6, "patent": 15, "project": 2, "weight": 23, "label": "同事"},
            {"source": 10, "target": 9, "paper": 9, "patent": 19, "project": 2, "weight": 30, "label": "同事"},
            {"source": 46, "target": 32, "paper": 0, "patent": 0, "project": 2, "weight": 2, "label": "同事"},
            {"source": 46, "target": 20, "paper": 2, "patent": 0, "project": 2, "weight": 4, "label": "同事"},
            {"source": 47, "target": 21, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 48, "target": 35, "paper": 0, "patent": 6, "project": 0, "weight": 6, "label": "同事"},
            {"source": 36, "target": 35, "paper": 0, "patent": 35, "project": 9, "weight": 44, "label": "同事"},
            {"source": 49, "target": 35, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 35, "target": 33, "paper": 1, "patent": 26, "project": 1, "weight": 28, "label": "同事"},
            {"source": 50, "target": 20, "paper": 0, "patent": 3, "project": 0, "weight": 3, "label": "同事"},
            {"source": 52, "target": 51, "paper": 0, "patent": 2, "project": 1, "weight": 3, "label": "同事"},
            {"source": 52, "target": 19, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 53, "target": 52, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 52, "target": 48, "paper": 0, "patent": 4, "project": 0, "weight": 4, "label": "同事"},
            {"source": 9, "target": 7, "paper": 5, "patent": 24, "project": 1, "weight": 30, "label": "同事"},
            {"source": 54, "target": 51, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 32, "target": 30, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 27, "target": 26, "paper": 0, "patent": 3, "project": 0, "weight": 3, "label": "同事"},
            {"source": 55, "target": 26, "paper": 2, "patent": 0, "project": 3, "weight": 5, "label": "同事"},
            {"source": 26, "target": 25, "paper": 3, "patent": 0, "project": 2, "weight": 5, "label": "同事"},
            {"source": 32, "target": 20, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 56, "target": 32, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 57, "target": 32, "paper": 1, "patent": 0, "project": 2, "weight": 3, "label": "同事"},
            {"source": 28, "target": 0, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 48, "target": 33, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 48, "target": 40, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 48, "target": 36, "paper": 0, "patent": 7, "project": 4, "weight": 11, "label": "同事"},
            {"source": 58, "target": 48, "paper": 1, "patent": 0, "project": 1, "weight": 2, "label": "同事"},
            {"source": 59, "target": 48, "paper": 1, "patent": 0, "project": 1, "weight": 2, "label": "同事"},
            {"source": 60, "target": 20, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 61, "target": 57, "paper": 6, "patent": 32, "project": 2, "weight": 40, "label": "同事"},
            {"source": 62, "target": 57, "paper": 3, "patent": 63, "project": 2, "weight": 68, "label": "同事"},
            {"source": 63, "target": 21, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 64, "target": 21, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 59, "target": 21, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 21, "target": 15, "paper": 1, "patent": 11, "project": 6, "weight": 18, "label": "同事"},
            {"source": 21, "target": 17, "paper": 2, "patent": 1, "project": 1, "weight": 4, "label": "同事"},
            {"source": 65, "target": 21, "paper": 2, "patent": 0, "project": 1, "weight": 3, "label": "同事"},
            {"source": 21, "target": 20, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 64, "target": 15, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 63, "target": 15, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 66, "target": 59, "paper": 5, "patent": 20, "project": 1, "weight": 26, "label": "同事"},
            {"source": 66, "target": 58, "paper": 4, "patent": 20, "project": 2, "weight": 26, "label": "同事"},
            {"source": 5, "target": 3, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 6, "target": 3, "paper": 3, "patent": 14, "project": 2, "weight": 19, "label": "同事"},
            {"source": 36, "target": 33, "paper": 0, "patent": 34, "project": 0, "weight": 34, "label": "同事"},
            {"source": 51, "target": 33, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 27, "target": 25, "paper": 2, "patent": 0, "project": 0, "weight": 2, "label": "同事"},
            {"source": 64, "target": 63, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 64, "target": 19, "paper": 0, "patent": 0, "project": 2, "weight": 2, "label": "同事"},
            {"source": 62, "target": 61, "paper": 1, "patent": 16, "project": 0, "weight": 17, "label": "同事"},
            {"source": 37, "target": 0, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 67, "target": 0, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 59, "target": 0, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 58, "target": 0, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 49, "target": 20, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 69, "target": 68, "paper": 0, "patent": 1, "project": 0, "weight": 1, "label": "同事"},
            {"source": 69, "target": 36, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 51, "target": 40, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 43, "target": 36, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 70, "target": 43, "paper": 1, "patent": 0, "project": 0, "weight": 1, "label": "同事"},
            {"source": 43, "target": 42, "paper": 2, "patent": 0, "project": 0, "weight": 2, "label": "同事"},
            {"source": 71, "target": 53, "paper": 0, "patent": 3, "project": 0, "weight": 3, "label": "同事"},
            {"source": 72, "target": 53, "paper": 0, "patent": 15, "project": 0, "weight": 15, "label": "同事"},
            {"source": 59, "target": 58, "paper": 9, "patent": 29, "project": 2, "weight": 40, "label": "同事"},
            {"source": 73, "target": 19, "paper": 4, "patent": 0, "project": 1, "weight": 5, "label": "同事"},
            {"source": 55, "target": 25, "paper": 2, "patent": 0, "project": 0, "weight": 2, "label": "同事"},
            {"source": 74, "target": 51, "paper": 0, "patent": 0, "project": 2, "weight": 2, "label": "同事"},
            {"source": 75, "target": 74, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 6, "target": 5, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 76, "target": 36, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 77, "target": 76, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 70, "target": 36, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"},
            {"source": 70, "target": 42, "paper": 8, "patent": 0, "project": 0, "weight": 8, "label": "同事"},
            {"source": 36, "target": 20, "paper": 0, "patent": 0, "project": 1, "weight": 1, "label": "同事"},
            {"source": 78, "target": 77, "paper": 1, "patent": 2, "project": 3, "weight": 6, "label": "同事"},
            {"source": 42, "target": 36, "paper": 0, "patent": 0, "project": 4, "weight": 4, "label": "同事"},
            {"source": 72, "target": 71, "paper": 0, "patent": 2, "project": 0, "weight": 2, "label": "同事"},
            {"source": 44, "target": 36, "paper": 0, "patent": 0, "project": 3, "weight": 3, "label": "同事"}
        ]
}